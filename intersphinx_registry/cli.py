import argparse
import sys

from intersphinx_registry import __version__
from intersphinx_registry.lookup import (
    _are_dependencies_available,
    lookup_packages,
    reverse_lookup,
    clear_cache,
)


def lookup_command(args):
    if not _are_dependencies_available():
        sys.exit(1)

    if not args.packages:
        print("Usage: intersphinx-registry lookup <package>[,package] [search_term]\n")
        print("Examples:")
        print("  intersphinx-registry lookup numpy,scipy array")
        print("  intersphinx-registry lookup ipython formatters.html")
        sys.exit(0)

    lookup_packages(args.packages, args.search_term)


def reverse_lookup_command(args):
    if not args.urls:
        print("Usage: intersphinx-registry reverse-lookup <url> [url ...]\n")
        print("Examples:")
        print("  intersphinx-registry reverse-lookup https://numpy.org/doc/stable/reference/arrays.html")
        print("  intersphinx-registry reverse-lookup https://docs.python.org/3/ https://numpy.org/doc/stable/")
        sys.exit(0)

    reverse_lookup(args.urls)


def clear_cache_command(args):
    clear_cache()


def main():
    parser = argparse.ArgumentParser(
        prog="intersphinx-registry",
        description="Default intersphinx mapping for the Python ecosystem",
        epilog="For more information, see: https://github.com/Quansight-labs/intersphinx_registry",
    )

    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"intersphinx-registry {__version__}",
    )

    subparsers = parser.add_subparsers(
        title="subcommands",
        description="available subcommands",
        dest="subcommand",
        help="subcommand help",
    )

    # Lookup subcommand
    lookup_parser = subparsers.add_parser(
        "lookup",
        help="Search and lookup intersphinx targets/webpages",
        description="Search intersphinx inventories for documentation targets",
    )
    lookup_parser.add_argument(
        "packages",
        nargs="?",
        default=None,
        help="Comma-separated list of package names (e.g., numpy,scipy)",
    )
    lookup_parser.add_argument(
        "search_term",
        nargs="?",
        default=None,
        help="Optional search term to filter results",
    )
    lookup_parser.set_defaults(func=lookup_command)

    reverse_lookup_parser = subparsers.add_parser(
        "reverse-lookup",
        help="Find which packages documentation URLs belong to",
        description="Given URLs, find which packages they come from",
    )
    reverse_lookup_parser.add_argument(
        "urls",
        nargs="*",
        default=None,
        help="URLs to look up (space-separated)",
    )
    reverse_lookup_parser.set_defaults(func=reverse_lookup_command)

    rev_parser = subparsers.add_parser(
        "rev",
        help="Alias for reverse-lookup",
        description="Given URLs, find which packages they come from",
    )
    rev_parser.add_argument(
        "urls",
        nargs="*",
        default=None,
        help="URLs to look up (space-separated)",
    )
    rev_parser.set_defaults(func=reverse_lookup_command)

    clear_cache_parser = subparsers.add_parser(
        "clear-cache",
        help="Clear the intersphinx inventory cache",
        description="Clear the cached intersphinx inventory files",
    )
    clear_cache_parser.set_defaults(func=clear_cache_command)

    args = parser.parse_args()

    if args.subcommand is None:
        parser.print_help()
        sys.exit(0)

    args.func(args)


if __name__ == "__main__":
    main()
