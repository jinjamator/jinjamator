from pdb import Pdb
import os
import io
from posixpath import split
import re
import sys
import cmd
import bdb
import dis
import code
import glob
import pprint
import signal
import inspect
import tokenize
import traceback
from linecache import cache, clearcache, lazycache
import logging


def updatecache(filename, module_globals=None):
    """Update a cache entry and return its list of lines.
    If something's wrong, print a message, discard the cache entry,
    and return an empty list."""
    if module_globals:
        if "jinjaTask" in module_globals:
            filename = module_globals["__file__"]
            lines = module_globals["__code__"].split("\n")
            task= module_globals["jinjaTask"]
            logging.critical(pprint.pformat(task._configuration))
            task.parent._celery.update_state(
                state="DEBUGGING",
                meta={
                    "status": f"debugging tasklet {filename}",
                    "configuration": {"root_task_path": "", "created_by_user_id": ""},
                    },
                )
            
            if lines and not lines[-1].endswith("\n"):
                lines[-1] += "\n"
            stat = os.stat(filename)
            size, mtime = stat.st_size, stat.st_mtime
            cache[filename] = size, mtime, lines, filename

            return lines

    if filename in cache:
        if len(cache[filename]) != 1:
            cache.pop(filename, None)
    if not filename or (filename.startswith("<") and filename.endswith(">")):
        return []

    fullname = filename
    try:
        stat = os.stat(fullname)
    except OSError:
        basename = filename

        # Realise a lazy loader based lookup if there is one
        # otherwise try to lookup right now.
        if lazycache(filename, module_globals):
            try:
                data = cache[filename][0]()
            except (ImportError, OSError):
                pass
            else:
                if data is None:
                    # No luck, the PEP302 loader cannot find the source
                    # for this module.
                    return []
                cache[filename] = (
                    len(data),
                    None,
                    [line + "\n" for line in data.splitlines()],
                    fullname,
                )
                return cache[filename][2]

        # Try looking through the module search path, which is only useful
        # when handling a relative filename.
        if os.path.isabs(filename):
            return []

        for dirname in sys.path:
            try:
                fullname = os.path.join(dirname, basename)
            except (TypeError, AttributeError):
                # Not sufficiently string-like to do anything useful with.
                continue
            try:
                stat = os.stat(fullname)
                break
            except OSError:
                pass
        else:
            return []
    try:
        with tokenize.open(fullname) as fp:
            lines = fp.readlines()
    except OSError:
        return []
    if lines and not lines[-1].endswith("\n"):
        lines[-1] += "\n"
    size, mtime = stat.st_size, stat.st_mtime
    cache[filename] = size, mtime, lines, fullname
    return lines


def getlines(filename, module_globals=None):
    """Get the lines for a Python source file from the cache.
    Update the cache if it doesn't contain an entry for this file already."""

    if filename in cache:
        entry = cache[filename]
        if len(entry) != 1:
            return cache[filename][2]

    try:
        return updatecache(filename, module_globals)
    except MemoryError:
        clearcache()
        return []


import linecache

linecache.updatecache = updatecache
linecache.getlines = getlines


def getsourcelines(obj):

    if inspect.isframe(obj) and obj.f_globals.get("jinjaTask"):
        return obj.f_globals["__code__"].split("\n"), 1
    else:
        lines, lineno = inspect.findsource(obj)
        if inspect.isframe(obj) and obj.f_globals is obj.f_locals:
            # must be a module frame: do not try to cut a block out of it
            return lines, 1
        elif inspect.ismodule(obj):
            return lines, 1
        return inspect.getblock(lines[lineno:]), lineno + 1


def lasti2lineno(code, lasti):
    linestarts = list(dis.findlinestarts(code))
    linestarts.reverse()
    for i, lineno in linestarts:
        if lasti >= i:
            return lineno
    return 0


