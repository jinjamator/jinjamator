import re


def uuid4(value):

    rxg = re.compile(
        r"^[0-9A-F]{8}-[0-9A-F]{4}-4[0-9A-F]{3}-[89AB][0-9A-F]{3}-[0-9A-F]{12}$"
    )
    if not rxg.match(value):
        raise ValueError(f"{value} is not a valid UUID V4 string")
    return value


# # Swagger documentation
uuid4.__schema__ = {
    "type": "string",
    "pattern": r"^[0-9A-F]{8}-[0-9A-F]{4}-4[0-9A-F]{3}-[89AB][0-9A-F]{3}-[0-9A-F]{12}$",
    "description": "UUID V4 string",
}


def task_data(value):
    return value


# task_data.__schema__ = {
#    "type": "object",
#    "additionalProperties": {"$ref": "#/definitions/cisco_nx-os_query"},
# }
