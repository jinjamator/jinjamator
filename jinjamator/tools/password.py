redacted_passwords = []


def redact(obj, is_password=False):
    if isinstance(obj, str):
        if is_password:
            if obj not in redacted_passwords:
                redacted_passwords.append(obj)
            obj = "__redacted__"
        return redacted_passwords, obj
    elif isinstance(obj, list):
        for index, item in enumerate(obj):
            obj[index] = redact(item)[1]
        return redacted_passwords, obj
    elif isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(k, str) and (
                ("pass" in k and isinstance(v, str))
                or (k.endswith("_key") and isinstance(v, str))
                or ("secret" in k and isinstance(v, str))
            ):
                obj[k] = redact(v, True)[1]
            else:
                obj[k] = redact(v)[1]
        return redacted_passwords, obj
    return redacted_passwords, obj
