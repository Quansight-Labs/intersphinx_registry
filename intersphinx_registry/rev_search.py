import re
from pathlib import Path
from typing import Iterable, NamedTuple, Optional, Tuple, Union

from .reverse_lookup import ReverseLookupResult, _do_reverse_lookup
from .utils import _are_dependencies_available, _compress_user_path

# ANSI escape sequences
RED = "\033[31m"
RED_BG = "\033[41;37m"
GREEN = "\033[32m"
GREEN_BG = "\033[42;30m"
BLUE = "\033[34m"
CYAN = "\033[36m"
YELLOW = "\033[33m"
YELLOW_BG = "\033[43;30m"
RESET = "\033[0m"


class Unchanged(str):
    """Token representing unchanged text."""


class Removed(str):
    """Token representing removed text."""


class Added(str):
    """Token representing added text."""


Token = Union[Unchanged, Removed, Added]

# OutputReplacementContext: tuple of three token sequences
# (context_before_tokens, target_line_tokens, context_after_tokens)
OutputReplacementContext = Tuple[
    Tuple[Token, ...],
    Tuple[Token, ...],
    Tuple[Token, ...],
]


def normalise_token_stream(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    """
    Normalize a token stream by:
    1. Filtering out empty tokens
    2. Merging consecutive tokens of the same type

    This is useful for comparing token streams that are semantically
    equivalent but may have different tokenization.
    """
    if not tokens:
        return (Unchanged(""),)

    normalized = []
    current_type = None
    current_content = ""

    for token in tokens:
        if not str(token):
            continue

        token_type = type(token)

        if token_type == current_type:
            current_content += str(token)
        else:
            if current_type is not None:
                normalized.append(current_type(current_content))
            current_type = token_type
            current_content = str(token)

    if current_type is not None:
        normalized.append(current_type(current_content))

    if not normalized:
        return (Unchanged(""),)

    return tuple(normalized)


def _make_line_tokens(
    line: str,
    start: int,
    end: int,
    old_text: str,
    new_text: str,
) -> tuple[tuple[Token, ...], tuple[Token, ...]]:
    """
    Build old and new token lists for a line where text is replaced.

    Returns (old_tokens, new_tokens) where:
    - old_tokens: [Unchanged(prefix), Removed(old_text), Unchanged(suffix)]
    - new_tokens: [Unchanged(prefix), Added(new_text), Unchanged(suffix)]
    """
    old_tokens: list[Token] = []
    new_tokens: list[Token] = []

    if start > 0:
        prefix = Unchanged(line[:start])
        old_tokens.append(prefix)
        new_tokens.append(prefix)

    old_tokens.append(Removed(old_text))
    new_tokens.append(Added(new_text))

    if end < len(line):
        suffix = Unchanged(line[end:])
        old_tokens.append(suffix)
        new_tokens.append(suffix)

    return tuple(old_tokens), tuple(new_tokens)


class UrlReplacement(NamedTuple):
    """
    Information about a URL replacement in an RST file.

    Attributes
    ----------
    line_num : int
        Line number where the URL was found
    matched_url : str
        The URL that was matched in the text and replaced
    context_old : OutputReplacementContext
        The old context (before replacement) with tokenized (context_before_tokens, target_line_tokens, context_after_tokens)
    context_new : OutputReplacementContext
        The new context (after replacement) with tokenized (context_before_tokens, target_line_tokens, context_after_tokens)
    inventory_url : Optional[str]
        The inventory URL used for the lookup, or None
    """

    line_num: int
    matched_url: str
    context_old: OutputReplacementContext
    context_new: OutputReplacementContext
    inventory_url: Optional[str]


class ReplacementContext(NamedTuple):
    """
    Context for a replacement operation.

    Attributes
    ----------
    context_before : str
        The context line before the target line. Empty string if there is no context before.
    target_line : str
        The target line to be replaced.
    context_after : str
        The context line after the target line. Empty string if there is no context after.
    """

    context_before: str
    target_line: str
    context_after: str


def _normalize_replacement(
    context_old: OutputReplacementContext,
    context_new: OutputReplacementContext,
) -> tuple[OutputReplacementContext, OutputReplacementContext]:
    """Normalize token streams in both contexts."""
    ctx_before_old, target_old, ctx_after_old = context_old
    ctx_before_new, target_new, ctx_after_new = context_new

    normalized_old = (
        normalise_token_stream(ctx_before_old),
        normalise_token_stream(target_old),
        normalise_token_stream(ctx_after_old),
    )
    normalized_new = (
        normalise_token_stream(ctx_before_new),
        normalise_token_stream(target_new),
        normalise_token_stream(ctx_after_new),
    )
    return normalized_old, normalized_new


def _make_replacement(
    context_before: str,
    context_after: str,
    target_tokens_old: tuple[Token, ...],
    target_tokens_new: tuple[Token, ...],
) -> tuple[OutputReplacementContext, OutputReplacementContext]:
    """Build normalized replacement contexts with unchanged context lines."""
    ctx = (Unchanged(context_before),), (Unchanged(context_after),)
    context_old: OutputReplacementContext = (ctx[0], target_tokens_old, ctx[1])
    context_new: OutputReplacementContext = (ctx[0], target_tokens_new, ctx[1])
    return _normalize_replacement(context_old, context_new)


# TODO:
# I'm pretty sure instead of having a before[Unchange|Removed] and after[Unchanged|added]
# we can have a single diff[Unchange|Removed|added] but I't more complicated to code.
# so if you think you can do it, please feel free.
# we can likely properly find the index of URL(s), backticks and everything,
# split and do the replacement on the token stream/
def _compute_full_link_replacement(
    original_line: str,
    context_before_str: str,
    context_after_str: str,
    lookup_result: ReverseLookupResult,
    target: str,
) -> Optional[tuple[OutputReplacementContext, OutputReplacementContext]]:
    """
    Handle full RST link replacement.

    Handles cases like:
    - `` `setuptools documentation <https://setuptools.pypa.io/en/latest/setuptools.html>`__ ``
    - `` `link text <URL>`_ ``
    - `` See `link text <URL>`__ for details ``

    Returns None if the pattern doesn't match.
    """
    full_link_match = re.search(
        r"`([^`<>]+)\s*<" + re.escape(lookup_result.url) + r"[.,;:!?)]*>`__?",
        original_line,
    )
    if not full_link_match:
        return None

    link_text = full_link_match.group(1).strip()
    original_text = full_link_match.group(0)
    start_idx = full_link_match.start()
    end_idx = full_link_match.end()
    domain_prefix = f":{lookup_result.domain}:"

    # Find where the URL is within the matched link text
    url_match_in_link = re.search(
        r"<" + re.escape(lookup_result.url) + r"[.,;:!?)]*>", original_text
    )

    old_tokens: list[Token] = []
    new_tokens: list[Token] = []

    # Add prefix (text before the link)
    if start_idx > 0:
        prefix = Unchanged(original_line[:start_idx])
        old_tokens.append(prefix)
        new_tokens.append(prefix)

    if url_match_in_link:
        # Fine-grained diff: show URL replacement within the link structure
        url_start = url_match_in_link.start()
        url_end = url_match_in_link.end()

        space_before = (
            " " if url_start > 0 and original_text[url_start - 1] == " " else ""
        )

        # Old: `link text <URL>`_  (show parts around URL as unchanged)
        old_tokens.append(
            Unchanged(original_text[: url_start + 1])
        )  # up to and including <
        old_tokens.append(
            Removed(original_text[url_start + 1 : url_end - 1])
        )  # URL only
        old_tokens.append(Unchanged(original_text[url_end - 1 : url_end]))  # >

        # Handle trailing backtick and underscores
        after_angle = original_text[url_end:]
        if after_angle.startswith("`"):
            old_tokens.append(Unchanged(after_angle[0]))  # `
            if len(after_angle) > 1:
                old_tokens.append(Removed(after_angle[1:]))  # underscores
        else:
            old_tokens.append(Removed(after_angle))

        # New: :domain:`link text <target>`
        new_tokens.append(Added(domain_prefix))
        new_tokens.append(Unchanged("`" + link_text + space_before + "<"))
        new_tokens.append(Added(target))
        new_tokens.append(Unchanged(">`"))
    else:
        # Simple replacement: whole link becomes role reference
        old_tokens.append(Removed(original_text))
        new_tokens.append(Added(domain_prefix))
        new_tokens.append(Unchanged("`" + link_text))
        new_tokens.append(Added(f" <{target}>`"))

    # Add suffix (text after the link)
    if end_idx < len(original_line):
        suffix = Unchanged(original_line[end_idx:])
        old_tokens.append(suffix)
        new_tokens.append(suffix)

    return _make_replacement(
        context_before_str, context_after_str, tuple(old_tokens), tuple(new_tokens)
    )


def _compute_simple_link_replacement(
    original_line: str,
    context_before_str: str,
    context_after_str: str,
    lookup_result: ReverseLookupResult,
    target: str,
    rst_ref: str,
) -> Optional[tuple[OutputReplacementContext, OutputReplacementContext]]:
    """
    Handle simple RST link replacement (may span multiple lines).

    Handles cases like:
    - `` `<https://docs.python.org/3/library/os.html>`_ ``
    - `` `<https://docs.python.org/3/library/os.html>`__ ``
    - Multi-line: context_before has `` `link text ``, target_line has `` <URL>`_ ``

    Returns None if the pattern doesn't match.
    """
    simple_link_match = re.search(
        r"`?<" + re.escape(lookup_result.url) + r"[.,;:!?)]*>`__?", original_line
    )
    if not simple_link_match:
        return None

    original_text = simple_link_match.group(0)
    start_idx = simple_link_match.start()
    end_idx = simple_link_match.end()

    # Check if link text is on the previous line (multi-line case)
    link_text_match = re.search(r"`([^`]+)$", context_before_str)
    if link_text_match:
        link_text = link_text_match.group(1).strip()

        # Build context_before tokens (with changes)
        ctx_old, ctx_new = _make_line_tokens(
            context_before_str,
            link_text_match.start(),
            link_text_match.end(),
            context_before_str[link_text_match.start() : link_text_match.end()],
            f":{lookup_result.domain}:`{link_text}",
        )

        # Build target line tokens
        target_old, target_new = _make_line_tokens(
            original_line, start_idx, end_idx, original_text, f"<{target}>`"
        )

        ctx_after = (Unchanged(context_after_str),)
        context_old: OutputReplacementContext = (ctx_old, target_old, ctx_after)
        context_new: OutputReplacementContext = (ctx_new, target_new, ctx_after)
        return _normalize_replacement(context_old, context_new)

    # Simple case: just replace the link on the target line
    old_tokens, new_tokens = _make_line_tokens(
        original_line, start_idx, end_idx, original_text, rst_ref
    )
    return _make_replacement(
        context_before_str, context_after_str, old_tokens, new_tokens
    )


def _compute_url_replacement(
    original_line: str,
    context_before_str: str,
    context_after_str: str,
    lookup_result: ReverseLookupResult,
    rst_ref: str,
) -> tuple[OutputReplacementContext, OutputReplacementContext]:
    """
    Handle plain URL replacement in text.

    Handles cases like:
    - `` See https://docs.python.org/3/library/os.html for details ``
    - `` Check https://docs.python.org/3/library/os.html. ``
    - `` https://docs.python.org/3/library/os.html is the documentation ``

    This is the fallback case when no RST link pattern matches.
    """
    url_match = re.search(re.escape(lookup_result.url) + r"[.,;:!?)]*", original_line)
    if url_match:
        old_tokens, new_tokens = _make_line_tokens(
            original_line,
            url_match.start(),
            url_match.end(),
            lookup_result.url,
            rst_ref,
        )
    else:
        old_tokens = (Removed(original_line),)
        new_tokens = (Added(rst_ref),)

    return _make_replacement(
        context_before_str, context_after_str, old_tokens, new_tokens
    )


def _compute_replacement(
    original: ReplacementContext,
    lookup_result: ReverseLookupResult,
) -> tuple[OutputReplacementContext, OutputReplacementContext]:
    """
    Compute the replacement line(s) for a URL in an RST file.

    Tries patterns in order: full RST link, simple link, plain URL.
    Returns (context_old, context_new) tuple of normalized token streams.
    """
    target = f"{lookup_result.package}:{lookup_result.rst_entry}"
    rst_ref = f":{lookup_result.domain}:`{target}`"
    ctx_before, line, ctx_after = original

    result = _compute_full_link_replacement(
        line, ctx_before, ctx_after, lookup_result, target
    )
    if result is not None:
        return result

    result = _compute_simple_link_replacement(
        line, ctx_before, ctx_after, lookup_result, target, rst_ref
    )
    if result is not None:
        return result

    return _compute_url_replacement(line, ctx_before, ctx_after, lookup_result, rst_ref)


def process_one_file(rst_file: Path):
    """
    Process a single RST file to find URLs that can be replaced with Sphinx references.

    Yields UrlReplacement objects for each URL found that has a corresponding
    inventory entry. Files are read, URLs are extracted and looked up, and
    replacements are computed with token-based diffs.

    Parameters
    ----------
    rst_file : Path
        Path to the RST file to process

    Yields
    ------
    UrlReplacement
        Information about each URL replacement found in the file
    """
    url_pattern = re.compile(r'https?://[^\s<>"{}|\\^`\[\]]+')
    url_locations: dict[str, list[tuple[int, str]]] = {}
    all_lines = []

    try:
        with open(rst_file, "r", encoding="utf-8") as f:
            all_lines = f.readlines()
            for line_num, line in enumerate(all_lines, start=1):
                urls = url_pattern.findall(line)
                for url in urls:
                    url = url.rstrip(".,;:!?)")
                    url_locations.setdefault(url, []).append((line_num, line.rstrip()))
    except Exception:
        return

    if not url_locations:
        return

    urls = list(url_locations.keys())
    results = _do_reverse_lookup(urls)

    replaceable = [
        (result, url_locations[result.url])
        for result in results
        if result.package is not None
    ]

    if not replaceable:
        return

    for lookup_result, line_infos in replaceable:
        for line_num, original_line in line_infos:
            context_before = all_lines[line_num - 2].rstrip() if line_num > 1 else ""
            context_after = (
                all_lines[line_num].rstrip() if line_num < len(all_lines) else ""
            )

            if lookup_result.rst_entry is not None:
                context_old, context_new = _compute_replacement(
                    ReplacementContext(context_before, original_line, context_after),
                    lookup_result,
                )
                yield UrlReplacement(
                    line_num,
                    lookup_result.url,
                    context_old,
                    context_new,
                    lookup_result.inventory_url,
                )
            else:
                # No replacement available - create empty contexts
                empty_context: OutputReplacementContext = (
                    (Unchanged(context_before),),
                    (Unchanged(original_line),),
                    (Unchanged(context_after),),
                )
                yield UrlReplacement(
                    line_num,
                    lookup_result.url,
                    empty_context,
                    empty_context,
                    lookup_result.inventory_url,
                )


def format_tokens(
    tokens: Tuple[Token, ...],
    prefix: str = "",
    defaultFG: str = "",
    AddedHighlight: str = "",
    RemovedHighlight: str = "",
) -> str:
    """
    Format tokens with appropriate colors.

    Parameters
    ----------
    tokens : Tuple[Token, ...]
        Sequence of tokens to format
    prefix : str
        Prefix to add before the tokens (e.g., "     - " or "       ")
    defaultFG : str
        Default foreground color for the line (e.g., RED, GREEN, BLUE). Empty string for no color.
    AddedHighlight : str
        Highlight style for Added tokens (e.g., GREEN_BG for background). Empty string for no highlight.
    RemovedHighlight : str
        Highlight style for Removed tokens (e.g., RED_BG for background). Empty string for no highlight.

    Returns
    -------
    str
        Formatted string with ANSI color codes
    """
    if not tokens:
        return ""

    output = ""
    # Add prefix with defaultFG color
    output += defaultFG + prefix + RESET + defaultFG

    for token in tokens:
        if isinstance(token, Added):
            output += f"{AddedHighlight}{str(token)}{RESET}{defaultFG}"
        elif isinstance(token, Removed):
            output += f"{RemovedHighlight}{str(token)}{RESET}{defaultFG}"
        else:  # Unchanged
            output += str(token)

    output += RESET

    return output


def rev_search(directory: str) -> None:
    """
    Search for URLs in .rst files that can be replaced with Sphinx references.

    Parameters
    ----------
    directory : str
        Path to a directory to search for .rst files, or a single .rst file path
    """
    if not _are_dependencies_available():
        return

    directory_path = Path(directory)
    if directory_path.is_file():
        rst_files: Iterable[Path] = (
            [directory_path] if directory_path.suffix == ".rst" else []
        )
    else:
        rst_files = directory_path.rglob("*.rst")

    for rst_file in rst_files:
        search_one_file(rst_file)


def search_one_file(rst_file: Path) -> None:
    """
    Search a single RST file and print formatted diffs for replaceable URLs.

    Processes the file to find replaceable URLs and prints a formatted diff
    showing the original and replacement text with color-coded token highlights.

    Parameters
    ----------
    rst_file : Path
        Path to the RST file to search and display results for
    """
    display_path = _compress_user_path(str(rst_file))
    for replacement in process_one_file(rst_file):
        print(f"{CYAN}{display_path}:{replacement.line_num}{RESET}")

        if replacement.context_old == replacement.context_new:
            ctx_before_tokens_old, target_tokens_old, ctx_after_tokens_old = (
                replacement.context_old
            )

            if ctx_before_tokens_old:
                print(format_tokens(ctx_before_tokens_old, "       "))

            print(format_tokens(target_tokens_old, "     ? ", defaultFG=BLUE))

            if ctx_after_tokens_old:
                print(format_tokens(ctx_after_tokens_old, "       "))

            print()
            continue

        ctx_before_tokens_old, target_tokens_old, ctx_after_tokens_old = (
            replacement.context_old
        )
        ctx_before_tokens_new, target_tokens_new, ctx_after_tokens_new = (
            replacement.context_new
        )

        if ctx_before_tokens_old or ctx_before_tokens_new:
            if ctx_before_tokens_old != ctx_before_tokens_new:
                print(
                    format_tokens(
                        ctx_before_tokens_old,
                        "     - ",
                        defaultFG=RED,
                        RemovedHighlight=RED_BG,
                    )
                )
            else:
                print(format_tokens(ctx_before_tokens_old, "       "))
        print(
            format_tokens(
                target_tokens_old, "     - ", defaultFG=RED, RemovedHighlight=RED_BG
            )
        )

        if replacement.inventory_url:
            old_text = "".join(
                str(token)
                for token in target_tokens_old
                if not isinstance(token, Added)
            )
            if replacement.inventory_url not in old_text:
                https_pos = old_text.find("https://")
                if https_pos >= 0:
                    spaces = " " * (7 + https_pos)
                else:
                    spaces = "       "

                matched_url = replacement.matched_url
                inventory_url = replacement.inventory_url

                prefix_len = 0
                while (
                    prefix_len < len(matched_url)
                    and prefix_len < len(inventory_url)
                    and matched_url[prefix_len] == inventory_url[prefix_len]
                ):
                    prefix_len += 1

                suffix_len = 0
                while (
                    suffix_len < len(matched_url) - prefix_len
                    and suffix_len < len(inventory_url) - prefix_len
                    and matched_url[-(suffix_len + 1)]
                    == inventory_url[-(suffix_len + 1)]
                ):
                    suffix_len += 1

                if prefix_len > 0 or suffix_len > 0:
                    prefix = inventory_url[:prefix_len]
                    middle = (
                        inventory_url[prefix_len : len(inventory_url) - suffix_len]
                        if suffix_len > 0
                        else inventory_url[prefix_len:]
                    )
                    suffix = inventory_url[-suffix_len:] if suffix_len > 0 else ""
                    highlighted_url = f"{YELLOW}{prefix}{YELLOW_BG}{middle}{RESET}{YELLOW}{suffix}{RESET}"
                else:
                    highlighted_url = f"{YELLOW_BG}{inventory_url}{RESET}"

                print(f"{spaces}{highlighted_url}")

        if ctx_before_tokens_old or ctx_before_tokens_new:
            if ctx_before_tokens_old != ctx_before_tokens_new:
                print(
                    format_tokens(
                        ctx_before_tokens_new,
                        "     + ",
                        defaultFG=GREEN,
                        AddedHighlight=GREEN_BG,
                        RemovedHighlight=RED_BG,
                    )
                )
        print(
            format_tokens(
                target_tokens_new,
                "     + ",
                defaultFG=GREEN,
                AddedHighlight=GREEN_BG,
                RemovedHighlight=RED_BG,
            )
        )

        if ctx_after_tokens_old or ctx_after_tokens_new:
            if ctx_after_tokens_old != ctx_after_tokens_new:
                print(
                    format_tokens(
                        ctx_after_tokens_old,
                        "     - ",
                        defaultFG=RED,
                        RemovedHighlight=RED_BG,
                    )
                )
                print(
                    format_tokens(
                        ctx_after_tokens_new,
                        "     + ",
                        defaultFG=GREEN,
                        AddedHighlight=GREEN_BG,
                        RemovedHighlight=RED_BG,
                    )
                )
            else:
                print(format_tokens(ctx_after_tokens_old, "       "))

        print()