class JinjamatorTaskPdb(Pdb):
    def do_list(self, arg):
        """l(ist) [first [,last] | .]

        List source code for the current file.  Without arguments,
        list 11 lines around the current line or continue the previous
        listing.  With . as argument, list 11 lines around the current
        line.  With one argument, list 11 lines starting at that line.
        With two arguments, list the given range; if the second
        argument is less than the first, it is a count.

        The current line in the current frame is indicated by "->".
        If an exception is being debugged, the line where the
        exception was originally raised or propagated is indicated by
        ">>", if it differs from the current line.
        """

        self.lastcmd = "list"
        last = None
        if arg and arg != ".":
            try:
                if "," in arg:
                    first, last = arg.split(",")
                    first = int(first.strip())
                    last = int(last.strip())
                    if last < first:
                        # assume it's a count
                        last = first + last
                else:
                    first = int(arg.strip())
                    first = max(1, first - 5)
            except ValueError:
                self.error("Error in argument: %r" % arg)
                return
        elif self.lineno is None or arg == ".":
            first = max(1, self.curframe.f_lineno - 5)
        else:
            first = self.lineno + 1
        if last is None:
            last = first + 10

        is_tasklet = False

        if self.curframe.f_globals.get("jinjaTask"):
            
            filename = self.curframe.f_globals["__file__"]
            is_tasklet = True
        else:
            filename = self.curframe.f_code.co_filename

        breaklist = self.get_file_breaks(filename)
        try:
            lines = getlines(filename, self.curframe.f_globals)
            self._print_lines(lines[first - 1 : last], first, breaklist, self.curframe)
            self.lineno = min(last, len(lines))
            if len(lines) < last:
                self.message("[EOF]")
        except KeyboardInterrupt:
            pass

    do_l = do_list

    def do_longlist(self, arg):
        """longlist | ll
        List the whole source code for the current function or frame.
        """
        if self.curframe.f_globals.get("jinjaTask"):
            filename = self.curframe.f_globals["__file__"]
        else:
            filename = self.curframe.f_code.co_filename
        breaklist = self.get_file_breaks(filename)
        try:
            lines, lineno = getsourcelines(self.curframe)
        except OSError as err:
            self.error(err)
            return
        self._print_lines(lines, lineno, breaklist, self.curframe)

    do_ll = do_longlist

    def do_break(self, arg, temporary=0):
        """b(reak) [ ([filename:]lineno | function) [, condition] ]
        Without argument, list all breaks.

        With a line number argument, set a break at this line in the
        current file.  With a function name, set a break at the first
        executable line of that function.  If a second argument is
        present, it is a string specifying an expression which must
        evaluate to true before the breakpoint is honored.

        The line number may be prefixed with a filename and a colon,
        to specify a breakpoint in another file (probably one that
        hasn't been loaded yet).  The file is searched for on
        sys.path; the .py suffix may be omitted.
        """
        
        if not arg:
            if self.breaks:  # There's at least one
                self.message("Num Type         Disp Enb   Where")
                for bp in bdb.Breakpoint.bpbynumber:
                    if bp:
                        self.message(bp.bpformat())
            return
        # parse arguments; comma has lowest precedence
        # and cannot occur in filename
        filename = None
        lineno = None
        cond = None
        comma = arg.find(",")
        if comma > 0:
            # parse stuff after comma: "condition"
            cond = arg[comma + 1 :].lstrip()
            arg = arg[:comma].rstrip()
        # parse stuff before comma: [filename:]lineno | function
        colon = arg.rfind(":")
        funcname = None
        if colon >= 0:
            filename = arg[:colon].rstrip()
            f = self.lookupmodule(filename)
            if not f:
                self.error("%r not found from sys.path" % filename)
                return
            else:
                filename = f
            arg = arg[colon + 1 :].lstrip()
            try:
                lineno = int(arg)
            except ValueError:
                self.error("Bad lineno: %s" % arg)
                return
        else:
            # no colon; can be lineno or function
            try:
                lineno = int(arg)
            except ValueError:
                try:
                    func = eval(arg, self.curframe.f_globals, self.curframe_locals)
                except:
                    func = arg
                try:
                    if hasattr(func, "__func__"):
                        func = func.__func__
                    code = func.__code__
                    # use co_name to identify the bkpt (function names
                    # could be aliased, but co_name is invariant)
                    funcname = code.co_name
                    lineno = code.co_firstlineno
                    filename = code.co_filename
                except:
                    # last thing to try
                    (ok, filename, ln) = self.lineinfo(arg)
                    if not ok:
                        self.error(
                            "The specified object %r is not a function "
                            "or was not found along sys.path." % arg
                        )
                        return
                    funcname = ok  # ok contains a function name
                    lineno = int(ln)
        if not filename:
            filename = self.defaultFile()

        # Check for reasonable breakpoint
        line = self.checkline(filename, lineno)
        if line:
            # now set the break point
            err = self.set_break(filename, line, temporary, cond, funcname)
            if err:
                self.error(err)
            else:
                bp = self.get_breaks(filename, line)[-1]
                self.message("Breakpoint %d at %s:%d" % (bp.number, bp.file, bp.line))

    do_b = do_break
    # To be overridden in derived debuggers
    def defaultFile(self):
        """Produce a reasonable default."""
        if self.curframe.f_globals.get("jinjaTask"):
            filename = self.curframe.f_globals["__file__"]
        else:
            filename = self.curframe.f_code.co_filename
        if filename == "<string>" and self.mainpyfile:
            filename = self.mainpyfile
        return filename

    def do_source(self, arg):
        """source expression
        Try to get source code for the given object and display it.
        """

        try:
            obj = self._getval(arg)
        except:
            return
        try:
            lines, lineno = getsourcelines(obj)
        except (OSError, TypeError) as err:
            self.error(err)
            return
        self._print_lines(lines, lineno)

    def checkline(self, filename, lineno):
        """Check whether specified line seems to be executable.

        Return `lineno` if it is, 0 if not (e.g. a docstring, comment, blank
        line or EOF). Warning: testing is not comprehensive.
        """
        # this method should be callable before starting debugging, so default
        # to "no globals" if there is no current frame

        globs = self.curframe.f_globals if hasattr(self, "curframe") else None
        line = linecache.getline(filename, lineno, globs)
        if not line:
            self.message("End of file")
            return 0
        line = line.strip()
        # Don't allow setting breakpoint at a blank line
        if not line or (line[0] == "#") or (line[:3] == '"""') or line[:3] == "'''":
            self.error("Blank or comment")
            return 0
        return lineno

    def canonic(self, filename):
        """Return canonical form of filename.

        For real filenames, the canonical form is a case-normalized (on
        case insensitive filesystems) absolute path.  'Filenames' with
        angle brackets, such as "<stdin>", generated in interactive
        mode, are returned unchanged.
        """
        if self.curframe:
            if self.curframe.f_globals.get("jinjaTask"):
                filename = self.curframe.f_globals["__file__"]

        if filename == "<" + filename[1:-1] + ">":
            return filename
        canonic = self.fncache.get(filename)
        if not canonic:
            canonic = os.path.abspath(filename)
            canonic = os.path.normcase(canonic)
            self.fncache[filename] = canonic
        return canonic


def set_trace(*, header=None):

    pdb = JinjamatorTaskPdb()
    if header is not None:
        pdb.message(header)
    pdb.set_trace(sys._getframe().f_back)
