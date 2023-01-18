import os
import yaml
import re

environ = os.environ

server_id_rgx = re.compile(
    f"JINJAMATOR_AAA_{provider_name.upper()}_SERVER" + r"(\d+)_(.*)"
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
    f"JINJAMATOR_AAA_{provider_name.upper()}_GROUP_ATTR", provider_name.upper()
)
cfg["ldap_configuration"]["username_attr"] = environ.get(
    f"JINJAMATOR_AAA_{provider_name.upper()}_USERNAME_ATTR", provider_name.upper()
)
cfg["ldap_configuration"]["domain"] = environ.get(
    f"JINJAMATOR_AAA_{provider_name.upper()}_DOMAIN", provider_name.upper()
)
cfg["ldap_configuration"]["user_base_dn"] = environ.get(
    f"JINJAMATOR_AAA_{provider_name.upper()}_USER_BASE_DN", provider_name.upper()
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

for env_var in sorted(
    [
        e
        for e in environ
        if e.startswith(f"JINJAMATOR_AAA_{provider_name.upper()}_ALLOWED_GROUP")
    ]
):
    cfg["ldap_configuration"]["allowed_groups"].append(environ.get(env_var))


return yaml.dump(cfg)
