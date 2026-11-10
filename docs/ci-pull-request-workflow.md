# AdamShell CI and Pull Request Workflow

## Purpose

Protect the main branch by validating proposed changes
through GitHub Actions before merging.

## Current CI

- Workflow: AdamShell CI
- Runner: windows-latest
- Python: 3.12.10
- Test dependency: pytest==9.1.1
- Command: python -B -m pytest -q
- Check: Full regression / Windows / Python 3.12.10

## Development workflow

1. Start from an up-to-date main branch.
2. Create a dedicated feature branch.
3. Make and locally verify the intended changes.
4. Commit and push the feature branch.
5. Open a pull request targeting main.
6. Verify the GitHub Actions regression result.
7. Merge only after successful checks and review.
8. Fast-forward the local main branch after merging.

## Protection rollout

This document is part of a pilot.

Branch protection and required checks are not
enabled by this documentation change.

Protection must be configured separately after
the pull request workflow has been validated.

Do not merge this pilot before its CI result
has been reviewed.
