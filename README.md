# Intersphinx Registry

A simple utility package that provide default inter sphinx mapping for a large chunk of the python ecosystem.

Usage in `conf.py`

```python
from intersphinx_registry import get_intersphinx_mapping

# ...
intersphinx_mapping = get_intersphinx_mapping(
    packages={"ipython", "matplotlib", "pandas", "python"}
)
intersphinx_mapping.update({
    'overwrite': ('<url>', None),
    'my-package' : ('<url>', None),
})
```


## Why ?

Sometime packages docs move and it's hard to keep track of. We _try_ to keep the
registry up to date, so yo do not have to ask yourself questions and update your
intersphinx-mapping.

You also might not want to think about adding intersphinx mapping when you refer
to dependencies.

## A package url is wrong !

Please send a PR updating only this package in the `registry.json`. We try to
link only to _stable_ package, not dev versions.

## A package is missing !

We can't do all packages, but if you think a package is widely used and missing,
please send a PR.
