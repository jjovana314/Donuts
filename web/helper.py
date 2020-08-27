from jsonschema import validate
from jsonschema.exceptions import ValidationError
from exceptions import InvalidSchemaError
from json import dumps, loads
import exception_messages as ex_m

# TODO: add comments and doctrings
# TODO: try to get rid of hardcoded part


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
                if flag >= 10:
                    grouped.append(
                        ("00"+str(flag),
                         data_batter[j][0],
                         data_topping[i][0],
                         flag)
                    )
                # also don't forget to add flag to tuple
                # we need that for later in other functions
                else:
                    grouped.append(
                        ("000"+str(flag),
                         data_batter[j][0],
                         data_topping[i][0],
                         flag)
                    )
                flag = int(flag)

    return grouped


def generate_all_data(data: list) -> list:
    _generate_outter_data(data)

    batter_values = [dictionary["batters"] for dictionary in data]
    batters_type = _generate_batter_data(batter_values)

    topping_type = _generate_topping_data(data)

    data_grouped = _group_data_by_flag(batters_type, topping_type)

    merged_types = merge_data(data_types, data_grouped)
    merged_all = merge_data(data_names, merged_types)

    data_final = []
    for tuple_ in merged_all:
        tuple_2 = (tuple_[2], tuple_[1], tuple_[0], tuple_[3], tuple_[4])
        data_final.append(tuple_2)
    return data_final


def merge_data(outter_data: list, grouped_data: list) -> list:
    merged = []
    len_group = len(grouped_data[0])
    all_flags = [grouped_data[i][len_group-1] 
                 for i in range(len(grouped_data))]
    max_flag = max(all_flags)

    for i in range(len(grouped_data)):
        for j in range(1, max_flag+1):
            if grouped_data[i][len_group-1] == j:
                merged.append(
                    (outter_data[j-1],
                     grouped_data[i][0],
                     grouped_data[i][1],
                     grouped_data[i][2],
                     grouped_data[i][3])
                )
    return merged
    
