"""
Mixins for config
"""
import os
from collections import namedtuple
from typing import Optional

from jinja2 import Template

from levy.exceptions import MissingEnvException


def register():
    """
    Helps us register custom functions for rendering
    """
    registry = dict()

    def add(name: str = None):
        def inner(fn):
            _name = fn.__name__ if not name else name
            registry[_name] = fn
            return fn

        return inner

    Register = namedtuple("Register", ["add", "registry"])
    return Register(add, registry)


render_reg = register()


@render_reg.add("env")  # Use this function as the default registry
def get_env(conf_str: str, default: Optional[str] = None) -> str:
    """
    Used to retrieve env vars in the rendering process.
    """
    env = os.environ.get(conf_str, default)

    if not env:
        raise MissingEnvException(
            f"Missing env variable {conf_str} when rendering the YAML, add the "
            f"env var or set a default"
        )

    return env


def render_str(raw: str, var_start="${", var_end="}"):
    """
    Given a string with Jinja templating, return
    the rendered version.
    :param raw: raw string to render
    :param var_start: to indicate jinja variable start
    :param var_end: for finishing jinja variable rendering
    :return: string with rendered logic
    """
    template = Template(
        raw, variable_start_string=var_start, variable_end_string=var_end
    )
    rendered = template.render(render_reg.registry)
    return rendered
