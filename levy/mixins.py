"""
Mixins for config
"""
import os
from typing import Optional

from jinja2 import Template

from levy.exceptions import MissingEnvException


class RenderMixin:
    """
    Contains functionalities to pass to ConfigParser
    to render config files
    """

    @staticmethod
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

    def render_str(self, raw: str, var_start="${", var_end="}"):
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
        rendered = template.render(env=self.get_env)
        return rendered
