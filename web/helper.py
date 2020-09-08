from jsonschema import validate
from jsonschema.exceptions import ValidationError
from exceptions import InvalidSchemaError
from json import dumps, loads
import exception_messages as ex_m


# TODO: try to get rid of hardcoded part


def validate_schema(schema: dict, data: dict) -> None:
    """ Schemma validation.

    Args:
        schema (dict): valid dictionary
        data (dict): dictionary for validation

    Raises:
        InvalidSchemaError: if data (schema) is not valid
    """
    data = dumps(data)
    try:
        validate(loads(data), schema)
    except ValidationError as ex:
        ex_str = str(ex)
        for message in ex_m.schema_errors:
            if message in ex_str:
                raise InvalidSchemaError(message, ex_m.INVALID_SCHEMA)


# global lists with outter values
data_ids = []
data_types = []
data_names = []


def _generate_outter_data(data: object) -> None:
    """ Generate data from outter dictionaries.

    Args:
        data (object): dictionary or list with data
    """
    if isinstance(data, dict):
        data_ids.append(data["id"])
        data_types.append(data["type"])
        data_names.append(data["name"])

    if isinstance(data, list):
        for dictionary in data:
            # recursively call for dictionary
            _generate_outter_data(dictionary)


def _generate_batter_data(data: list) -> list:
    """ Generate data from dictionary with 'betters' key.

    Args:
        data (list): list with all batter dictionaries

    Returns:
        list with all batter types
    """
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
    """ Generate data from dictionary with 'topping' key

    Args:
        data (list): list with all topping dictionaries

    Returns:
        list with all topping types
    """
    topping_list = []
    for dictionary in data:
        topping = dictionary.get("topping", None)

        if topping is not None:
            # topping is list with dicitonaries
            for dict_top in topping:
                topping_list.append(dict_top["type"])
    return topping_list


def _group_data_by_flag(data_batter: list, data_topping: list) -> list:
    """ Grouping data by flags from batter and topping data.

    Args:
        data_batter (list): list with all batters data and flag
        data_topping (list): list with all toppings data and flag

    Returns:
        list with tuples that contains id, batter type, topping type and flag
    """
    grouped = []
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
                        ("00"+str(flag), data_batter[j][0], data_topping[i][0], flag)
                    )
                # also don't forget to add flag to tuple
                # we need that for later in other functions
                else:
                    grouped.append(
                        ("000"+str(flag), data_batter[j][0], data_topping[i][0], flag)
                    )
                # don't forget to convert flag back to int
                flag = int(flag)

    return grouped


def generate_all_data(data: list) -> list:
    """ Generate data that is sent from server.

    Args:
        data (list): data from server

    Returns:
        list with tuples that contains id, type, name, batters and toppings data
    """
    _generate_outter_data(data)

    batter_values = [dictionary["batters"] for dictionary in data]
    batters_type = _generate_batter_data(batter_values)
    topping_type = _generate_topping_data(data)

    data_grouped = _group_data_by_flag(batters_type, topping_type)

    merged_types = _merge_data(data_types, data_grouped)
    merged_all = _merge_data(data_names, merged_types)

    data_final = []
    # ! hardcoded
    for tuple_ in merged_all:
        tuple_2 = (tuple_[2], tuple_[1], tuple_[0], tuple_[3], tuple_[4])
        data_final.append(tuple_2)
    return data_final


call_counter = 0    # count how many times function is called


def _merge_data(outter_data: list, grouped_data: list) -> list:
    """ Merge outter and grouped data together.

    Args:
        outter_data (list): list with values from outter dictionaries
        grouped_data (list): list with all grouped values

    Returns:
        list with combined grouped and outter data
    """
    global call_counter
    call_counter += 1
    merged = []
    len_group = len(grouped_data[0])

    if call_counter == 1:
        all_flags = [grouped_data[i][len_group-1] for i in range(len(grouped_data))]
    else:
        # all_flags contains id converted to integer
        # * example: if id is '0003' then int('0003') is 3 
        all_flags = [int(tuple_[1]) for tuple_ in grouped_data]

    max_flag = max(all_flags)

    def _group_data():
        """ Group data from outter function. """
        nonlocal merged
        grouped_inner = [grouped_data[i][k] for k in range(max_flag+1)]
        merged.append((outter_data[j-1], *grouped_inner))

    for i in range(len(grouped_data)):
        for j in range(1, max_flag+1):
            # id_ can be id from grouped_data list
            # or flag if there is not id in grouped_data
            if call_counter == 1:
                id_ = grouped_data[i][len_group-1]
            else:
                id_ = int(grouped_data[i][1])
            if id_ == j:
                _group_data()
    
    return merged
