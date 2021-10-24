## Rendering JSON Files

`levy` supports JSON file as well as YAML. All the features remain the same, however,
we need to make sure that the JSON file we write is a correctly formatted JSON
after the render phase, which might be a bit tricky at times.

> OBS: Note that the added difficulty is only for Jinja templating, as we need to
  take care about putting all the quotes and commas.

Let's revisit the first example we saw, and how it would look like as a JSON file:

```json
{
  "title": "Lévy the cat",
  "colors": ["black", "white"],
  "hobby": {
    "eating": {
      "what": "anything"
    }
  },
  "friends": [
    {% set friends = [ "cartman", "lima" ] %}
    {% for friend in friends %}
      {
        "name": "${ friend }",
        "type": "cat"
      }
        {% if loop.index0 < friends|length - 1%}
        ,
        {% endif %}
    {% endfor %}
    ]
}
```

As you can see, most of it is the same. However, in the `friends` list, we need
to add specific logic to add commas `,` if we have not reached the end of the loop.

Afterwards, the API remains:

```python
from levy.config import Config

cfg = Config.read_file("test.json")
```
