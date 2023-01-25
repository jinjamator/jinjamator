import os
import yaml
import re

environ = os.environ

server_id_rgx = re.compile(
    f"JINJAMATOR_AAA_{provider_name.upper()}_SERVER" + r"(\d+)_(.*)"
)
allowed_group_id_rgx = re.compile(
    f"JINJAMATOR_AAA_{provider_name.upper()}_ALLOWED_GROUP" + r"(\d+)"
)


cfg = {
    "type": "ldap",
    "name": provider_name,
    "display_name": environ.get(
        f"JINJAMATOR_AAA_{provider_name.upper()}_DISPLAY_NAME", provider_name.upper()
    ),
    "ldap_configuration": {"allowed_groups": []},
}
cfg["display_name"] = environ.get(
    f"JINJAMATOR_AAA_{provider_name.upper()}_DISPLAY_NAME", provider_name.upper()
)
cfg["ldap_configuration"]["group_attr"] = environ.get(
    f"JINJAMATOR_AAA_{provider_name.upper()}_GROUP_ATTR", "<not configured>"
)
cfg["ldap_configuration"]["username_attr"] = environ.get(
    f"JINJAMATOR_AAA_{provider_name.upper()}_USERNAME_ATTR", "<not configured>"
)
cfg["ldap_configuration"]["domain"] = environ.get(
    f"JINJAMATOR_AAA_{provider_name.upper()}_DOMAIN", "<not configured>"
)
cfg["ldap_configuration"]["user_base_dn"] = environ.get(
    f"JINJAMATOR_AAA_{provider_name.upper()}_USER_BASE_DN", ""
)
cfg["ldap_configuration"]["resolve_groups_recursive"] = environ.get(
    f"JINJAMATOR_AAA_{provider_name.upper()}_RESOLVE_GROUPS_RECURSIVE", True
)
cfg["ldap_configuration"]["maximum_group_recursion"] = int(
    environ.get(f"JINJAMATOR_AAA_{provider_name.upper()}_MAXIMUM_GROUP_RECURSION"), 5
)


cfg["ldap_configuration"]["servers"] = []
for env_var in sorted(
    [
        e
        for e in environ
        if e.startswith(f"JINJAMATOR_AAA_{provider_name.upper()}_SERVER")
    ]
):
    server_id, var_name = server_id_rgx.match(env_var).groups()
    idx = int(server_id) - 1
    var_name = var_name.lower()
    try:
        cfg["ldap_configuration"]["servers"][idx]
    except IndexError:
        cfg["ldap_configuration"]["servers"].append({})
    try:
        cfg["ldap_configuration"]["servers"][idx][var_name] = int(environ.get(env_var))
    except:
        if environ.get(env_var).lower() in ["true", "yes"]:
            cfg["ldap_configuration"]["servers"][idx][var_name] = bool(
                environ.get(env_var)
            )
        else:
            cfg["ldap_configuration"]["servers"][idx][var_name] = str(
                environ.get(env_var)
            )


for env_var in environ:
    res = allowed_group_id_rgx.match(env_var)
    ad_group = environ.get(env_var)
    if res:
        cfg["ldap_configuration"]["allowed_groups"].append(ad_group)
        try:
            for group in environ.get(f"{env_var}_MAP").split(","):
                if "map_groups" not in cfg["ldap_configuration"]:
                    cfg["ldap_configuration"]["map_groups"] = {}
                if ad_group not in cfg["ldap_configuration"]["map_groups"]:
                    cfg["ldap_configuration"]["map_groups"][ad_group] = []
                cfg["ldap_configuration"]["map_groups"][ad_group].append(group)
        except AttributeError:
            pass


return yaml.dump(cfg)
