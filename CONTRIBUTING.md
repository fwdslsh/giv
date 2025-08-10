# Contributing to GIV CLI

Thank you for your interest in contributing to **giv**! This document provides guidelines and information to help you contribute effectively to the project.

## 🚀 Quick Start

1. **Fork** the repository on GitHub
2. **Clone** your fork locally
3. **Install** dependencies: `poetry install`
4. **Create** a feature branch: `git checkout -b feature/my-feature`
5. **Make** your changes and test them
6. **Submit** a pull request

## 📋 Development Setup

### Prerequisites

- **Python 3.9+** - Required for development
- **Poetry** - Dependency management (`pip install poetry`)
- **Git** - Version control

### Local Environment Setup

```bash
# Clone your fork
git clone https://github.com/your-username/giv.git
cd giv

# Install dependencies
poetry install

# Activate virtual environment
poetry shell

# Verify installation
poetry run giv --version
```

## 🧪 Testing

We maintain comprehensive test coverage. Always run tests before submitting changes:

```bash
# Run all tests
poetry run pytest

# Run specific test categories
poetry run pytest -m unit           # Unit tests only
poetry run pytest -m integration    # Integration tests only
poetry run pytest -m compatibility  # Compatibility tests only

# Run with coverage
poetry run pytest --cov=giv --cov-report=html
```

### Writing Tests

- **Unit tests**: Test individual functions and classes
- **Integration tests**: Test command-line interface and workflows
- **Compatibility tests**: Test cross-platform functionality

## 🎯 Contribution Areas

### High Priority (Help Needed!)

- **Documentation improvements**: API docs, workflow examples, custom prompt guides
- **Testing enhancements**: Real-world scenarios, performance benchmarking
- **Template system**: New template variables and customization options

### Medium Priority

- **Content generation**: Git user integration, README integration, enhanced TODO processing
- **User experience**: Interactive modes, better error messages, output formatting
- **Template enhancements**: Rules files, example extraction, sample content tokens

### Looking Ahead

- **Advanced features**: AI-powered help, chat interfaces, LLM-powered review
- **New document types**: README generation, license management
- **Performance**: Large repository support, caching improvements

See our [roadmap](docs/roadmap.md) for a complete list of planned features.

## 📝 Coding Standards

### Code Style

We use automated formatting and linting:

```bash
# Format code
poetry run black giv/ tests/

# Lint code
poetry run flake8 giv/ tests/

# Type checking
poetry run mypy giv/ tests/
```

### Code Quality Guidelines

- **Clear naming**: Use descriptive variable and function names
- **Documentation**: Add docstrings for public functions and classes
- **Error handling**: Implement appropriate error handling and user-friendly messages
- **Type hints**: Use type hints for function parameters and return values

### Architecture Patterns

- **Commands**: Inherit from `BaseCommand`, use `customize_context()` and `handle_output()`
- **Configuration**: Use `ConfigManager` for settings with proper precedence
- **Templates**: Follow template variable naming conventions (`{VARIABLE}`)
- **Error handling**: Use custom exceptions from `errors.py`

## 🛠️ Development Workflow

### Branching Strategy

