<p align="center">
    <em>Supercharge YAML configs with Jinja templates, typing and custom functions.</em>
</p>
<p align="center">
<a href="https://pypi.org/project/levy/" target="_blank">
    <img src="https://img.shields.io/pypi/v/levy.svg" alt="pypi">
</a>
<a href="https://pypi.org/project/levy/" target="_blank">
    <img src="https://img.shields.io/pypi/pyversions/levy.svg" alt="Versions">
</a>
<a href="https://github.com/psf/black" target="_blank">
    <img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="Black">
</a>
<a href="https://github.com/pmbrull/levy" target="_blank">
    <img src="https://github.com/pmbrull/levy/actions/workflows/CI.yaml/badge.svg" alt="Package version">
</a>
<a href="https://codecov.io/gh/pmbrull/levy">
    <img src="https://codecov.io/gh/pmbrull/levy/branch/main/graph/badge.svg?token=C2OSY77VFR"/>
</a> 
</p>

---

**Documentation**: <a href="https://pmbrull.github.io/levy/" target="_blank">https://pmbrull.github.io/levy/</a>

**Source Code**: <a href="https://github.com/pmbrull/levy" target="_blank">https://github.com/pmbrull/levy</a>

---

## Installation

Get up and running with

<div class="termy">

```console
$ pip install levy
---> 100%
Successfully installed levy
```

</div>


This will also bring to your environment `PyYAML`, `Jinja2` and `pydantic`.

## Quickstart

This project is a lightweight take on configuration parsing with a twist.  So far, it only supports YAML files or reading configurations directly from a `dict`.

`levy` adds a `jinja2` layer on top our YAML files, which allows us to run any Jinja templating syntax on them. Later on, we will also see how to register our own custom functions.

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

### Accessing Values

`levy` dynamically creates `Config` objects building the whole tree. This means that we can use the same strategy to retrieve data from the root level or any arbitrary nesting.

<div class="termy">

```console
// Check Config level
$ cfg
Config("root")

// Access information as attributes
$ cfg.title
"Lévy the cat"
$ cfg.colors
["black", "white"]

// Even if those are nested dicts
$ cfg.hobby
Config("hobby")

// Chain calls until reaching our values
$ cfg.hobby.eating.what
"anything"
```

</div>

### Accessing Lists

Getting data from a list is the same as for any `Config`.

<div class="termy">

```console
// Access a list element by name
$ cfg.friends.lima
Config(lima)

// Extract information as usual
$ cfg.friends.lima.type
cat
```

</div>