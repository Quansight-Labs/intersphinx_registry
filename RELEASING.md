# Releasing

Releases are published to PyPI as `intersphinx_registry`, triggered by pushing a
git tag. Versions are calendar-based: `0.YYMM.D` (for example `0.2608.26` for
2026-08-26). The version lives only in `intersphinx_registry/__init__.py`
(`version_info`); flit reads it from there.

## Prerequisites

- You are on `main`, up to date with `origin/main`, with a clean working tree.
- GNU sed is installed as `gsed` (`brew install gnu-sed` on macOS). `bump_version.sh`
  calls `gsed` and will fail if it is missing.
- No tag for today's version exists yet (`git tag -l '0.2608.26'`). Only one
  release per day is possible with this scheme; a second one the same day
  needs a different approach.

## Steps (manual)

```bash
git checkout main
git pull --ff-only origin main
./bump_version.sh                       # rewrites version_info, commits "release X", tags X (annotated)
git push origin main                    # pushes the release commit
git push origin "$(git describe --tags --abbrev=0)"   # pushes the tag, which triggers publish
```

`git push --follow-tags` only sends annotated tags, so the script uses `git tag -a`.
Lightweight tags (`git tag X`) are silently skipped by `--follow-tags`, which likely
explains why the existing tags never triggered a publish. Check with `git cat-file -t X`; it should print `tag`.

Pushing the tag triggers `.github/workflows/publish.yml` ("CD"), which builds the
package with `python -m build` and uploads it to PyPI through trusted publishing
(the `pypi` GitHub environment).

Then:

1. Watch the "CD" run in GitHub Actions and confirm it succeeded.
2. Check the new version on https://pypi.org/project/intersphinx_registry/.
3. Smoke test: `pip install -U intersphinx_registry && intersphinx-registry --version`.

To undo a bad tag before it is published, delete it locally and on the remote
(`git tag -d X && git push origin :refs/tags/X`), then revert the release
commit. If it was already published to PyPI, it cannot be re-uploaded under the
same version; release a new one instead.

## Work in progress: `release.yml`

`.github/workflows/release.yml` (a `workflow_dispatch` button in GitHub Actions)
is meant to automate the bump, commit, tag and publish steps above. **It is not
committed yet and is not known to work.** Before using it, fix:

- `publish.yml` has only a `push: tags` trigger, but `release.yml` calls it with
  `uses:` and passes `with: ref:`. That needs a `workflow_call` trigger with a
  `ref` input, and its checkout step must use that ref. Otherwise it publishes
  the pre-bump commit.
- `bump_version.sh` runs on `ubuntu-latest`, which has no `gsed`. Use `sed` on
  Linux or install `gnu-sed` in the job.
- Tags pushed with the default `GITHUB_TOKEN` do not trigger other workflows, so
  the `push: tags` trigger will not fire from `release.yml`. The `workflow_call`
  path above avoids this; a PAT or GitHub App token would be needed otherwise.
- The `pypi` environment URL in `publish.yml` has a typo (`inersphinx_registry`).

Until those are fixed, use the manual steps above.
