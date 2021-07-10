# levy

[![Latest version](https://img.shields.io/pypi/v/levy.svg)](https://pypi.org/project/levy/)
[![Python versions](https://img.shields.io/pypi/pyversions/levy.svg)](https://pypi.org/project/levy/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![actions](https://github.com/pmbrull/levy/actions/workflows/CI.yaml/badge.svg)](https://github.com/pmbrull/levy)

> Yet Another Configuration Parser

This project is a lightweight take on configuration parsing with a twist.

So far, it only supports YAML files or reading configurations directly from a `dict`.

The interesting approach here is regarding handling multiple environments. Usually we
need to pass different parameters depending on where we are (DEV, PROD, and any 
arbitrary environment name we might use). It is also common to have these specific parameters
available as env variables, be it our infra or in a CI/CD process.

`levy` adds a `jinja2` layer on top of our YAML files, so that not only we can load
env variables on the fly, but helps us leverage templating syntax to keep
our configurations centralized and DRY.

## How to

Let's suppose we have the following configuration:

```yaml
title: "Lévy the cat"
colors:
  - "black"
  - "white"
hobby:
  eating:
    what: "anything"
friends:
  {% set friends = [ "cartman", "lima" ] %}
  {% for friend in friends %}
  - name: ${ friend }
    type: "cat"
  {% endfor %}
```

We have a bit of everything:
- Root configurations
- Simple lists
- Nested configurations
- Dynamic `jinja2` lists as nested configurations

We can create our `Config` object as

```python
from levy.config import Config

cfg = Config.read_file("test.yaml")
```

As there is the `jinja2` layer we might want to check what is the shape of the
parsed values. We can do so with `cfg._vars`. In our case we'll get back something
like:

```
{
'title': 'Lévy the cat',
'colors': ['black', 'white'],
'hobby': {
  'eating': {
    'what': 'anything'
    }
  },
'friends': [
  {'name': 'cartman', 'type': 'cat'},
  {'name': 'lima', 'type': 'cat'}
  ]
}
```

> OBS: When reading from files and for debugging purposes, we can access the `cfg._file`
var to check what file was parsed.

### Accessing values

All the information has been set as attributes to the `Config` instance. We can
retrieve the values as `cfg.<name>`, e.g.

```python
cfg.title  # 'Lévy the cat'
cfg.colors  # ['black', 'white']
```

Note that so far those are just `root` values, as they come directly from the root
configuration. Whenever we have a nested item, we are creating a `Config` attribute
with the key as name:

```python
print(cfg)  # Config(root)
print(cfg.hobby)  # Config(hobby)
```

If we need to retrieve nested values, as we are just nesting `Config` instances, we can
keep chaining attribute calls:

```python
cfg.hobby.eating.what  # 'anything'
```

### Nested Config lists

The `colors` list has nothing fancy in it, as we have simple types. However, we want
to parse nested configurations as `Config`, while being able to access them by name
as attributes.

To fit this spot we have `namedtuple`s. The list attribute becomes a `namedtuple` where
the properties are the `name`s of the nested items. `name` is set as the default
identifier, but we can pass others as parameter,

```python
print(cfg.friends.lima)  # Config(lima)
cfg.friends.lima.type  # 'cat'
```

And if we check the type...
```python
isinstance(cfg.friends, tuple)  # True
```

## Using defaults

It is common to fall back to default values when some parameter is not informed in our configuration.

We can `__call__` our `Config` in order to be able to apply them.

```python
cfg("not in there", default="default")  # 'default'
cfg("not in there", default=None)  # None
```

If no default is specified, the call will run the usual attribute retrieval. This is
interesting for cases where we need to dynamically get some configuration that *should*
be there:

```python
cfg("not in there")  # AttributeError
```

## Render custom functions

### Environment Variables

With this templating approach on top of YAML, we can not only use default behaviors, but also
define our own custom functionalities.

The one we have provided by default is reading environment variables at render time:

```yaml
variable: ${ env('VARIABLE') }
default: ${ env('foo', default='bar') }
```

Where the function `env` is the key name given to a function defined to `get` env vars
with an optional default. If the env variable is not found and no default is provided,
we'll get a `MissingEnvException`.

### Registering new functions

If we need to apply different functions when rendering the YAML, we can register them
by name before instantiating the `Config` class.

Let's imagine the following YAML file:

```yaml
variable: ${ my_func(1) }
foo: ${ bar('x') }
```

We then need to define the behavior of the functions `my_func` and `bar`.

```python
from levy.config import Config
from levy.renderer import render_reg

@render_reg.add()  # By default, it registers the function name
def my_func(num: int):
    return num + 1

@render_reg.add('bar')  # Name can be overwritten if required
def upper(s: str):
    return s.upper()

cfg = Config.read_file("<file>")
cfg.variable  # 2
cfg.foo  # 'X'
```

Note how we registered `my_func` with the same name it appeared in the YAML. However,
the name is completely arbitrary, and we can pass the function `upper` with the name `bar`.

With this approach one can add even further dynamism to the YAML config files.

To peek into the registry state, we can run:

```python
render_reg.registry
```

Which in the example will show us

```
{'env': <function __main__.get_env(conf_str: str, default: Optional[str] = None) -> str>,
 'my_func': <function __main__.my_func(num: int)>,
 'bar': <function __main__.upper(s: str)>}
```

## Contributing

You can install the project requirements with `make install`. To run the tests, `make install_test`
and `make unit`.

With `make precommit_install` you can install the pre-commit hooks.

To install the package from source, clone the repo, `pip install flit` and run `flit install`.

## References

- [pyconfs](https://github.com/gahjelle/pyconfs) as inspiration.
