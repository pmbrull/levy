"""
Config parser definition
"""
import yaml

from collections import namedtuple
from typing import Optional, Dict, Any

from levy.mixins import RenderMixin


class _NULL:
    """Used to have an internal alternative to None"""

    pass


class Config(RenderMixin):
    """
    This class parses the pipelines config files
    """

    def __init__(
        self, name: Optional[str] = None, conf: Optional[Dict[str, Any]] = None
    ):
        """
        Load the config ingestion from a given path
        :param file: YAML file to load
        """
        self.name = name
        self._vars = conf
        self._list_id = "name"  # Identifies different entities in list

    @classmethod
    def read_file(cls, file: str, name: Optional[str] = "root") -> "Config":
        """
        Load the configuration from a file
        :param file: YAML file to load
        :param name: Config name
        :return:
        """

        cfg = cls(name=name)
        cfg._file = file

        with open(cfg._file, "r") as yml_file:
            rendered = cfg.render_str(yml_file.read())
            cfg._vars = yaml.safe_load(rendered)

        cfg.update_vars(cfg._vars)
        return cfg

    @classmethod
    def read_dict(cls, _vars: Dict[str, Any], name: Optional[str] = "root") -> "Config":
        """
        Create a Config instance from dict values
        :param _vars: config to load
        :param name: config name
        :return:
        """
        cfg = cls(name=name)
        cfg._vars = _vars

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
                self.__setattr__(key, self.__class__(name=key, conf=_vars[key]))
                self(key).update_vars(val)

            elif isinstance(val, list):
                configs = [Config.read_dict(v, name=v[self._list_id]) for v in val]
                ConfTuple = namedtuple(key, (conf.name for conf in configs))
                self.__setattr__(key, ConfTuple(*configs))

            else:
                self.__setattr__(key, val)

    def __call__(self, key: str, default: Optional[Any] = _NULL):
        """
        Used for info retrieval
        :param key: attribute to get
        :param default: optional default to get if key not in __dict__
        :return:
        """
        if default is _NULL:
            return self.__getattribute__(key)

        return self.__getattribute__(key) if key in self.__dict__ else default

    def __repr__(self):
        return f"Config({self.name})"
