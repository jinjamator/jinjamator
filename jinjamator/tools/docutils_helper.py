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

from docutils.core import publish_doctree
import docutils.nodes
import os
import logging

log = logging.getLogger()


def get_section_from_task_doc(task_path, section="description"):
    retval = None
    try:
        with open(os.path.join(task_path, "README.rst"), "r") as fh:
            s = fh.read()
    except:
        return None
    doctree = publish_doctree(s)
    doc_section = doctree.ids.get(section)

    if isinstance(doc_section, docutils.nodes.section):
        retval = doc_section.children[1].astext()
    return retval
