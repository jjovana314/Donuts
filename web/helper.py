from jsonschema import validate
from jsonschema.exceptions import ValidationError
from exceptions import InvalidSchemaError
from json import dumps, loads
import exception_messages as ex_m


def validate_schema(schema: dict, data: dict) -> None:
    data = dumps(data)
    try:
        validate(loads(data), schema)
    except ValidationError as ex:
        ex_str = str(ex)
        for message in ex_m.schema_errors:
            if message in ex_str:
                raise InvalidSchemaError(message, ex_m.INVALID_SCHEMA)


list_data = []


def data_getter(data: object):
    if isinstance(data, list):
        # iterate thru dictionaries
        for dictionary in data:
            data_getter(dictionary)
    # id, type, name, batter, topping
    id_current = data.get("id", None)
    type_current = data.get("type", None)
    name = data.get("name", None)
    batters = data.get("batters", None)
    topping = data.get("topping", None)

    if batters is not None:
        batter = batters["batter"]
        for value in batter:
            data_getter(value)
    if topping is not None:
        for value in topping:
            data_getter(value)

    list_data.append((id_current, type_current, name))


with open("data_db.txt", "w") as f:
    f.write(str(list_data))
