#!/usr/bin/env bash
set -euo pipefail

YEAR=$(date +%y)
MONTH=$(date +%m)
DAY=$(date +%d)

# Strip leading zeros so the tuple stays PEP 440-compliant
YYMM="${YEAR}${MONTH}"
DAY_NUM=$((10#$DAY))

NEW_VERSION="0.${YYMM}.${DAY_NUM}"
NEW_TUPLE="(0, ${YYMM}, ${DAY_NUM})"

INIT_FILE="intersphinx_registry/__init__.py"

# Replace the version_info tuple in __init__.py
gsed -i "s/^version_info = (.*/version_info = ${NEW_TUPLE}/" "$INIT_FILE"

echo "Version bumped to ${NEW_VERSION}"

git add "$INIT_FILE"
git commit -m "release ${NEW_VERSION}"
git tag "${NEW_VERSION}"

echo "Committed and tagged ${NEW_VERSION}"
