import argparse
import sys
from intersphinx_registry import __version__


def lookup_command(args):
    from intersphinx_registry.lookup import _are_dependencies_available, lookup_packages

    if not _are_dependencies_available():
        sys.exit(1)

    if not args.packages:
        print("Usage: intersphinx-registry lookup <package>[,package] [search_term]")
        print()
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

    args = parser.parse_args()

    if args.subcommand is None:
        parser.print_help()
        sys.exit(0)

    args.func(args)


if __name__ == "__main__":
    main()
