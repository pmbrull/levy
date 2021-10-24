## Environment Variables

It is common to have these specific parameters available as env variables, be it our infra or in a CI/CD process. In these situations, we often end up duplicating configurations, which might end up with issues rising from a configuration drift between environments.

To ease these scenarios `levy` provides one functionality out of the box: read environment variables at render time.

```yaml
variable: ${ env('VARIABLE') }
default: ${ env('foo', default='bar') }
```

Where the function `env` is the key name given to a function defined to `get` env vars
with an optional default. If the env variable is not found and no default is provided,
we'll get a `MissingEnvException`.

We can then access these values as usual.

## Registering new functions

If we need to apply different functions when rendering the files, we can register them
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
```

<div class="termy">

```console
// We can access the results of the functions as usual
$ cfg.variable
2

$ cfg.foo
"X"
```

</div>

Note how we registered `my_func` with the same name it appeared in the YAML. However,
the name is completely arbitrary, and we can pass the function `upper` with the name `bar`.

With this approach one can add even further dynamism to our config files.

## Registry

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

> OBS: If you take a look at the source code, the `env` function has been defined in the registry as shown here.
