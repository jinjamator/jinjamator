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


def save(data, path):
    if isinstance(data, list):
        if isinstance(data[0], dict):
            with open(path, "w") as f:
                writer = csv.DictWriter(f, fieldnames=data[0].keys(), dialect=csv.excel)
                writer.writeheader()
                writer.writerows(data)
                log.debug(f"successfully written {len(data)} lines of data to {path}")
            return True
        raise ValueError(f"csv save not implemented for list of {type(data[0])}")
    raise ValueError(f"csv save not implemented for {type(data)}")
