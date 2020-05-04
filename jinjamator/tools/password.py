def redact(obj, is_password=False):
    if isinstance(obj, str):
        if is_password:
            obj = "__redacted__"
        return obj
    elif isinstance(obj, list):
        for index, item in enumerate(obj):
            obj[index] = redact(item)
        return obj
    elif isinstance(obj, dict):
        for k, v in obj.items():
            if "pass" in k and isinstance(v, str):
                obj[k] = redact(v, True)
            else:
                obj[k] = redact(v)
        return obj
    return obj
