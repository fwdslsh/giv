---
description: GitHub and CI/CD specialist with vast experince in managing open source project on GitHub.
applyTo: "**/*.*"
---
# GitHub Copilot Release Instructions for giv

To create a new release for the giv CLI using GitHub Actions, follow these steps:

## 1. Bump the Version
- Open `pyproject.toml`.
- Update the `version` field under `[tool.poetry]` to the new release version (e.g., `0.5.7`).

## 2. Commit the Change
- Stage and commit all pending changes:
  ```bash
  git add .
  git commit -m "chore: bump version to <new-version>"
  ```

## 3. Tag the Release
- Create a new annotated tag for the release:
  ```bash
  git tag v<new-version>
  ```

## 4. Push to Remote
- Push the commit and tag to the remote repository:
  ```bash
  git push origin main --tags
  ```

## 5. Trigger the Release Workflow
- The GitHub Actions workflow `.github/workflows/release.yml` will automatically run when a new tag matching `v*` is pushed.
- The workflow will build binaries, create PyPI packages, and publish the release.

## 6. Verify the Release
- Check the Actions tab for workflow status.
- Confirm the new release appears under the Releases tab.
- Verify that binaries and PyPI packages are published as expected.

---

**Note:** Ensure your `PYPI_API_TOKEN` secret is set in the repository for PyPI publishing.
