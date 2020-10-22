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
import csv


def save(data, destination_path, **kwargs):
    """Generate a csv file from a datastructure.

    :param data: Currently data must be a list of dicts.
    :type data: list of dict
    :param destination_path: Path of the resulting CSV file.
    :type destination_path: str
    :raises ValueError: If the format of data cannot be determined.
    :return: Returns True on success.
    :rtype: bool

    :Keyword Arguments:
        Currently None
    """
    if isinstance(data, list):
        if isinstance(data[0], dict):
            with open(destination_path, "w") as f:
                writer = csv.DictWriter(f, fieldnames=data[0].keys(), dialect=csv.excel)
                writer.writeheader()
                writer.writerows(data)
                log.debug(
                    f"successfully written {len(data)} lines of data to {destination_path}"
                )
            return True
        raise ValueError(f"csv save not implemented for list of {type(data[0])}")
    raise ValueError(f"csv save not implemented for {type(data)}")


def load(source_path, **kwargs):
    """Load data from a CSV file

    :param source_path: URL or local path
    :type source_path: ``str``

    :Keyword Arguments:
        Currently None
    """
    retval = []
    log.debug(f"trying to import file {source_path}")
    with file.open(source_path, "r") as f:
        for row in csv.DictReader(f):
            retval.append(row)
    return retval
