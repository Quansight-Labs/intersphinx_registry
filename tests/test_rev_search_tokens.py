"""Tests for rev_search tokenization."""

import warnings

import pytest

from intersphinx_registry.rev_search import (
    Added,
    ReplacementContext,
    Removed,
    Unchanged,
    _compute_replacement,
    normalise_token_stream,
)
from intersphinx_registry.reverse_lookup import ReverseLookupResult


@pytest.mark.parametrize(
    "original,lookup_result,expected",
    [
        # Test case 1: Full link on its own line (no prefix in line, prefix in context_before)
        (
            ReplacementContext(
                "For more details, see the",
                "`setuptools documentation <https://setuptools.pypa.io/en/latest/setuptools.html>`__",
                "",
            ),
            ReverseLookupResult(
                "https://setuptools.pypa.io/en/latest/setuptools.html",
                "setuptools",
                "std:doc",
                "setuptools",
                None,
                "https://setuptools.pypa.io/en/latest/setuptools.html",
            ),
            (
                (
                    (Unchanged("For more details, see the"),),
                    (
                        Unchanged("`setuptools documentation <"),
                        Removed("https://setuptools.pypa.io/en/latest/setuptools.html"),
                        Unchanged(">`"),
                        Removed("__"),
                    ),
                    (Unchanged(""),),
                ),
                (
                    (Unchanged("For more details, see the"),),
                    (
                        Added(":std:doc:"),
                        Unchanged("`setuptools documentation <"),
                        Added("setuptools:setuptools"),
                        Unchanged(">`"),
                    ),
                    (Unchanged(""),),
                ),
            ),
        ),
        # Test case 2: Full link with prefix text in the same line
        (
            ReplacementContext(
                "",
                "For more details, see the `setuptools documentation <https://setuptools.pypa.io/en/latest/setuptools.html>`__",
                "",
            ),
            ReverseLookupResult(
                "https://setuptools.pypa.io/en/latest/setuptools.html",
                "setuptools",
                "std:doc",
                "setuptools",
                None,
                "https://setuptools.pypa.io/en/latest/setuptools.html",
            ),
            (
                (
                    (Unchanged(""),),
                    (
                        Unchanged(
                            "For more details, see the `setuptools documentation <"
                        ),
                        Removed("https://setuptools.pypa.io/en/latest/setuptools.html"),
                        Unchanged(">`"),
                        Removed("__"),
                    ),
                    (Unchanged(""),),
                ),
                (
                    (Unchanged(""),),
                    (
                        Unchanged("For more details, see the "),
                        Added(":std:doc:"),
                        Unchanged("`setuptools documentation <"),
                        Added("setuptools:setuptools"),
                        Unchanged(">`"),
                    ),
                    (Unchanged(""),),
                ),
            ),
        ),
        # Test case 3: Full link with suffix text
        (
            ReplacementContext(
                "",
                "`setuptools documentation <https://setuptools.pypa.io/en/latest/setuptools.html>`__ for details",
                "",
            ),
            ReverseLookupResult(
                "https://setuptools.pypa.io/en/latest/setuptools.html",
                "setuptools",
                "std:doc",
                "setuptools",
                None,
                "https://setuptools.pypa.io/en/latest/setuptools.html",
            ),
            (
                (
                    (Unchanged(""),),
                    (
                        Unchanged("`setuptools documentation <"),
                        Removed("https://setuptools.pypa.io/en/latest/setuptools.html"),
                        Unchanged(">`"),
                        Removed("__"),
                        Unchanged(" for details"),
                    ),
                    (Unchanged(""),),
                ),
                (
                    (Unchanged(""),),
                    (
                        Added(":std:doc:"),
                        Unchanged("`setuptools documentation <"),
                        Added("setuptools:setuptools"),
                        Unchanged(">` for details"),
                    ),
                    (Unchanged(""),),
                ),
            ),
        ),
        # Test case 4: Full link with both prefix and suffix
        (
            ReplacementContext(
                "",
                "See `setuptools documentation <https://setuptools.pypa.io/en/latest/setuptools.html>`__ for details",
                "",
            ),
            ReverseLookupResult(
                "https://setuptools.pypa.io/en/latest/setuptools.html",
                "setuptools",
                "std:doc",
                "setuptools",
                None,
                "https://setuptools.pypa.io/en/latest/setuptools.html",
            ),
            (
                (
                    (Unchanged(""),),
                    (
                        Unchanged("See `setuptools documentation <"),
                        Removed("https://setuptools.pypa.io/en/latest/setuptools.html"),
                        Unchanged(">`"),
                        Removed("__"),
                        Unchanged(" for details"),
                    ),
                    (Unchanged(""),),
                ),
                (
                    (Unchanged(""),),
                    (
                        Unchanged("See "),
                        Added(":std:doc:"),
                        Unchanged("`setuptools documentation <"),
                        Added("setuptools:setuptools"),
                        Unchanged(">` for details"),
                    ),
                    (Unchanged(""),),
                ),
            ),
        ),
    ],
    ids=[
        "link_only_line",
        "link_with_prefix_in_line",
        "link_with_suffix",
        "link_with_prefix_and_suffix",
    ],
)
def test_full_link_tokenization(original, lookup_result, expected):
    """Test that full link replacement tokenizes correctly."""
    context_old, context_new = _compute_replacement(original, lookup_result)
    expected_old, expected_new = expected

    # Check if expected is already normalized and warn if not
    exp_before_old, exp_target_old, exp_after_old = expected_old
    exp_before_new, exp_target_new, exp_after_new = expected_new

    if normalise_token_stream(exp_before_old) != exp_before_old:
        normalized = normalise_token_stream(exp_before_old)
        warnings.warn(
            f"expected_old context_before is not normalized.\n"
            f"  Original: {exp_before_old}\n"
            f"  Normalized: {normalized}",
            UserWarning,
        )
    if normalise_token_stream(exp_target_old) != exp_target_old:
        normalized = normalise_token_stream(exp_target_old)
        warnings.warn(
            f"expected_old target_line is not normalized.\n"
            f"  Original: {exp_target_old}\n"
            f"  Normalized: {normalized}",
            UserWarning,
        )
    if normalise_token_stream(exp_after_old) != exp_after_old:
        normalized = normalise_token_stream(exp_after_old)
        warnings.warn(
            f"expected_old context_after is not normalized.\n"
            f"  Original: {exp_after_old}\n"
            f"  Normalized: {normalized}",
            UserWarning,
        )
    if normalise_token_stream(exp_before_new) != exp_before_new:
        normalized = normalise_token_stream(exp_before_new)
        warnings.warn(
            f"expected_new context_before is not normalized.\n"
            f"  Original: {exp_before_new}\n"
            f"  Normalized: {normalized}",
            UserWarning,
        )
    if normalise_token_stream(exp_target_new) != exp_target_new:
        normalized = normalise_token_stream(exp_target_new)
        warnings.warn(
            f"expected_new target_line is not normalized.\n"
            f"  Original: {exp_target_new}\n"
            f"  Normalized: {normalized}",
            UserWarning,
        )
    if normalise_token_stream(exp_after_new) != exp_after_new:
        normalized = normalise_token_stream(exp_after_new)
        warnings.warn(
            f"expected_new context_after is not normalized.\n"
            f"  Original: {exp_after_new}\n"
            f"  Normalized: {normalized}",
            UserWarning,
        )

    # Normalize both actual and expected streams before comparing
    ctx_before_old, target_old, ctx_after_old = context_old
    ctx_before_new, target_new, ctx_after_new = context_new

    normalized_context_old = (
        normalise_token_stream(ctx_before_old),
        normalise_token_stream(target_old),
        normalise_token_stream(ctx_after_old),
    )
    normalized_context_new = (
        normalise_token_stream(ctx_before_new),
        normalise_token_stream(target_new),
        normalise_token_stream(ctx_after_new),
    )
    normalized_expected_old = (
        normalise_token_stream(exp_before_old),
        normalise_token_stream(exp_target_old),
        normalise_token_stream(exp_after_old),
    )
    normalized_expected_new = (
        normalise_token_stream(exp_before_new),
        normalise_token_stream(exp_target_new),
        normalise_token_stream(exp_after_new),
    )

    assert normalized_context_old == normalized_expected_old, "context_old mismatch"
    assert normalized_context_new == normalized_expected_new, "context_new mismatch"
