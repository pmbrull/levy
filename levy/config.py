"""
Config parser definition
"""
import logging
from collections import namedtuple
from typing import Any, Dict, Generic, List, Optional, TypeVar

import yaml
from pydantic import ValidationError

from levy.exceptions import ListParseException
from levy.renderer import render_str

T = TypeVar("T")


class Config(Generic[T]):
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

        self.file = None  # Present if we read_file
        self.data = None  # Present if we read a file with datatype

    @classmethod
    def read_file(
        cls,
        file: str,
        *,
        name: Optional[str] = "root",
        list_id: Optional[str] = "name",
        datatype: Optional[T] = None,
    ) -> "Config":
        """
        Load the configuration from a file
        :param file: YAML file to load
        :param name: Config name
        :param list_id: Identifier of different entities in config list
        :param datatype: Class defining incoming data
        :return:
        """

        with open(file, "r") as yml_file:
            rendered = render_str(yml_file.read())
            cfg = cls.read_dict(
                yaml.safe_load(rendered), name=name, list_id=list_id, datatype=datatype
            )

        cfg._file = file  # pylint: disable=attribute-defined-outside-init
        return cfg

    @classmethod
    def read_dict(
        cls,
        _vars: Dict[str, Any],
        *,
        name: Optional[str] = "root",
        list_id: Optional[str] = "name",
        datatype: Optional[T] = None,
    ) -> "Config":
        """
        Create a Config instance from dict values
        :param _vars: config to load
        :param name: Config name
        :param list_id: Identifier of different entities in config list
        :param datatype: Class defining incoming data
        :return:
        """
        cfg = cls(name=name, conf=_vars, list_id=list_id)

        cfg.validate_schema(datatype)
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

    def validate_schema(self, datatype: Optional[T] = None):
        """
        Optionally, validate the incoming data vs a provided schema.

        The schema should follow JSON schema specification.
        :param datatype: Pydantic data type class
        :return: Either the validation passes or raise an exception
        """
        if datatype:
            try:
                self.data = datatype(**self._vars)
                logging.info(f"Updating vars based on {datatype}")
                self._vars = self.data.dict()
            except ValidationError as e:
                logging.error(f"Error validating data with {datatype}")
                raise e

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
