from jsonschema import validate
from jsonschema.exceptions import ValidationError
from exceptions import InvalidSchemaError, InvalidValue
from json import dumps, loads
import exception_messages as ex_m


# TODO: try to get rid of hardcoded part
# ! repeated code in _generate_batter_data and _generate_topping_data functions


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
    flag = 0
    for dictionary in data:
        topping = dictionary.get("topping", None)

        if topping is not None:
            # topping is list with dictionaries
            flag += 1
            for dict_top in topping:
                topping_list.append((dict_top["type"], flag))
    return topping_list


grouped = []    # list of tuples with id, batter type, topping and flag


def _group_data_by_flag(data_batter: list, data_topping: list) -> None:
    """ Grouping data by flags from batter and topping data.

    Args:
        data_batter (list): list with all batters data and flag
        data_topping (list): list with all toppings data and flag
    """
    idx_topping = 0
    flag = 1
    for idx_batter in range(len(data_batter)):
        if _is_batter_flags_different(data_batter, idx_batter):
            # move on to the next dictionary
            flag += 1
        for idx_topping in range(len(data_topping)):
            if _flags_batter_topping_equal(data_batter, idx_batter, data_topping, idx_topping):
                _append_to_grouped(flag, data_batter, idx_batter, data_topping, idx_topping)
                flag = int(flag)


def _is_batter_flags_different(data_batter: dict, idx_batter: int) -> bool:
    return data_batter[idx_batter][1] != data_batter[idx_batter-1][1] and idx_batter > 0


def _flags_batter_topping_equal(
    data_batter: dict, idx_batter: int, data_topping: dict, idx_topping: int
) -> bool:
    return data_batter[idx_batter][1] == data_topping[idx_topping][1]


def _append_to_grouped(
    flag: int, data_batter: dict, idx_batter: int, data_topping: dict, idx_topping: int
) -> None:
    if flag >= 10:
        caller_counter = 1
    else:
        caller_counter = 2
    grouped.append((
        _append_to_flag(str(flag), caller_counter),
        data_batter[idx_batter][0],
        data_topping[idx_topping][0],
        flag)
    )


def _append_to_flag(flag_str: str, caller_counter: int) -> str:
    """ Append zeros to flag to make it look like id.

    Args:
        flag_str (str): flag converted to string

    Kwargs:
        caller_counter (int): number for multiplication of zeros in string

    Returns:
        string with flag and zeros concatenated before flag number
    """
    zeros_str = "0" * caller_counter
    return zeros_str + flag_str


merged_types = []
merged_all = []


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

    _group_data_by_flag(batters_type, topping_type)

    merged_types.append(_merge_data(data_types))
    merged_all.append(_merge_data(data_names))

    data_final = []
    # ! hardcoded
    for tuple_ in merged_all:
        tuple_2 = (tuple_[2], tuple_[1], tuple_[0], tuple_[3], tuple_[4])
        data_final.append(tuple_2)
    return data_final


call_counter = 0    # count how many times function is called


def _merge_data(outter_data: list) -> list:
    """ Merge outter and grouped data together.

    Args:
        outter_data (list): list with values from outter dictionaries
        grouped_data (list): list with all grouped values

    Returns:
        list with combined grouped and outter data
    """
    global call_counter
    data = _data_generated_by_counter()
    call_counter += 1

    merged = []
    len_group = len(data[0])
    global all_flags

    max_flag = max(all_flags)

    for idx_grouped_data in range(len(data)):
        for flag in range(1, max_flag+1):
            # id_ can be id from data list
            # or flag if there is not id in data
            id_ = _generate_id(data, idx_grouped_data, len_group)
            if id_ == flag:
                grouped_inner = [data[idx_grouped_data][k] for k in range(max_flag+1)]
                merged.append((data[flag-1], *grouped_inner))

    return merged


def _check_call_counter(data, len_group) -> list:
    if call_counter == 1:
        return [data[i][len_group-1] for i in range(len(data))]
    else:
        # all_flags contains id converted to integer
        # * example: if id is '0003' then int('0003') is 3 
        return _define_flags(data)


def _data_generated_by_counter():
    global grouped
    global merged_types
    if call_counter == 0:
        return grouped
    else:
        return merged_types


def _define_flags(grouped_data: list) -> list:
    try:
        return [int(tuple_[0]) for tuple_ in grouped_data]
    except ValueError:
        raise InvalidValue(
            "Some value in dictionary data is not valid.",
            ex_m.INVALID_DATA
        ) from None


def _generate_id(grouped_data, idx_grouped_data, len_group):
    global call_counter
    if call_counter == 1:
        return grouped_data[idx_grouped_data][len_group-1]
    return _id_error_handler(grouped_data, idx_grouped_data)


def _id_error_handler(grouped_data, idx_grouped_data):
    try:
        return int(grouped_data[idx_grouped_data][1])
    except ValueError:
        return int(grouped_data[idx_grouped_data][0])
