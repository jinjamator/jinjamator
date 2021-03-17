# Copyright 2021 Philipp Berger

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

from base64 import b64encode as b64_encode, b64decode as b64_decode


def encode(data):
    """
    base64 encode helper for jinja

    :param data: encodeable bytes-object
    :type model: byte
    :returns: base64 encoded bytes-object
    :rtype: byte
    """
    return b64_encode(data)


def encodes(data, code="ascii"):
    """
    base64 encode helper for jinja taking string and returning string

    :param data: string which should be encoded
    :type model: string
    :param code: code to use for bytes en-/decoding (default: ascii)
    :type model: string
    :returns: base64-encoded string
    :rtype: string
    """
    return b64_encode(data.encode(code)).decode(code)


def decode(data):
    """
    base64 decode helper for jinja

    :param data: base64 encodeable bytes-object
    :type model: byte
    :returns: decodeed bytes-object
    :rtype: byte
    """
    return b64_decode(data)


def decodes(data, code="ascii"):
    """
    base64 decode helper for jinja taking string and returning string

    :param data: base64-encoded string which should be decoded
    :type model: string
    :param code: code to use for bytes en-/decoding (default: ascii)
    :type model: string
    :returns: decoded string
    :rtype: string
    """
    return b64_decode(data.encode(code)).decode(code)
