# Intersphinx Registry

A simple utility package that provides a default intersphinx mapping for a large chunk of the Python ecosystem.

## Installation

```bash
# Core package only (for use in conf.py/Sphinx projects)
pip install intersphinx_registry

# With a command-line interface
pip install intersphinx_registry[cli]
# or
uv tool install intersphinx_registry[cli]
# or
pipx install intersphinx_registry[cli]
```

You can also use it without installation:

```bash
uvx intersphinx-registry[cli] lookup numpy,scipy array
```

## Usage in `conf.py`

```python
from intersphinx_registry import get_intersphinx_mapping

# ...
intersphinx_mapping = get_intersphinx_mapping(
    packages={"ipython", "matplotlib", "pandas", "python"}
)
intersphinx_mapping.update({
    'overwrite': ('<url>', None),
    'my-package': ('<url>', None),
})
```

## Command-line interface

The package provides a command-line interface for looking up intersphinx targets.

> [!NOTE]
> The CLI requires installing the `[cli]` extra: `pip install intersphinx_registry[cli]`

```bash
$ intersphinx-registry --version
# or
$ intersphinx-registry -v
```

### quick lookup

You can use the lookup command to search for intersphinx targets and webpages across various packages.

Call without arguments to get help:

```bash
$ intersphinx-registry lookup
```

Basic usage:

```bash
$ intersphinx-registry lookup <package>[,package] [search_term]
```

Examples:

```bash
$ intersphinx-registry lookup numpy,scipy array
$ intersphinx-registry lookup ipython formatters.html
```

You can search multiple packages at once:

```bash
$ intersphinx-registry lookup numpy,scipy Universal
std:label ufuncs                             NumPy 2.1    'Universal functions (ufunc)'                         https://numpy.org/doc/stable/reference/ufuncs.html#ufuncs
std:label ufuncs-basics                      NumPy 2.1    'Universal functions (ufunc) basics'                  https://numpy.org/doc/stable/user/basics.ufuncs.html#ufuncs-basics
std:label ufuncs-internals                   NumPy 2.1    'Universal functions'                                 https://numpy.org/doc/stable/dev/internals.code-explanations.html#ufuncs-internals
std:doc   reference/ufuncs                   NumPy 2.1    'Universal functions (ufunc)'                         https://numpy.org/doc/stable/reference/ufuncs.html
std:doc   user/basics.ufuncs                 NumPy 2.1    'Universal functions (ufunc) basics'                  https://numpy.org/doc/stable/user/basics.ufuncs.html
std:label non-uniform-random-number-sampling SciPy 1.14.1 'Universal Non-Uniform Random Number Sampling in SciPy' https://docs.scipy.org/doc/scipy/tutorial/stats/sampling.html#non-uniform-random-number-sampling
std:doc   tutorial/stats/sampling            SciPy 1.14.1 'Universal Non-Uniform Random Number Sampling in SciPy' https://docs.scipy.org/doc/scipy/tutorial/stats/sampling.html
```

> [!WARNING]
> There is no cache; the lookup command downloads the inventory of each mentioned package every time.

You can also use the lookup functionality via the module interface:

```bash
$ python -m intersphinx_registry.lookup <package>[,package] [search_term]
```

### reverse-lookup

Find which package a documentation URL belongs to and get its Sphinx reference.

```bash
$ intersphinx-registry reverse-lookup <url> [url...]
```

Examples:

```bash
$ intersphinx-registry reverse-lookup https://numpy.org/doc/stable/reference/arrays.html
$ intersphinx-registry reverse-lookup https://docs.python.org/3/ https://numpy.org/doc/stable/
```

This is useful when you have a link to documentation and want to know the corresponding Sphinx reference (`:domain:package:target`) that you can use in your own documentation with intersphinx.

### rev-search

Scan `.rst` files in a directory for hardcoded URLs and suggest replacements with Sphinx references.

```bash
$ intersphinx-registry rev-search <directory-or-file>
```

Examples:

```bash
$ intersphinx-registry rev-search docs/
$ intersphinx-registry rev-search docs/index.rst
```

This command helps you convert hardcoded URLs in your reStructuredText documentation into proper intersphinx references. It scans your documentation files, finds URLs that match known packages in the registry, and shows you a diff-style output of the suggested changes.

## Why ?

Sometimes, packages docs move and it's hard to keep track of them. We _try_ to keep the
registry up to date, so you do not have to ask yourself questions and update your
intersphinx-mapping.

You also might not want to think about adding intersphinx mapping when you refer
to dependencies.

## A package url is wrong !

Please send a PR updating only this package in the `registry.json`. We try to
link only to _stable_ package, not dev versions.

## A package is missing !

We can't do all packages, but if you think a package is widely used and missing,
please send a PR.
