import os
import pytest
from typing import Dict, List, Optional
from unittest import mock

from pydantic import BaseModel, ValidationError

from levy.config import Config
from levy.renderer import render_reg
from levy.exceptions import ListParseException


class TestConfig:
    def setup(self):

        self.dir = os.path.dirname(os.path.realpath(__file__))
        self.resources = os.path.join(self.dir, "resources")

        self.file = os.path.join(self.resources, "test.yaml")
        self.cfg = Config.read_file(file=self.file)

    def test_name(self):
        """
        Default read name is root
        """

        assert self.cfg.name == "root"

    def test_root(self):
        """
        Root configs are parsed correctly
        """

        assert self.cfg.title == "Lévy the cat"
        # Access config also by call
        assert self.cfg("colors") == ["black", "white"]

    def test_dict(self):
        """
        Dictionaries become new Config
        """

        assert isinstance(self.cfg.hobby, Config)
        assert self.cfg.hobby.name == "hobby"
        assert self.cfg.hobby.eating.what == "anything"

    def test_lists(self):
        """
        Dict lists become namedtuples of Config
        """

        assert isinstance(self.cfg.friends, tuple)
        assert self.cfg.friends.cartman.type == "cat"

    def test_default(self):
        """
        We can use default values if config is missing
        If no default is specified, raise an exception
        """

        assert self.cfg("not in there", "default") == "default"
        with pytest.raises(AttributeError):
            self.cfg("not in there")

    def test_id_yaml(self):
        """
        Check how to use custom identifiers for lists
        """
        file = os.path.join(self.resources, "test_id.yaml")
        cfg = Config.read_file(file, list_id="id")
        assert isinstance(cfg.friends.lima, Config)

        with pytest.raises(ListParseException):
            Config.read_file(file, list_id="random")

    @mock.patch.dict(os.environ, {"VARIABLE": "random"})
    def test_env_var(self):
        """
        Render environment variables with and without default
        """
        file = os.path.join(self.resources, "test_env.yaml")
        cfg = Config.read_file(file)
        assert cfg.variable == "random"
        assert cfg.default == "bar"

    def test_custom_render(self):
        """
        Check renderer registry is applied when reading YAML
        """

        @render_reg.add()
        def my_func(num: int):
            return num + 1

        @render_reg.add("bar")  # Name can be arbitrary
        def upper(s: str):
            return s.upper()

        file = os.path.join(self.resources, "test_custom.yaml")
        cfg = Config.read_file(file)
        assert cfg.variable == 2
        assert cfg.foo == "X"

        # We can still call our function as usual
        assert my_func(1) == 2

    def test_validate(self):
        """
        Prove validation behavior
        """

        class Friends(BaseModel):
            name: str
            type: str
            fur: str = "soft"

        class Kitten(BaseModel):
            title: str
            age: Optional[int]
            colors: List[str]
            hobby: Dict[str, Dict[str, str]]
            friends: List[Friends]

        cfg = Config.read_file(self.file, datatype=Kitten)

        # We should have the data attribute now
        assert cfg.data is not None

        # We have optional values as None
        assert cfg.age is None

        # We have missing values with their default
        assert cfg.friends.lima.fur == "soft"

        # Value is not a dict, however colors is correct as we can cast int to str
        with pytest.raises(ValidationError):
            file = os.path.join(self.resources, "test_ko.yaml")
            Config.read_file(file, datatype=Kitten)
