import os
import pytest

from levy.config import Config


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
