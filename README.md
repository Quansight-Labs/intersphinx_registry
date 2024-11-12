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

## quick lookup

You can use the following to lookup target/webpages of various packages.

Call without arguments to get help:

```
$ python -m intersphinx_registry.lookup

    Usage: python -m intersphinx_registry.lookup <package>[,package] [search_term]

    Example:

    $ python -m intersphinx_registry.lookup numpy,scipy array
    $ python -m intersphinx_registry.lookup ipython formatters.html

```

You can search multiple packages as once.

```
$ python -m intersphinx_registry.lookup numpy,scipy Universal
std:label ufuncs                             NumPy 2.1    'Universal functions (ufunc)'                         https://numpy.org/doc/stable/reference/ufuncs.html#ufuncs
std:label ufuncs-basics                      NumPy 2.1    'Universal functions (ufunc) basics'                  https://numpy.org/doc/stable/user/basics.ufuncs.html#ufuncs-basics
std:label ufuncs-internals                   NumPy 2.1    'Universal functions'                                 https://numpy.org/doc/stable/dev/internals.code-explanations.html#ufuncs-internals
std:doc   reference/ufuncs                   NumPy 2.1    'Universal functions (ufunc)'                         https://numpy.org/doc/stable/reference/ufuncs.html
std:doc   user/basics.ufuncs                 NumPy 2.1    'Universal functions (ufunc) basics'                  https://numpy.org/doc/stable/user/basics.ufuncs.html
std:label non-uniform-random-number-sampling SciPy 1.14.1 'Universal Non-Uniform Random Number Sampling in SciPy' https://docs.scipy.org/doc/scipy/tutorial/stats/sampling.html#non-uniform-random-number-sampling
std:doc   tutorial/stats/sampling            SciPy 1.14.1 'Universal Non-Uniform Random Number Sampling in SciPy' https://docs.scipy.org/doc/scipy/tutorial/stats/sampling.html
```

Warning, there is no cache, it downloads the inventory of each mentioned package every time.


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
