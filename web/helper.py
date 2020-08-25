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
all_keys = ["id", "type", "name", "batters", "topping"]


def generate_data(data: object):
    if isinstance(data, list):
        # iterate thru dictionaries
        for dictionary in data:
            generate_data(dictionary)
    [id_current, type_current, name, batters, topping] = _geters(data)
    # id, type, name, batter, topping
    # id_current = data.get("id", None)
    # type_current = data.get("type", None)
    # name = data.get("name", None)

    # batters = data.get("batters", None)
    # topping = data.get("topping", None)

    if batters is not None:
        batter = batters["batter"]
        for value in batter:
            generate_data(value)
    if topping is not None:
        for value in topping:
            generate_data(value)

    list_data.append((id_current, type_current, name))


def _geters(data: dict) -> list:
    return [data.get(key, None) for key in all_keys]
    # for key in keys:
    #     list_return.append(data.get(key, None))

with open("data_db.txt", "w") as f:
    f.write(str(list_data))
