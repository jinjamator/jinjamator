cisco.aci
===============================================

.. toctree::
    :maxdepth: 1

    cisco.aci.apic.rst
    cisco.aci.test.rst


.. py:function:: cisco.aci.connect_apic(subscription_enabled=False, *, _requires=<function _get_missing_apic_connection_vars at 0x7fa5a72f90d0>):

    not documented yet

.. py:function:: cisco.aci.credentials_set():

    Check if jinjamator has all information set necessary to connect to APIC.

    :returns: True if all required APIC connection parameters are set, False if not.
    :rtype: boolean
    

.. py:function:: cisco.aci.dn_exists(dn, *, _requires=<function _get_missing_apic_connection_vars at 0x7fa5a72f90d0>):

    Checks if the dn exists. Logs API Error to error log. 

    :param dn: APIC dn-string
    :type dn: ``str``
    :returns: True if dn exists (or contains an error), false if not existing
    :rtype: ``bool``
    

.. py:function:: cisco.aci.dn_has_attribute(dn, key, value, *, _requires=<function _get_missing_apic_connection_vars at 0x7fa5a72f90d0>):

    not documented yet

.. py:function:: cisco.aci.get_access_aep_name_by_vlan_id(vlan_id, dn_filter='Access', *, _requires=<function _get_missing_apic_connection_vars at 0x7fa5a72f90d0>):

    not documented yet

.. py:function:: cisco.aci.get_all_configured_spine_uplinks(*, _requires=<function _get_missing_apic_connection_vars at 0x7fa5a72f90d0>):

    not documented yet

.. py:function:: cisco.aci.get_all_downlinks(model):

    Return all downlink ports from plugin internal switch database.

    :param model: Cisco Switch Model String
    :type model: string
    :returns: A list of all default downlink port numbers.
    :rtype: list
    

.. py:function:: cisco.aci.get_all_fabric_ports(*, _requires=<function _get_missing_apic_connection_vars at 0x7fa5a72f90d0>):

    not documented yet

.. py:function:: cisco.aci.get_all_lldp_neighbours(*, _requires=<function _get_missing_apic_connection_vars at 0x7fa5a72f90d0>):

    not documented yet

.. py:function:: cisco.aci.get_all_nodes(index_by='id', *, _requires=<function _get_missing_apic_connection_vars at 0x7fa5a72f90d0>):

    not documented yet

.. py:function:: cisco.aci.get_all_uplinks(model):

    not documented yet

.. py:function:: cisco.aci.get_all_vlans_from_pool(pool_name, *, _requires=<function _get_missing_apic_connection_vars at 0x7fa5a72f90d0>):

    not documented yet

.. py:function:: cisco.aci.get_convertible_uplinks(model, count, min_uplinks=2):

    not documented yet

.. py:function:: cisco.aci.get_dict_from_epg_dn(dn):

    not documented yet

.. py:function:: cisco.aci.get_dict_from_external_epg_dn(dn):

    not documented yet

.. py:function:: cisco.aci.get_dict_from_node_dn(dn):

    not documented yet

.. py:function:: cisco.aci.get_dict_from_vrf_dn(dn):

    not documented yet

.. py:function:: cisco.aci.get_endpoint_table(*, _requires=<function _get_missing_apic_connection_vars at 0x7fa5a72f90d0>):

    not documented yet

.. py:function:: cisco.aci.get_fex_types():

    not documented yet

.. py:function:: cisco.aci.get_leaf_types():

    not documented yet

.. py:function:: cisco.aci.get_next_free_vpc_domain_id(*, _requires=<function _get_missing_apic_connection_vars at 0x7fa5a72f90d0>):

    not documented yet

.. py:function:: cisco.aci.get_parent_dn_from_child_dn(dn):

    not documented yet

.. py:function:: cisco.aci.get_podid_by_switch_id(switch_id, *, _requires=<function _get_missing_apic_connection_vars at 0x7fa5a72f90d0>):

    Retrive the pod_id for a switch_id from APIC, if not possible ask user to enter pod_id

    :param switch_id: integer from 100 to 3999
    :type switch_id: ``int``
    :returns: pod_id
    :rtype: ``int``
    :raises ValueError: If the node with the specified apic_node_id is invalid.
    

.. py:function:: cisco.aci.get_role_by_model(model):

    not documented yet

.. py:function:: cisco.aci.get_spine_types():

    not documented yet

.. py:function:: cisco.aci.is_api_error(response):

    Check the API-Response for errors

    :param response: Dict of the request response ([imdata][0][....])
    :type response: ``dict``
    :returns: True if response contains an error, false if not
    :rtype: ``bool``
    

.. py:function:: cisco.aci.is_dn_in_use(dn, ignore_children=False, *, _requires=<function _get_missing_apic_connection_vars at 0x7fa5a72f90d0>):

    not documented yet

.. py:function:: cisco.aci.is_min_version(major, minor, patch_level=None, node_id=1):

    Checks if the APIC run a minimum version specified

    :param major: minimum APIC major version, eg.: 4 for ACI 4.x.x
    :type major: ``int``
    :param minor: minimum APIC major version, eg.: 2 for ACI x.2.x
    :type minor: ``int``
    :param patch_level: minimum APIC patchlevel . eg.: 4i for ACI x.x.(4i) or None if it should be ignored
    :type patch_level: ``str`` or ``None``
    :param node_id: APIC node id to query, defaults to 1
    :type node_id: ``int``, optional
    :return: True if the APIC run specified version or greater, False if not.
    :rtype: ``bool``

    :Examples:

        jinja2 tasklet:
        
            .. code-block:: jinja

                {% if aci_is_min_version(4, 2, None) %} {#check if APIC runs at least 4.2 version of code#}
                bla bla
                {% endif %}
        
        python tasklet:

            .. code-block:: python

                if aci_is_min_version(4, 2, None): //check if APIC runs at least 4.2 version of code
                    do_something_fancy()
                else:
                    do_other_things()
    
    
    

.. py:function:: cisco.aci.model_is_leaf(model):

    not documented yet

.. py:function:: cisco.aci.model_is_spine(model):

    not documented yet

.. py:function:: cisco.aci.parse_api_error(response):

    Parse the error-message from the API Response.
    Assumes, that a check if there is an error present was done beforehand.

    :param response: Dict of the request response ([imdata][0][....])
    :type response: ``dict``
    :returns: Parsed Error-Text
    :rtype: ``str``
    

.. py:function:: cisco.aci.query(query_url, timeout=60, *, _requires=<function _get_missing_apic_connection_vars at 0x7fa5a72f90d0>):

    [summary]

    :param query_url: URL for the query, eg. "/api/node/class/topology/pod-1/node-101/faultSummary.json". If the URL contains "subscription=yes as parameter", a websocket session will be opened automatically.
    :type query_url: ``str``
    :param timeout: Timeout waiting for an http response from the apic, defaults to 60
    :type timeout: int, optional
    :return: dictionary containing the response from the APIC
    :rtype: ``dict``
    

.. py:function:: cisco.aci.version(apic_node_id=1, *, _requires=<function _get_missing_apic_connection_vars at 0x7fa5a72f90d0>):

    Returns the firmware version of an APIC

    :param apic_node_id: Node id of the apic to query for the version from 1 to 10, defaults to 1
    :type apic_node_id: integer, optional
    :returns: Version information as returned from APIC e.g.: 4.2(1p)
    :rtype: string
    :raises ValueError: If the node with the specified apic_node_id cannot be found.

    

.. py:function:: cisco.aci.vlan_pool_contains_vlan(pool_name, vlan_id):

    not documented yet


