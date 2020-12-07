class DonutDataError(Exception):
    """ General donut data exception. """


class InvalidSchemaError(DonutDataError):
    """ Raised if schema is not valid. """


class InvalidValue(DonutDataError, ValueError):
    """ Raised if value in donut data is not valid. """
