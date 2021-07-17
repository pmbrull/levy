"""
Config parser definition
"""
from collections import namedtuple
from typing import Optional, Dict, Any, List

import logging
import yaml
from jsonschema import validate, ValidationError, SchemaError

from levy.renderer import render_str
from levy.exceptions import ListParseException


class Config:
    """
    This class parses the pipelines config files
    """

    def __init__(
        self,
        name: Optional[str] = None,
        conf: Optional[Dict[str, Any]] = None,
        list_id: Optional[str] = "name",
    ):
        """
        Load the config ingestion from a given path
        :param file: YAML file to load
        """
        self.name = name
        self._vars = conf
        self._list_id = list_id  # Identifies different entities in list

    @classmethod
    def read_file(
        cls,
        file: str,
        name: Optional[str] = "root",
        list_id: Optional[str] = "name",
        schema: Optional[Dict[Any, Any]] = None,
    ) -> "Config":
        """
        Load the configuration from a file
        :param file: YAML file to load
        :param name: Config name
        :param list_id: Identifier of different entities in config list
        :param schema: Used to validate the data to be loaded
        :return:
        """

        cfg = cls(name=name, list_id=list_id)
        cfg._file = file  # pylint: disable=attribute-defined-outside-init

        with open(cfg._file, "r") as yml_file:
            rendered = render_str(yml_file.read())
            cfg._vars = yaml.safe_load(rendered)

        cfg.validate_schema(schema)
        cfg.update_vars(cfg._vars)
        return cfg

    @classmethod
    def read_dict(
        cls,
        _vars: Dict[str, Any],
        name: Optional[str] = "root",
        list_id: Optional[str] = "name",
    ) -> "Config":
        """
        Create a Config instance from dict values
        :param _vars: config to load
        :param name: Config name
        :param list_id: Identifier of different entities in config list
        :return:
        """
        cfg = cls(name=name, conf=_vars, list_id=list_id)

        cfg.update_vars(cfg._vars)
        return cfg

    def update_vars(self, _vars: Dict[str, Any]):
        """
        Update attributes for Config.
        Created nested Configs for dictionaries & lists
        :param _vars: variables to set
        :return:
        """
        for key, val in _vars.items():

            if isinstance(val, dict):
                self.__setattr__(
                    key,
                    self.__class__(name=key, conf=_vars[key], list_id=self._list_id),
                )
                self(key).update_vars(val)

            elif isinstance(val, list):
                self.update_list(key, val)

            else:
                self.__setattr__(key, val)

    def update_list(self, key: str, values: List[Any]):
        """
        Prepare attributes coming from a list.
        If any elements is a dictionary, try to set a namedtuple of Config, otherwise
        pass the list as is.
        :param key: configuration key
        :param values: list to add as attributes
        :return:
        """
        if any((isinstance(val, dict)) for val in values):
            try:
                configs = [
                    Config.read_dict(v, name=v[self._list_id], list_id=self._list_id)
                    for v in values
                ]
                conf_tuple = namedtuple(key, (conf(self._list_id) for conf in configs))
                self.__setattr__(key, conf_tuple(*configs))
            except Exception:
                raise ListParseException(f"Error parsing list in {key}")

        else:
            self.__setattr__(key, values)

    def validate_schema(self, schema: Optional[Dict[Any, Any]] = None):
        """
        Optionally, validate the incoming data vs a provided schema.

        The schema should follow JSON schema specification.
        :param schema: JSON schema specification as a Dict
        :return: Either the validation passes or raise an exception
        """
        if schema:
            try:
                validate(self._vars, schema)
            except ValidationError as err:
                logging.error("Data does not follow the provided schema.")
                raise err
            except SchemaError as err:
                logging.error("Trying to run a validation with a bad schema")
                raise err

    def __call__(self, key: str, default: Optional[Any] = ...):
        """
        Used for info retrieval
        :param key: attribute to get
        :param default: optional default to get if key not in __dict__
        :return:
        """
        if default is ...:
            return self.__getattribute__(key)

        return self.__getattribute__(key) if key in self.__dict__ else default

    def __repr__(self):
        return f"Config({self.name})"
