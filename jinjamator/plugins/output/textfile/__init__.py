import sys
import os
from jinjamator.tools.output_plugin_base import outputPluginBase
from pprint import pprint
import os
import json
import errno


class textfile(outputPluginBase):
    def addArguments(self):
        self._parent._parser.add_argument(
            "--textfile-file-prefix",
            dest="textfile_file_prefix",
            help="destination file name prefix [default: %(default)s]",
            default="",
        )
        self._parent._parser.add_argument(
            "--textfile-file-suffix",
            dest="textfile_file_suffix",
            help="destination file name suffix [default: %(default)s]",
            default="txt",
        )
        self._parent._parser.add_argument(
            "--textfile-output-directory",
            dest="textfile_output_directory",
            help="destination directory for generated files",
            default="/tmp",
        )

    def connect(self, **kwargs):
        pass

    def process(self, data, **kwargs):
        try:
            os.mkdir(
                self._parent.configuration.get("textfile_output_directory", "/tmp")
            )
        except OSError as exc:
            if exc.errno != errno.EEXIST:
                raise
            pass

        generated_filename = "{0}{1}.{2}".format(
            self._parent.configuration.get("textfile_file_prefix", ""),
            os.path.basename(kwargs["template_path"]),
            self._parent.configuration.get("textfile_file_suffix", "txt"),
        )
        generated_dest = os.path.join(
            self._parent.configuration.get("textfile_output_directory", "/tmp"),
            generated_filename,
        )
        dest = self._parent.configuration.get("textfile_output_path", generated_dest)

        with open(dest, "w") as fh:
            fh.write(data)
        self._log.info("sucessfully written file: {0}".format(dest))
