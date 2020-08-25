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


data_ids = []
data_types = []
data_names = []


def _generate_outter_data(data: object) -> None:
    if isinstance(data, dict):
        data_ids.append(data["id"])
        data_types.append(data["type"])
        data_names.append(data["name"])

    if isinstance(data, list):
        for dictionary in data:
            _generate_outter_data(dictionary)


def _generate_batter_data(data: list) -> list:
    values = []
    for dictionary in data:
        batter_inner = dictionary["batter"]
        for inner_dict in batter_inner:
            values.append(inner_dict["type"])
    pprint(values)
    return values


def _generate_topping_data(data: list) -> list:
    topping_data = []
    topping_data.append(data["type"])
    return topping_data


def generate_all_data(data):
    _generate_outter_data(data)

    batter_values = [dictionary["batters"] for dictionary in data]
    batters = _generate_batter_data(batter_values)

    topping_list = []
    for dictionary in data:
        topping = dictionary.get("topping", None)
        pprint(topping)
        if topping is not None:
            # topping is list with dicitonaries
            for dict_top in topping:
                topping_list.append(*_generate_topping_data(dict_top))
