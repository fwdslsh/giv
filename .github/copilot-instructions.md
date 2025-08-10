# GitHub Copilot Instructions for giv CLI

## Project Overview
**giv** is an AI-powered Git history assistant that generates commit messages, changelogs, release notes, and announcements. It is implemented in Python and distributed as cross-platform binaries with zero runtime dependencies.

## Architecture & Key Patterns

### Command System (commands)
- All commands inherit from `BaseCommand`.
- Use `argparse.Namespace` + `ConfigManager` in constructors.
- Override `customize_context()` to modify template variables.
- Override `handle_output()` to customize file writing.
- Commands auto-discover templates via `template_name` attribute.
- Example: `MessageCommand` uses `TEMPLATE_MESSAGE = "commit_message_prompt.md"`.

### Configuration Hierarchy (config.py)
- Precedence: project config > user `~/.giv/config` > environment variables (`GIV_` prefix, dot-notation).
- Access merged config via `ConfigManager.get(key)`.

### Template System (templates.py)
- Templates from: `giv/templates/*.md`, templates, `~/.giv/templates/`.
- Variables: `{VARIABLE}` syntax, rendered with `TemplateEngine.render_template_file()`.

### Git Integration (git.py)
- `GitRepository` provides: `get_diff()`, `build_history_metadata()`, `get_commits()`.

## Developer Workflows

### Build & Test
- Install: `poetry install`
- Run all tests: `poetry run pytest`
- Unit tests: `poetry run pytest -m unit`
- Integration tests: `poetry run pytest -m integration`
- Compatibility tests: `poetry run pytest -m compatibility`
- Lint/format: `poetry run black giv/ tests/`, `poetry run flake8 giv/ tests/`, `poetry run mypy giv/`
- Build binaries: `poetry run build-binary`

### Release & Distribution
- Automated via GitHub Actions on new tags.
- Binaries and PyPI packages attached to releases.
- Manual build: build_binary.py (PyInstaller).

## Project-Specific Conventions

### Error Handling (errors.py)
- Use custom exceptions:
  - `TemplateError` → exit code 2
  - `GitError` → exit code 3
  - `ConfigError` → exit code 4
  - `APIError` → exit code 5

### LLM Integration (llm.py)
- `LLMClient` supports OpenAI, Ollama, and custom endpoints.

### Output Management (output.py)
- `write_output()` modes: `auto`, `append`, `prepend`, `update`, `overwrite`.

### Cross-Platform Testing
- Mocking for path, encoding, and config differences.
- Use `unittest.mock.patch.object()` for platform-specific tests.

## Integration Points

### Adding New Commands
1. Create `giv/commands/new_command.py` (inherits `BaseCommand`)
2. Register in __init__.py and cli.py
3. Add template constant to constants.py
4. Create template in templates
5. Add tests in test_commands_integration.py

### Template Development
- Context variables: `{DIFF}`, `{VERSION}`, `{COMMIT_ID}`, `{DATE}`, `{AUTHOR}`, `{TODOS}`
- Validate with `TemplateEngine.validate_template()`

## Quick Examples

- Initialize: `giv init`
- Generate commit message: `giv message`
- Changelog: `giv changelog v1.0.0..HEAD`
- Release notes: `giv release-notes v1.2.0..HEAD`
