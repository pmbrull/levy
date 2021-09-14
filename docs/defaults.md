## Accessing Data

Being flexible when working with config files is rather helpful. It is common to fall back to default values when some parameter is not informed in our configuration.

Instead of extracting the values as `attributes`, we can `__call__` our `Config` in order to be able to apply defaults at will.

<div class="termy">

```console
// We can access data by call
$ cfg("title")
"Lévy the cat"

// Here we can use defaults
$ cfg("not in there", default="random")
"random"

// We can return `None` as well
$ cfg("not in there", None)
None
```

</div>

## Dynamic Access

If no default is specified, the call will run the usual attribute retrieval. This is
interesting for cases where we need to dynamically get some configuration that *should*
be there.

<div class="termy">

```console
// If the attribute is not there...
$ cfg("not in there")
AttributeError
```

</div>
