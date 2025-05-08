# Copyright 2019 Wilhelm Putz

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import os
from html.parser import HTMLParser

l = logging.getLogger("")

class HTMLTagRemover(HTMLParser):
    def __init__(self):
        super().__init__()
        self.result = []

    def handle_data(self, data):
        if self.lasttag not in ["script"]:
            self.result.append(data)

    def get_text(self):
        return ''.join(self.result)



def info(message):
    """Log helper function for jinja2 tasks"""
    l.info(message)
    return ""


def warn(message):
    """Log helper function for jinja2 tasks"""
    l.warning(message)
    return ""


def warning(message):
    """Log helper function for jinja2 tasks"""
    l.warning(message)
    return ""


def error(message):
    """Log helper function for jinja2 tasks"""
    l.error(message)
    return ""


def debug(message):
    """Log helper function for jinja2 tasks"""
    l.debug(message)
    return ""


def console(message):
    print(message)
    l.debug(f"console log: {message}")



def summary(message, **kwargs):
    filename=kwargs.get("create_file")
    
    if isinstance(filename,bool):
        if filename:
            filename="results_summary.txt"
    if filename:
        textfile_output_directory = os.path.join(_jinjamator._configuration.get("jinjamator_user_directory"),"logs", _jinjamator._configuration.get("jinjamator_job_id"),"files")
        log.debug(f"saving summary to {textfile_output_directory}")
        os.makedirs(textfile_output_directory, exist_ok=True)
        if not kwargs.get("keep_tags"):
            remover = HTMLTagRemover()
            remover.feed(message)
            txt_msg=remover.get_text()
        else:
            txt_msg=message
        file.save(txt_msg, f"{textfile_output_directory}{os.path.sep}{filename}")

    l.summary(message)
