calc.dscp
===============================================

.. toctree::
    :maxdepth: 1



.. py:function:: calc.dscp.dec_to_name(dec):

    Converts the DSCP decimal value to it'S corresponding name

    :param name: Decimal DSCP value (i.e. 24)
    :type name: ``int``
    :return: DSCP name (i.e. CS3). Returns False if no mapping could be found
    :rtype: ``str`` | ``bool``
    

.. py:function:: calc.dscp.dscp_map():

    Internal function that returns a dict with valid DSCP names to thier decimal values

    :return: Dictionary containing the values (name => dec)
    :rtype: ``dict``
    

.. py:function:: calc.dscp.name_to_dec(name):

    Converts the DSCP name to it'S corresponding decimal value

    :param name: DSCP name (i.e. CS3)
    :type name: ``string``
    :return: Decimal DSCP value (i.e. 24). Returns False if no mapping could be found
    :rtype: ``int``
    


