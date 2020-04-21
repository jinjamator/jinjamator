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
