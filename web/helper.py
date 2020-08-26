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


def _group_data_by_flag(data_batter: list, data_topping: list) -> list:
    grouped = []
    i = 0
    flag = 1
    for j in range(len(data_batter)):
        # if flags in data_batter are different then
        # we moved on to next dictionary
        if data_batter[j][1] != data_batter[j-1][1] and j > 0:
            flag += 1
        for i in range(len(data_topping)):        
            # if flags in data_batter and data_topping are
            # equal, then we want to group those types together
            if data_batter[j][1] == data_topping[i][1]:
                if flag > 10:
                    grouped.append(data_batter[j][0], data_topping[i][0], "00"+str(flag))
                # also don't forget to add flag to tuple
                # we need that for later in other functions
                else:
                    grouped.append((data_batter[j][0], data_topping[i][0], "000"+str(flag)))
                flag = int(flag)

    return grouped


def generate_all_data(data: list) -> tuple:
    _generate_outter_data(data)

    batter_values = [dictionary["batters"] for dictionary in data]
    batters_type = _generate_batter_data(batter_values)
    topping_type = _generate_topping_data(data)

    grouped_topping_batter = _group_data_by_flag(batters_type, topping_type)


def merge_data(list1: list, list2: list) -> list:
    # l_return = []
    # for tuple1 in list1:
    #     for tuple2 in list2:
    #         tuple_new = tuple1 + tuple2
    #         l_return.append(tuple_new)
    # return l_return
    
    
