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
            # recursively call for dictionary
            _generate_outter_data(dictionary)


def _generate_batter_data(data: list) -> list:
    values = []
    flag = 0
    for dictionary in data:
        batter_inner = dictionary["batter"]
        flag += 1
        # batter_inner is list with dictionaries
        for inner_dict in batter_inner:
            values.append((inner_dict["type"], flag))

    return values


def _generate_topping_data(data: list) -> list:
    topping_list = []
    for dictionary in data:
        topping = dictionary.get("topping", None)

        if topping is not None:
            # topping is list with dicitonaries
            for dict_top in topping:
                topping_list.append(dict_top["type"])
    return topping_list


def generate_all_data(data: list) -> tuple:
    _generate_outter_data(data)

    batter_values = [dictionary["batters"] for dictionary in data]
    batters_type = _generate_batter_data(batter_values)
    topping_type = _generate_topping_data(data)

    # tuple_data = ()
    # list_tuples = []
    # for id_ in data_ids:
    #     for type_ in data_types:
    #         for name in data_names:
    #             for batter in batters_type:
    #                 for topping in topping_type:
    #                     tuple_data = (id_, type_, name, batter, topping)
    #                     list_tuples.append(tuple_data)
    # return list_tuples

def group_data_by_flag(data_batter: list, data_topping):
    grouped = []
    i = 0
    while i < len(data_batter) and j < len(data_topping):
        # check if flags are the same
        if data_batter[i][1] == data_topping[i][1]:
            grouped.append([data_batter, data_topping])
    return grouped
