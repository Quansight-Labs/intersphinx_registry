import shutil
import sys
from datetime import timedelta
from pathlib import Path

import platformdirs
import requests_cache

from . import __version__


def _compress_user_path(path: str) -> str:
    """
    Replace home directory with ~ in a path string.

    Parameters
    ----------
    path : str
        Path to compress

    Returns
    -------
    str
        Path with home directory replaced by ~
    """
    home = str(Path.home())
    if path.startswith(home):
        return path.replace(home, "~", 1)
    return path


def _get_cache_dir() -> Path:
    """
    Get the cache directory for the current version of intersphinx_registry.

    Returns
    -------
    Path
        Cache directory path with version subdirectory
    """
    base_cache_dir = Path(platformdirs.user_cache_dir("intersphinx_registry"))
    cache_dir = base_cache_dir / __version__
    cache_dir.mkdir(parents=True, exist_ok=True)

    return cache_dir


def _cleanup_old_caches() -> None:
    """
    Remove cache directories from old versions of intersphinx_registry.
    Only keeps the current version's cache.
    """
    base_cache_dir = Path(platformdirs.user_cache_dir("intersphinx_registry"))

    if not base_cache_dir.exists():
        return

    current_version = __version__

    for version_dir in base_cache_dir.iterdir():
        if version_dir.is_dir() and version_dir.name != current_version:
            try:
                shutil.rmtree(version_dir)
            except Exception:
                pass


def _install_cache() -> None:
    """
    Install the version-specific requests cache.
    Cleans up old caches on first use.
    """
    _cleanup_old_caches()

    cache_dir = _get_cache_dir()
    cache_path = cache_dir / "intersphinx_cache.sqlite"

    requests_cache.install_cache(
        str(cache_path),
        backend="sqlite",
        expire_after=timedelta(hours=6),
        stale_if_error=True,
        cache_control=True,
    )


def _are_dependencies_available() -> bool:
    """
    Check if CLI dependencies are missing or not.
    Returns True if all dependencies are available, False otherwise.
    """
    missing = []
    try:
        import sphinx  # noqa: F401
    except ModuleNotFoundError:
        missing.append("sphinx")

    try:
        import requests  # noqa: F401
    except ModuleNotFoundError:
        missing.append("requests")

    try:
        import requests_cache  # noqa: F401
    except ModuleNotFoundError:
        missing.append("requests-cache")

    try:
        import platformdirs  # noqa: F401
    except ModuleNotFoundError:
        missing.append("platformdirs")

    if missing:
        print(
            "ERROR: the lookup functionality requires additional dependencies.",
            file=sys.stderr,
        )
        print(
            "Please install with: pip install 'intersphinx_registry[cli]'",
            file=sys.stderr,
        )
        print(f"Missing dependencies: {', '.join(missing)}", file=sys.stderr)
        return False

    return True
