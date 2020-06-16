def get(tenant, filter_name):
    """
    Get the specified filter in tenant

    :param tenant: String containing the tenant-name
    :param filter_name: String containing the filter-name
    :returns: dict with the response
    """
    return cisco.aci.query(f"/api/node/mo/uni/tn-{tenant}/flt-{filter_name}.json")
