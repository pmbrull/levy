"""
Define module custom exceptions
"""


class MissingEnvException(Exception):
    """
    Error raised when the config file cannot be parsed
    """


class ListParseException(Exception):
    """
    Tried to parse a config list
    """
