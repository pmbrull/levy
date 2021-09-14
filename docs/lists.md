## Jinja

Having a `jinja2` layer on our config files helps us centralise information and keep configurations as DRY as possible.

Recall our test YAML:

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

## Namedtuples

The `colors` list has nothing fancy in it, as we have simple types. However, we want
to parse nested configurations as `Config`, while being able to access them by name
as attributes.

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

To fit this spot we have `namedtuple`s. The list attribute becomes a `namedtuple` where
the properties are the `name`s of the nested items. If we check the type...

<div class="termy">

```console
// Check list instance
$ isinstance(cfg.friends, tuple)
True
```

</div>

## Identifiers

`name` is set as the default identifier, i.e., will be used to name the `namedtuple`, but we can pass others as parameter. For example, we can set it as `id` if we had the following YAML:

```yaml
[...]
friends:
  {% set friends = [ "cartman", "lima" ] %}
  {% for friend in friends %}
  - id: ${ friend }
    type: "cat"
  {% endfor %}
```


```python
from levy.config import Config

cfg = Config.read_file(file, list_id="id")
```

## Handling Exceptions

If we encounter an error while defining the `namedtuple`s structure, we will get a 
`ListParseException`. We should then check how are we defining the lists and our `list_id` argument.

> OBS: Note that the `list_id` field should be a valid `namedtuple` key. This means that
    it cannot contain spaces or other not supported special characters.
