import argparse
import sys

from intersphinx_registry import __version__
from intersphinx_registry.lookup import clear_cache, lookup_packages, print_info
from intersphinx_registry.reverse_lookup import reverse_lookup
from intersphinx_registry.rev_search import rev_search
from intersphinx_registry.utils import _are_dependencies_available


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
        epilog="Examples:\n"
        "  intersphinx-registry reverse-lookup https://numpy.org/doc/stable/reference/arrays.html\n"
        "  intersphinx-registry reverse-lookup https://docs.python.org/3/ https://numpy.org/doc/stable/",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    reverse_lookup_parser.add_argument(
        "urls",
        nargs="*",
        help="URLs to look up (space-separated)",
    )

    def _reverse_lookup_wrapper(args):
        if not args.urls:
            reverse_lookup_parser.print_help()
            sys.exit(0)
        reverse_lookup(args.urls)

    reverse_lookup_parser.set_defaults(func=_reverse_lookup_wrapper)

    rev_search_parser = subparsers.add_parser(
        "rev-search",
        help="Search .rst files for URLs that can be replaced with Sphinx references",
        description="Scan directory for .rst files and find URLs that can be replaced",
        epilog="Examples:\n"
        "  intersphinx-registry rev-search docs/\n"
        "  intersphinx-registry rev-search .",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    rev_search_parser.add_argument(
        "directory",
        help="Directory to search for .rst files",
    )
    rev_search_parser.set_defaults(func=lambda args: rev_search(args.directory))

    clear_cache_parser = subparsers.add_parser(
        "clear-cache",
        help="Clear the intersphinx inventory cache",
        description="Clear the cached intersphinx inventory files",
    )
    clear_cache_parser.set_defaults(func=lambda args: clear_cache())

    info_parser = subparsers.add_parser(
        "info",
        help="Display information about the intersphinx-registry installation",
        description="Show version, cache location, registry file location, and package count",
    )
    info_parser.set_defaults(func=lambda args: print_info())

    args = parser.parse_args()

    if args.subcommand is None:
        parser.print_help()
        sys.exit(0)

    args.func(args)


if __name__ == "__main__":
    main()
