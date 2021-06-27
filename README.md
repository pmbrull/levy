# levy

> Yet Another Configuration Parser

This project is a lightweight take on configuration parsing with a twist.

So far, it only supports YAML files or reading configurations directly from a `dict`.

The interesting approach here is regarding handling multiple environments. Usually we
need to pass different parameters depending on where we are (DEV, PROD, and any 
arbitrary environment name we might use). It is also common to have these specific parameters
available as env variables, be it our infra or in a CI/CD process.

`levy` adds a `jinja2` layer on top of our YAML files, so that not only we can load
env variables on the fly, but helping us leverage templating syntax to keep
our configurations centralized and DRY.

## References

- [pyconfs](https://github.com/gahjelle/pyconfs) as inspiration.
