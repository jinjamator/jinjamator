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

l = logging.getLogger("")


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
