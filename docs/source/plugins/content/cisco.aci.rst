cisco.aci
===============================================

.. toctree::
    :maxdepth: 1

    cisco.aci.apic.rst
    cisco.aci.test.rst


.. py:function:: cisco.aci.connect_apic(subscription_enabled=False):

        not documented yet

.. py:function:: cisco.aci.credentials_set():

        Check if jinjamator has all information set necessary to connect to APIC.

    :returns: True if all required APIC connection parameters are set, False if not.
    :rtype: boolean
    

.. py:function:: cisco.aci.dn_exists(dn):

        Checks if the dn exists. Also returns true when there was an API-Error. Writes the error to error-out

    :param dn: dn-string
    :type dn: string
    :returns: True if dn exists (or contains an error), false if not existing
    :rtype: boolean
    

.. py:function:: cisco.aci.dn_has_attribute(dn, key, value):

        not documented yet

.. py:function:: cisco.aci.get_access_aep_name_by_vlan_id(vlan_id, dn_filter='Access'):

        not documented yet

.. py:function:: cisco.aci.get_all_configured_spine_uplinks():

        not documented yet

.. py:function:: cisco.aci.get_all_downlinks(model):

        Return all downlink ports from plugin internal switch database.

    :param model: Cisco Switch Model String
    :type model: string
    :returns: A list of all default downlink port numbers.
    :rtype: list
    

.. py:function:: cisco.aci.get_all_fabric_ports():

        not documented yet

.. py:function:: cisco.aci.get_all_lldp_neighbours():

        not documented yet

.. py:function:: cisco.aci.get_all_nodes(index_by='id'):

        not documented yet

.. py:function:: cisco.aci.get_all_uplinks(model):

        not documented yet

.. py:function:: cisco.aci.get_all_vlans_from_pool(pool_name):

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

.. py:function:: cisco.aci.get_endpoint_table():

        not documented yet

.. py:function:: cisco.aci.get_fex_types():

        not documented yet

.. py:function:: cisco.aci.get_leaf_types():

        not documented yet

.. py:function:: cisco.aci.get_next_free_vpc_domain_id():

        not documented yet

.. py:function:: cisco.aci.get_parent_dn_from_child_dn(dn):

        not documented yet

.. py:function:: cisco.aci.get_podid_by_switch_id(switch_id):

        Retrive the pod_id for a switch_id from APIC, if not possible ask user to enter pod_id

    :param switch_id: integer from 100 to 3999
    :type switch_id: integer
    :returns: pod_id
    :rtype: integer
    

.. py:function:: cisco.aci.get_role_by_model(model):

        not documented yet

.. py:function:: cisco.aci.get_spine_types():

        not documented yet

.. py:function:: cisco.aci.is_api_error(response):

        Check the API-Response for errors

    :param response: Dict of the request response ([imdata][0][....])
    :type response: dict
    :returns: True if response contains an error, false if not
    :rtype: boolean
    

.. py:function:: cisco.aci.is_dn_in_use(dn, ignore_children=False):

        not documented yet

.. py:function:: cisco.aci.is_min_version(major, minor, patch_level, node_id=1):

        {% if aci_is_min_version(4, 0, None) %}
    {% endif %}
    

.. py:function:: cisco.aci.model_is_leaf(model):

        not documented yet

.. py:function:: cisco.aci.model_is_spine(model):

        not documented yet

.. py:function:: cisco.aci.parse_api_error(response):

        Parse the error-message from the API Response.
    Assumes, that a check if there is an error present was done beforehand.

    :param response: Dict of the request response ([imdata][0][....])
    :type response: dict
    :returns: Parsed Error-Text
    :rtype: string
    

.. py:function:: cisco.aci.query(queryURL, timeout=60):

        not documented yet

.. py:function:: cisco.aci.version(apic_node_id=1):

        Returns the firmware version of an APIC

    :param apic_node_id: Node id of the apic to query for the version from 1 to 10, defaults to 1
    :type apic_node_id: integer, optional
    :returns: Version information as returned from APIC e.g.: 4.2(1p)
    :rtype: string
    :raises ValueError: If the node with the specified apic_node_id cannot be found.

    

.. py:function:: cisco.aci.vlan_pool_contains_vlan(pool_name, vlan_id):

        not documented yet


