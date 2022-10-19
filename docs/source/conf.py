# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys

sys.path.insert(0, os.path.abspath("../../"))
import sphinx_rtd_theme


def setup(app):
    from jinjamator.plugin_loader.content import (
        ContentPluginLoader,
        #        global_ldr,
        #        init_loader,
        contentPlugin,
    )
    from pprint import pprint

    # globals()["global_ldr"] = init_loader(app)
    # globals()["global_ldr"].load(
    #    "/home/putzw/git/jinjamator/jinjamator/plugins/content"
    # )
    import importlib
    import traceback
    import warnings
    from typing import Any, Callable, Dict, List, Mapping, NamedTuple, Optional, Tuple

    from sphinx.deprecation import RemovedInSphinx40Warning, deprecated_alias
    from sphinx.pycode import ModuleAnalyzer
    from sphinx.util import logging
    from sphinx.util.inspect import isclass, isenumclass, safe_getattr

    logger = logging.getLogger(__name__)
    import sphinx.ext.autodoc
    from sphinx.ext.autodoc.importer import import_module, mangle, unmangle

    def import_object_new(
        modname: str,
        objpath: List[str],
        objtype: str = "",
        attrgetter: Callable[[Any, str], Any] = safe_getattr,
        warningiserror: bool = False,
    ) -> Any:

        import imp
        import types

        print(
            "----------------------------------------hack---------------------------------"
        )
        # print(f'modname: {modname} objpath: {objpath}')
        # module = imp.new_module(modname)
        #        global_ldr = globals()["global_ldr"]

        class_path = modname.split(".")
        base_obj_name = class_path.pop(0)
        base_obj = global_ldr.get_functions()[base_obj_name]
        # print(global_ldr.get_functions())

        module = imp.new_module(base_obj_name)
        # sys.modules[base_obj_name] = module
        # for path in class_path:
        #     cur = getattr(base_obj,item)

        parent = base_obj
        #     base_obj=getattr(base_obj,path)

        for item in dir(base_obj):
            cur = getattr(base_obj, item)
            if isinstance(cur, contentPlugin):
                setattr(module, item, cur)

                print(f"register {base_obj_name}.{item}")

        return [module, None, modname, module]
        # parent=None
        # for path in class_path:
        #     parent=base_obj
        #     base_obj=getattr(base_obj,path)

        # pprint(dir(base_obj))

        #         func = getattr(module, func_name)
        #         if isinstance(func, types.FunctionType):

        if objpath:
            logger.debug("[autodoc] from %s import %s", modname, ".".join(objpath))
        else:
            logger.debug("[autodoc] import %s", modname)

        try:
            # module = None
            exc_on_importing = None
            objpath = list(objpath)
            while module is None:
                try:
                    module = import_module(modname, warningiserror=warningiserror)
                    logger.debug("[autodoc] import %s => %r", modname, module)
                except ImportError as exc:
                    logger.debug("[autodoc] import %s => failed", modname)
                    exc_on_importing = exc
                    if "." in modname:
                        # retry with parent module
                        modname, name = modname.rsplit(".", 1)
                        objpath.insert(0, name)
                    else:
                        raise

            obj = module
            parent = None
            object_name = None
            for attrname in objpath:
                parent = obj
                logger.debug("[autodoc] getattr(_, %r)", attrname)
                mangled_name = mangle(obj, attrname)
                obj = attrgetter(obj, mangled_name)
                logger.debug("[autodoc] => %r", obj)
                object_name = attrname
                print([module, parent, object_name, obj])
            return [module, parent, object_name, obj]
        except (AttributeError, ImportError) as exc:
            if isinstance(exc, AttributeError) and exc_on_importing:
                # restore ImportError
                exc = exc_on_importing

            if objpath:
                errmsg = "autodoc: failed to import %s %r from module %r" % (
                    objtype,
                    ".".join(objpath),
                    modname,
                )
            else:
                errmsg = "autodoc: failed to import %s %r" % (objtype, modname)

            if isinstance(exc, ImportError):
                # import_module() raises ImportError having real exception obj and
                # traceback
                real_exc, traceback_msg = exc.args
                if isinstance(real_exc, SystemExit):
                    errmsg += (
                        "; the module executes module level statement "
                        "and it might call sys.exit()."
                    )
                elif isinstance(real_exc, ImportError) and real_exc.args:
                    errmsg += (
                        "; the following exception was raised:\n%s" % real_exc.args[0]
                    )
                else:
                    errmsg += (
                        "; the following exception was raised:\n%s" % traceback_msg
                    )
            else:
                errmsg += (
                    "; the following exception was raised:\n%s" % traceback.format_exc()
                )

            logger.debug(errmsg)
            raise ImportError(errmsg) from exc

    # translator = docxbuilder.DocxBuilder.default_translator_class
    # setattr(translator, 'visit_mermaid', docx_visit_mermaid)

    # setattr(sphinx.ext.autodoc, 'import_object', import_object_new)

    # pprint(global_ldr.get_functions()['file'].excel.to_csv.__doc__)

    # # Define the docx visit method for mermaid node generated by sphinxcontrib.mermaid
    # # https://pypi.org/project/sphinxcontrib-mermaid/
    # def docx_visit_mermaid(self, node):
    #     def get_filepath(self, node):
    #         from sphinxcontrib import mermaid
    #         _, filepath = mermaid.render_mm(self, node['code'], node['options'],'png')
    #         return filepath
    #     alt=""
    #     if 'alt' in node.attributes:
    #         alt=node['alt']
    #     # Docxbuilder provides useful methods. See Docxbuilder API reference.
    #     self.visit_image_node(node, alt, get_filepath)
    # # Add the visit method to Docxbuilder
    # import docxbuilder
    # translator = docxbuilder.DocxBuilder.default_translator_class
    # setattr(translator, 'visit_mermaid', docx_visit_mermaid)


# -- Project information -----------------------------------------------------

project = "jinjamator"
copyright = "2020, Wilhelm Putz"
author = "Wilhelm Putz"

# The full version, including alpha/beta/rc tags
release = "0.9.13"

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ["sphinx.ext.autodoc", "sphinx.ext.napoleon"]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#

html_theme = "sphinx_rtd_theme"
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]
