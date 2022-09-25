base64
===============================================

.. toctree::
    :maxdepth: 1



.. py:function:: base64.decode(data):

    base64 decode helper for jinja

    :param data: base64 encodeable bytes-object
    :type model: byte
    :returns: decodeed bytes-object
    :rtype: byte
    

.. py:function:: base64.decodes(data, code='ascii'):

    base64 decode helper for jinja taking string and returning string

    :param data: base64-encoded string which should be decoded
    :type model: string
    :param code: code to use for bytes en-/decoding (default: ascii)
    :type model: string
    :returns: decoded string
    :rtype: string
    

.. py:function:: base64.encode(data):

    base64 encode helper for jinja

    :param data: encodeable bytes-object
    :type model: byte
    :returns: base64 encoded bytes-object
    :rtype: byte
    

.. py:function:: base64.encodes(data, code='ascii'):

    base64 encode helper for jinja taking string and returning string

    :param data: string which should be encoded
    :type model: string
    :param code: code to use for bytes en-/decoding (default: ascii)
    :type model: string
    :returns: base64-encoded string
    :rtype: string
    


