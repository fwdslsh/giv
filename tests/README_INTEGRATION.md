# Integration Tests for Build and Publish Workflow

This directory contains comprehensive integration tests for the giv CLI build, package, and publish workflow. These tests validate the end-to-end process without actually publishing to external services.

## Test Files

### `test_integration_simple_build.py`
- **Purpose**: Core build workflow validation without complex dependencies
- **Scope**: System requirements, project structure, Poetry functionality, version detection
- **Dependencies**: Python, git, Poetry (optional)
- **Runtime**: Fast (~1-2 seconds per test)

### `test_integration_build_workflow.py`
- **Purpose**: Complete build system integration tests
- **Scope**: UnifiedBuilder, version detection, binary simulation, package building
- **Dependencies**: Build system modules, Poetry
- **Runtime**: Medium (~5-10 seconds per test)

### `test_integration_package_managers.py`
- **Purpose**: Package manager configuration and validation
- **Scope**: Homebrew, Scoop, NPM, Chocolatey, Debian, Snap, Flatpak
- **Dependencies**: Build system, package manager builders (optional)
- **Runtime**: Medium (~3-8 seconds per test)

### `test_integration_publish_workflow.py`
- **Purpose**: GitHub Actions workflow simulation and publish dry-runs
- **Scope**: Workflow steps, artifact handling, release preparation, error scenarios
- **Dependencies**: Build system (optional), subprocess mocking
- **Runtime**: Slow (~10-30 seconds per test)

## Running Tests

### Quick Tests (Recommended for CI)
```bash
# Run basic validation tests
python scripts/run_integration_tests.py --quick

# Or directly with pytest
poetry run pytest tests/test_integration_simple_build.py -v
```

### Full Integration Tests
```bash
# Run all integration tests
python scripts/run_integration_tests.py --full

# Or directly with pytest
poetry run pytest -m integration -v
```

### Specific Test Categories
```bash
# System requirements only
poetry run pytest tests/test_integration_simple_build.py::TestBasicBuildWorkflow::test_system_requirements -v

# Complete workflow simulation
poetry run pytest tests/test_integration_simple_build.py::TestEndToEndWorkflowSimulation -v

# Package manager tests
poetry run pytest tests/test_integration_package_managers.py -v
```

## Test Categories

### ✅ System Validation
- Python 3.8+ availability
- Git functionality
- Linux (Debian-based) environment
- Required tools and dependencies

### ✅ Project Structure
- pyproject.toml validation
- Source code structure
- Build directory organization
- Poetry configuration

### ✅ Build Process
- Version detection from multiple sources
- Binary creation simulation
- Package building (wheel, sdist)
- Checksum generation

### ✅ Package Managers
- Homebrew formula generation
- Scoop manifest creation
- NPM package structure
- Chocolatey package validation
- Debian package structure
- Snap and Flatpak configurations

### ✅ Publish Workflow
- GitHub Actions workflow simulation
- Artifact organization
- Release preparation
- PyPI publish dry-runs
- GitHub release creation
- Error scenario handling

### ✅ End-to-End Validation
- Complete build cycle
- Asset validation
- Workflow error detection
- Performance and size checks

## Test Design Principles

### 1. **No External Dependencies**
- Tests run without internet access
- Mock all external API calls
- Use temporary directories for file operations
- Simulate rather than actually publish

### 2. **Safe Execution**
- Never modify system configuration
- No side effects on host system
- Clean up all temporary resources
- Graceful handling of missing dependencies

### 3. **Comprehensive Coverage**
- Test both success and failure paths
- Validate error detection and reporting
- Cover edge cases and boundary conditions
- Test workflow from multiple entry points

### 4. **Platform Compatibility**
- Designed for Debian-based Linux systems
- Graceful degradation on other platforms
- Clear dependency requirements
- Optional components with fallbacks

## Expected Test Results

### Quick Tests (~7 test categories)
- **Runtime**: 5-10 seconds
- **Success Rate**: 100% on properly configured systems
- **Dependencies**: Python, git, Poetry

### Full Integration Tests (~20+ test categories)
- **Runtime**: 2-5 minutes
- **Success Rate**: 80-100% depending on available build components
- **Dependencies**: Full build system, optional package managers

## Troubleshooting

### Common Issues

**ImportError: Build modules not available**
- Expected behavior when build system components are missing
- Tests will skip gracefully with appropriate warnings
- Install Poetry and run `poetry install` for full functionality

**Poetry not available**
- Some tests will be skipped
- Install Poetry: `curl -sSL https://install.python-poetry.org | python3 -`
- Or use system package manager: `apt install python3-poetry`

**Permission errors**
- Ensure write access to temporary directories
- Check that /tmp is writable
- Run tests from project root directory

### Debugging Failed Tests

1. **Run with verbose output**: Add `-v -s` flags to pytest
2. **Check system requirements**: Run system validation tests first
3. **Review test logs**: Look for specific error messages
4. **Validate environment**: Ensure all required tools are available

## Integration with CI/CD

### GitHub Actions
```yaml
- name: Run Integration Tests
  run: |
    python scripts/run_integration_tests.py --quick
```

### Local Development
```bash
# Before committing changes
poetry run pytest tests/test_integration_simple_build.py -v

# Before releasing
python scripts/run_integration_tests.py --full
```

## Future Enhancements

- [ ] Cross-platform testing (macOS, Windows)
- [ ] Docker-based test environments
- [ ] Performance benchmarking
- [ ] Real package manager integration testing
- [ ] Network-dependent tests with proper isolation
- [ ] Integration with actual CI/CD environments

## Contributing

When adding new integration tests:

1. **Follow the naming convention**: `test_integration_*.py`
2. **Add appropriate markers**: `@pytest.mark.integration`, `@pytest.mark.slow`
3. **Include error handling**: Graceful degradation for missing dependencies
4. **Document test purpose**: Clear docstrings and comments
5. **Test both success and failure**: Comprehensive coverage
6. **Update this README**: Document new test categories

## Related Documentation

- [Build System Documentation](../build/README.md)
- [GitHub Workflows](../.github/workflows/)
- [Poetry Configuration](../pyproject.toml)
- [Main Test Suite](../tests/)