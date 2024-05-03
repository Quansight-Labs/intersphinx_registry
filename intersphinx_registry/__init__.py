"""
This package provides convenient utilities and data to write a sphinx config file.
"""
from __future__ import annotations

from pathlib import Path
import json
from typing import Dict, Tuple

__version__ = "0.0.1"

registry_file = Path(__file__).parent / "registry.json"


def get_intersphinx_mapping() -> Dict[str, Tuple[str, str]]:
    """
    Return values of intersphinx_mapping for sphinx configuration.

    For conveneience, the return dict is a copy so should be ok to mutate
    """
    return json.loads(registry_file.read_bytes())


data = {}

# This is a raw dump of what I found on my machine. Some of those are likely wrong and need update.
data.update(
    {
        "pytorch_lightning": (
            "https://pytorch-lightning.readthedocs.io/en/stable/",
            None,
        ),
        "sphinx_automodapi": (
            "https://sphinx-automodapi.readthedocs.io/en/stable/",
            None,
        ),
        "prompt_toolkit": (
            "https://python-prompt-toolkit.readthedocs.io/en/stable/",
            None,
        ),
        "importlib-resources": (
            "https://importlib-resources.readthedocs.io/en/latest",
            None,
        ),
        "django": (
            "https://docs.djangoproject.com/en/2.2/",
            "https://docs.djangoproject.com/en/2.2/_objects/",
        ),
        "pandas": (
            "https://pandas.pydata.org/pandas-docs/stable/",
            "https://pandas.pydata.org/pandas-docs/stable/objects.inv",
        ),
        "numpy": (
            "https://numpy.org/doc/stable/",
            "https://numpy.org/doc/stable/objects.inv",
        ),
        "asyncssh": (
            "https://asyncssh.readthedocs.io/en/latest/",
            "https://asyncssh.readthedocs.io/en/latest/objects.inv",
        ),
        "zarr": (
            "https://zarr.readthedocs.io/en/latest/",
            "https://zarr.readthedocs.io/en/latest/objects.inv",
        ),
        "fsspec": (
            "https://filesystem-spec.readthedocs.io/en/latest/",
            "https://filesystem-spec.readthedocs.io/en/latest/objects.inv",
        ),
        "napari_plugin_engine": [
            "https://napari-plugin-engine.readthedocs.io/en/latest/",
            "https://napari-plugin-engine.readthedocs.io/en/latest/objects.inv",
        ],
        "magicgui": [
            "https://pyapp-kit.github.io/magicgui/",
            "https://pyapp-kit.github.io/magicgui/objects.inv",
        ],
        "Pillow": ("https://pillow.readthedocs.io/en/stable/", None),
        "PyPUG": ("https://packaging.python.org/en/latest/", None),
        "anndata": ("https://anndata.readthedocs.io/en/stable/", None),
        "asdf-astropy": ("https://asdf-astropy.readthedocs.io/en/latest/", None),
        "astropy-dev": ("https://docs.astropy.org/en/latest/", None),
        "asv": ("https://asv.readthedocs.io/en/stable/", None),
        "attrs": ("https://www.attrs.org/en/stable/", None),
        "bhub": ("https://binderhub.readthedocs.io/en/latest/", None),
        "bokeh": ("https://docs.bokeh.org/en/latest", None),
        "boltons": ("https://boltons.readthedocs.io/en/latest/", None),
        "bottle": ("https://bottlepy.org/docs/dev/", None),
        "build": ("https://pypa-build.readthedocs.io/en/latest/", None),
        "cartopy": ("https://scitools.org.uk/cartopy/docs/latest/", None),
        "cffi": ("https://cffi.readthedocs.io/en/latest/", None),
        "click": ("https://click.palletsprojects.com/", None),
        "conda": ("https://conda.io/en/latest/", None),
        "cycler": ("https://matplotlib.org/cycler/", None),
        "cython": ("https://docs.cython.org/en/latest", None),
        "dask": ("https://docs.dask.org/en/latest", None),
        "dateutil": ("https://dateutil.readthedocs.io/en/latest/", None),
        "devguide": ("https://devguide.python.org/", None),
        "devpi": ("https://devpi.net/docs/devpi/devpi/latest/+doc", None),
        "dh-virtualenv": ("https://dh-virtualenv.readthedocs.io/en/latest/", None),
        "distlib": ("https://distlib.readthedocs.io/en/latest/", None),
        "distributed": ("https://distributed.dask.org/en/stable/", None),
        "dlpack": ("https://dmlc.github.io/dlpack/latest", None),
        "flax": ("https://flax.readthedocs.io/en/latest/", None),
        "flexx": ("https://flexx.readthedocs.io/en/latest/", None),
        "fsspec": ("https://filesystem-spec.readthedocs.io/en/latest/", None),
        "geopandas": ("https://geopandas.org/en/stable/", None),
        "hub": ("https://jupyterhub.readthedocs.io/en/latest/", None),
        "imageio": ("https://imageio.readthedocs.io/en/stable", None),
        "ipykernel": ("https://ipykernel.readthedocs.io/en/latest/", None),
        "ipyleaflet": ("https://ipyleaflet.readthedocs.io/en/latest/", None),
        "ipyparallel": ("https://ipyparallel.readthedocs.io/en/latest/", None),
        "ipython": ("https://ipython.readthedocs.io/en/latest/", None),
        "ipywidgets": ("https://ipywidgets.readthedocs.io/en/latest/", None),
        "jax": ("https://jax.readthedocs.io/en/latest/", None),
        "jedi": ("https://jedi.readthedocs.io/en/latest/", None),
        "jinja": ("http://jinja.pocoo.org/docs", None),
        "jupyter": ("https://jupyter.readthedocs.io/en/latest", None),
        "jupyter-server": ("https://jupyter-server.readthedocs.io/en/stable/", None),
        "jupyter_core": ("https://jupyter-core.readthedocs.io/en/stable/", None),
        "jupyterbook": ("https://jupyterbook.org/", None),
        "jupyterclient": ("https://jupyter-client.readthedocs.io/en/latest/", None),
        "jupytercore": ("https://jupyter-core.readthedocs.io/en/latest/", None),
        "jupytext": ("https://jupytext.readthedocs.io/en/stable/", None),
        "kwarray": ("https://kwarray.readthedocs.io/en/latest/", None),
        "kwimage": ("https://kwimage.readthedocs.io/en/latest/", None),
        "lab": ("https://jupyterlab.readthedocs.io/en/latest/", None),
        "llvmlite": ("https://llvmlite.readthedocs.io/en/latest/", None),
        "lxml": ("https://lxml.de/apidoc/", None),
        "markdown_it": ("https://markdown-it-py.readthedocs.io/en/latest", None),
        "matplotlib": ("https://matplotlib.org/stable/", None),
        "meson-python": ("https://meson-python.readthedocs.io/en/stable/", None),
        "monkeytype": ("https://monkeytype.readthedocs.io/en/latest", None),
        "mpmath": ("https://mpmath.org/doc/current/", None),
        "myst-nb": ("https://myst-nb.readthedocs.io/en/v0.12.3/", None),
        "myst-parser": ("https://myst-parser.readthedocs.io/en/v0.15.1/", None),
        "nbconvert": ("https://nbconvert.readthedocs.io/en/latest/", None),
        "nbformat": ("https://nbformat.readthedocs.io/en/latest/", None),
        "nbgitpuller": ("https://nbgitpuller.readthedocs.io/en/latest/", None),
        "nbsphinx": ("https://nbsphinx.readthedocs.io/", None),
        "ndsampler": ("https://ndsampler.readthedocs.io/en/latest/", None),
        "neps": ("https://numpy.org/neps/", None),
        "networkx": ("https://networkx.org/documentation/stable/", None),
        "notebook": ("https://jupyter-notebook.readthedocs.org/en/stable/", None),
        "nox": ("https://nox.thea.codes/en/latest/", None),
        # is this one wrong ? numpy-dev ?
        # "numpy": ("https://numpy.org/devdocs/", None),
        "numpy": ("https://numpy.org/doc/stable/", None),
        #
        "numpy-tutorials": ("https://numpy.org/numpy-tutorials", None),
        "numpydoc": ("https://numpydoc.readthedocs.io/en/latest", None),
        "nx-guides": ("https://networkx.org/nx-guides/", None),
        "openstack": ("https://docs.openstack.org/glance/latest/", None),
        # those are two different things:
        # "packaging": ("https://packaging.pypa.io/en/latest/", None),
        # "packaging": ("https://packaging.python.org/en/latest", None),
        # "packaging": ("https://packaging.python.org/en/latest/", None),
        # "packaging.python.org": ("https://packaging.python.org/en/latest/", None),
        "pandas": ("https://pandas.pydata.org/docs/", None),
        # this was the old ones.
        #        "pandas": ("https://pandas.pydata.org/pandas-docs/stable", None),
        "pandas-gbq": ("https://pandas-gbq.readthedocs.io/en/latest/", None),
        "parso": ("https://parso.readthedocs.io/en/latest/", None),
        "pip": ("https://pip.pypa.io/en/latest/", None),
        "pipenv": ("https://pipenv.pypa.io/en/latest/", None),
        "piwheels": ("https://piwheels.readthedocs.io/en/latest/", None),
        "pluggy": ("https://pluggy.readthedocs.io/en/stable", None),
        "poliastro": ("https://docs.poliastro.space/en/v0.15.2/", None),
        "py": ("https://pylib.readthedocs.io/en/latest/", None),
        "pyarrow": ("https://arrow.apache.org/docs/", None),
        "pybind11": ("https://pybind11.readthedocs.io/en/stable/", None),
        "pyerfa": ("https://pyerfa.readthedocs.io/en/stable/", None),
        "pygraphviz": ("https://pygraphviz.github.io/documentation/stable/", None),
        "pymde": ("https://pymde.org/", None),
        "pymongo": ("https://pymongo.readthedocs.io/en/stable/", None),
        "pynsist": ("https://pynsist.readthedocs.io/en/latest/", None),
        "pypa": ("https://www.pypa.io/en/latest/", None),
        "pypug": ("https://packaging.python.org/", None),
        "pypy": ("http://pypy.readthedocs.org/en/latest/", None),
        "pyro": ("http://docs.pyro.ai/en/stable/", None),
        "pytest": ("https://pytest.org/en/stable/", None),
        "python": ("https://docs.python.org/3", None),
        "python": ["https://docs.python.org/3/", None],
        "python-guide": ("https://docs.python-guide.org", None),
        "qiskit": ("https://qiskit.org/documentation/", None),
        "qtconsole": ("https://jupyter.org/qtconsole/dev/", None),
        "readthedocs": ("https://docs.readthedocs.io/en/stable", None),
        "requests": ("https://docs.python-requests.org/en/latest/", None),
        "rpy2": ("https://rpy2.github.io/doc/latest/html/", None),
        "rst-to-myst": ("https://rst-to-myst.readthedocs.io/en/stable/", None),
        "rtd": ("https://docs.readthedocs.io/en/stable/", None),
        "rtd-dev": ("https://dev.readthedocs.io/en/latest/", None),
        "scanpy": ("https://scanpy.readthedocs.io/en/stable/", None),
        #  both of these are correct,
        # "scipy": ("https://docs.scipy.org/doc/scipy/", None),
        # but this one has API I think
        "scipy": ("https://docs.scipy.org/doc/scipy/reference/", None),
        #
        # "scipy-devdocs": ("https://scipy.github.io/devdocs/", None),
        "scipy-lecture-notes": ("https://scipy-lectures.org", None),
        "scriptconfig": ("https://scriptconfig.readthedocs.io/en/latest/", None),
        "server": ("https://jupyter-server.readthedocs.org/en/stable", None),
        "setuptools": ("https://setuptools.pypa.io/en/latest/", None),
        "setuptools": ("https://setuptools.pypa.io/en/stable", None),
        "six": ("https://six.readthedocs.io", None),
        "skimage": ("https://scikit-image.org/docs/stable/", None),
        "spack": ("https://spack.readthedocs.io/en/latest/", None),
        "sparse": ("https://sparse.pydata.org/en/latest/", None),
        "sphinx": ("https://www.sphinx-doc.org/en/master/", None),
        "sphinx-gallery": ("https://sphinx-gallery.github.io/stable/", None),
        "sqlalchemy": ("https://docs.sqlalchemy.org/en/latest/", None),
        "statsmodels": ("https://www.statsmodels.org/stable", None),
        "sympy": ("https://docs.sympy.org/latest/", None),
        "tljh": ("https://tljh.jupyter.org/en/latest/", None),
        "torch": ("https://pytorch.org/docs/master/", None),
        "tornado": ("https://www.tornadoweb.org/en/stable/", None),
        "tox": ("https://tox.wiki/en/latest/", None),
        "tox": ("https://tox.wiki/en/stable", None),
        "traitlets": ("https://traitlets.readthedocs.io/en/stable/", None),
        "twine": ("https://twine.readthedocs.io/en/stable/", None),
        "typing": ("https://typing.readthedocs.io/en/latest/", None),
        "ubelt": ("https://ubelt.readthedocs.io/en/latest/", None),
        "urwid": ("https://urwid.org/", None),
        "virtualenv": ("https://virtualenv.pypa.io/en/stable/", None),
        "writethedocs": ("https://www.writethedocs.org/", None),
        "xarray": ("https://docs.xarray.dev/en/stable/", None),
        "xdoctest": ("https://xdoctest.readthedocs.io/en/latest/", None),
        "z2jh": ("https://zero-to-jupyterhub.readthedocs.io/en/latest/", None),
    }
)