- **main**: Stable branch, deployable at any time
- **feature/**: New features (`feature/add-glow-integration`)
- **fix/**: Bug fixes (`fix/template-parsing-error`)
- **docs/**: Documentation updates (`docs/api-examples`)

### Commit Messages

Use conventional commit format:

```bash
# Features
feat: add glow integration for markdown rendering
feat(templates): add SAMPLE token support

# Bug fixes
fix: resolve template parsing error with special characters
fix(config): handle missing config file gracefully

# Documentation
docs: add API integration examples
docs(contributing): update development setup instructions

# Tests
test: add integration tests for message command
test(unit): improve coverage for template engine

# Refactoring
refactor: simplify command argument parsing
refactor(cli): extract common validation logic
```

### Pull Request Process

1. **Check existing issues**: Look for related issues or discussions
2. **Create feature branch**: Use descriptive branch names
3. **Implement changes**: Follow coding standards and test thoroughly
4. **Update documentation**: Update relevant docs and README if needed
5. **Run full test suite**: Ensure all tests pass
6. **Submit PR**: Use the pull request template and provide clear description

### PR Requirements

- [ ] **Tests pass**: All existing and new tests must pass
- [ ] **Code formatted**: Run `black` and `flake8`
- [ ] **Type checks**: Pass `mypy` type checking
- [ ] **Documentation**: Update docs for user-facing changes
- [ ] **Changelog**: Add entry to changelog for significant changes

## 🐛 Reporting Issues

### Bug Reports

Include the following information:

- **Environment**: OS, Python version, giv version
- **Command**: Full command that caused the issue
- **Expected behavior**: What you expected to happen
- **Actual behavior**: What actually happened
- **Reproduction steps**: Step-by-step instructions to reproduce
- **Additional context**: Logs, screenshots, or other relevant information

### Feature Requests

- **Problem description**: What problem would this feature solve?
- **Proposed solution**: How should this feature work?
- **Alternatives considered**: Other approaches you've considered
- **Additional context**: Examples, mockups, or related features

## 📚 Documentation Contributions

Documentation improvements are always welcome:

- **API documentation**: Help document configuration options and template variables
- **Workflow examples**: Provide integration examples (npm, CI/CD, Git hooks)
- **Tutorials**: Create step-by-step guides for common use cases
- **Template examples**: Share custom templates and prompt examples

## 🏗️ Building and Testing

### Local Binary Building

```bash
# Build binary for current platform
poetry run build-binary

# Test the binary
./giv-{platform}-{arch} --version
```

### Cross-Platform Testing

We test on multiple platforms. If you have access to different operating systems:

- **Linux**: Ubuntu 20.04+, RHEL 8+, Debian 10+
- **macOS**: 10.15+ (Intel and Apple Silicon)
- **Windows**: Windows 10 1909+

## 🤖 AI Integration Guidelines

When working with AI/LLM features:

- **Test with multiple providers**: OpenAI, Anthropic, Ollama
- **Handle rate limits**: Implement appropriate retry logic
- **Validate outputs**: Ensure generated content follows expected formats
- **Privacy considerations**: Don't expose sensitive repository information

## 📦 Release Process

Releases are automated via GitHub Actions:

1. **Version bump**: Update version in `pyproject.toml`
2. **Create tag**: `git tag v1.2.3 && git push origin v1.2.3`
3. **Automated workflow**: Builds binaries and publishes to PyPI

Contributors don't need to worry about releases - maintainers handle this process.

## 🤝 Community Guidelines

### Code of Conduct

- **Be respectful**: Treat all community members with respect
- **Be inclusive**: Welcome newcomers and diverse perspectives
- **Be collaborative**: Help others learn and grow
- **Be constructive**: Provide helpful feedback and suggestions

### Getting Help

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and community discussion
- **Documentation**: Check existing docs before asking questions

### Recognition

Contributors are recognized in:

- **Release notes**: Significant contributions mentioned in releases
- **GitHub contributors**: Automatic recognition via GitHub
- **Project documentation**: Notable contributors acknowledged in docs

## 💡 Tips for Success

### For First-Time Contributors

- **Start small**: Look for issues labeled `good first issue`
- **Read the code**: Familiarize yourself with the codebase structure
- **Ask questions**: Don't hesitate to ask for clarification
- **Test thoroughly**: Ensure your changes work across different scenarios

### For Experienced Contributors

- **Mentor others**: Help newcomers get started
- **Review PRs**: Provide constructive feedback on pull requests
- **Share expertise**: Contribute to architecture discussions
- **Lead initiatives**: Take ownership of larger features or improvements

## 🔗 Resources

- **[Project Repository](https://github.com/fwdslsh/giv)**: Main project page
- **[Documentation](docs/)**: Comprehensive project documentation
- **[Roadmap](docs/roadmap.md)**: Planned features and improvements
- **[Build System](docs/development/build-system.md)**: Technical architecture details
- **[Release Guide](docs/development/how-to-publish.md)**: Release process documentation

## 📞 Contact

- **Issues**: Use GitHub Issues for bugs and feature requests
- **Discussions**: Use GitHub Discussions for questions and ideas
- **Security**: Report security issues privately to the maintainers

---

Thank you for contributing to giv! Your efforts help make AI-powered Git tooling better for everyone. 🎉