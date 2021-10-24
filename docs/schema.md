## Pydantic

At some point it might be interesting to make sure that the YAML we are reading follows
some standards. That is why we have introduced the ability to pass a schema our file
needs to follow.

This feature is supported by [Pydantic](https://pydantic-docs.helpmanual.io/), 
and not only helps us to validate the schema, but even updating the values we're 
reading with `Optionals` and defaults.

Let's continue working with our example YAML:

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

We can get this running as

```python
from typing import Optional, List, Dict

from levy.config import Config
from pydantic import BaseModel


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

cfg = Config.read_file("<file>", datatype=Kitten)
```

Note how this adds even another layer of flexibility, as after reading the config we will
have all the data we might require available to use.


<div class="termy">

```console
// We have the data attribute now hosting the data class
$ cfg.data
Kitten(title='Lévy the cat', age=None, colors=['black', 'white'], hobby={'eating': {'what': 'anything'}}, friends=[Friends(name='cartman', type='cat', fur='soft'), Friends(name='lima', type='cat', fur='soft')])

// Optional values become None
$ cfg.age
None

// We have missing values with their default
$ cfg.friends.lima.fur
"soft"
```

</div>
