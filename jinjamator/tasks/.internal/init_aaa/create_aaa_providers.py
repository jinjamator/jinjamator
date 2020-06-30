import os
import re

env_rgx = re.compile(r"JINJAMATOR_AAA_([A-Z|0-9]+)_TYPE")

for v in task.run(
    "create_local_provider", {"provider_name": "local"}, output_plugin="null"
):
    file.save(v["result"], os.path.expanduser("~/.jinjamator/aaa/99_local.yaml"))

for k, v in os.environ.items():
    result = env_rgx.match(k)
    if result:
        self.configuration["provider_name"] = provider_name = result.group(1).lower()
        if v.lower() == "oidc":
            for res in task.run(
                "create_oidc_provider", self.configuration, output_plugin="null"
            ):
                provider_priority = os.environ.get(
                    f"JINJAMATOR_AAA_{provider_name.upper()}_PRIORITY", "01"
                )
                file.save(
                    res["result"],
                    os.path.expanduser(
                        f"~/.jinjamator/aaa/{provider_priority}_{provider_name.lower()}.yaml"
                    ),
                )
