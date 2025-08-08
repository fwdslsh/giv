# Build System for giv CLI

This directory contains the modern Python-based build system for creating cross-platform binaries and packages for the giv CLI tool.

## Overview

The build system has been completely rewritten from Bash scripts to Python for better maintainability, cross-platform support, and integration with modern CI/CD workflows.

### Key Features

- **Cross-platform binary compilation** using PyInstaller
- **Automated GitHub Actions** for building on multiple platforms
- **Package manager integration** (Homebrew, Scoop, PyPI, etc.)
- **Comprehensive testing** of built binaries
- **Size optimization** with UPX compression
- **Release automation** with checksums and signing

## Quick Start

### Prerequisites

- Python 3.8+
- Poetry (for dependency management)
- Git

### Building Binaries

```bash
# Build for current platform only
python build.py --binaries-only

# Build packages for specific package managers
python build.py --packages-only --package-types pypi homebrew

# Build all binaries and packages
python build.py

# List available builders
python build.py --list-builders
```

### Publishing

```bash
# Publish to PyPI (using dedicated publish script)
python publish.py pypi

# Publish to Test PyPI
python publish.py pypi --test

# Note: Package manager updates are built but not auto-published
```

## Architecture

### Core Components

- **`core/`** - Core build system infrastructure
  - `config.py` - Build configuration management
  - `version_manager.py` - Version handling and validation
  - `utils.py` - Utility functions for build system

- **`build_binary.py`** - Simple binary compilation using PyInstaller
  - Builds for current platform only
  - Auto-detects platform and architecture
  - Minimal configuration approach

### Package Managers

- **`pypi/`** - Python Package Index distribution
- **`homebrew/`** - macOS/Linux Homebrew formula
- **`scoop/`** - Windows Scoop manifest
- **`npm/`** - Node.js package wrapper
- **`snap/`** - Ubuntu Snap packages
- **`flatpak/`** - Linux Flatpak packages

**Note:** Package manager builders are loaded dynamically and may not all be fully implemented.

### Automation

- **GitHub Actions** - Can be configured for automated builds
- **Local development** - Primary focus on local building and testing

## Build Commands

### Main Build Script (`build.py`)

```bash
# List available builders
python build.py --list-builders

# Build binaries only (current platform)
python build.py --binaries-only

# Build packages only
python build.py --packages-only

# Build specific package types
python build.py --packages-only --package-types pypi homebrew scoop

# Build everything (binaries + packages)
python build.py

# Specify version (auto-detected if not provided)
python build.py --version 1.2.3
```

### Publishing Script (`publish.py`)

```bash
# Publish to PyPI
python publish.py pypi

# Publish to Test PyPI
python publish.py pypi --test

# Note: Full publishing system is under development
```

### Individual Component Scripts

```bash
# Build binary for current platform
python build_binary.py

# Build PyPI packages (if pypi/ builder exists)
python pypi/build.py

# Generate package manager configs (if builders exist)
python homebrew/build.py
python scoop/build.py
```

## Platform Support

### Current Implementation

The build system currently focuses on **local platform building**:

| Platform | Architecture | Binary Name | Status |
|----------|-------------|-------------|--------|
| Current Platform | Auto-detected | `giv-{system}-{arch}` | ✅ Supported |

**System mapping:**
- `darwin` → `macos` 
- `linux` → `linux`
- `windows` → `windows`

**Architecture mapping:**
- `x86_64`, `amd64` → `x86_64`
- `aarch64`, `arm64` → `arm64`

### Build Methods

1. **Local builds** - Build on the current platform using `build_binary.py`
2. **Package managers** - Generate configuration files for distribution
3. **Future**: Cross-platform builds and CI/CD automation

## Package Manager Support

### Implementation Status

The build system includes package manager builders that are dynamically loaded:

```python
# From build.py - builders are loaded with graceful fallback
try:
    from pypi import PyPIBuilder
    self.builders['pypi'] = PyPIBuilder
except ImportError:
    print("⚠️  PyPIBuilder not available")
```

### Supported Package Managers

- **PyPI** - Python package distribution (primary)
- **Homebrew** - macOS/Linux package manager
- **Scoop** - Windows package manager  
- **NPM** - Node.js wrapper package
- **Snap** - Ubuntu package format
- **Flatpak** - Universal Linux package format

**Note:** Not all builders may be fully implemented. Use `python build.py --list-builders` to see available ones.

## CI/CD Integration

### Current Status

The build system is designed for local development with future CI/CD integration planned:

- **Local builds** - Primary focus using `build.py` and `publish.py`
- **GitHub Actions** - Can be configured for automated builds
- **Package distribution** - Individual package manager builders available

### Environment Variables

For publishing (when implemented):

```bash
# PyPI publishing
PYPI_API_TOKEN=your-pypi-token
TEST_PYPI_API_TOKEN=your-test-pypi-token
```

## Development

### Current Implementation

The `UnifiedBuilder` class in `build.py` provides:

1. **Dynamic builder loading** - Package managers loaded as available
2. **Binary building** - Uses `build_binary.py` for current platform
3. **Package building** - Coordinates multiple package manager builders
4. **Version management** - Auto-detection via `VersionManager`

### Adding New Package Managers

1. Create new directory under `build/` (e.g., `apt/`, `yum/`)
2. Implement builder class with appropriate methods:
   - `build_packages()` for PyPI-style builders
   - `build_formula()` for Homebrew-style builders  
   - `build_manifest()` for Scoop-style builders
   - `build_package()` for generic builders
3. Import will be attempted in `_load_builders()` method
4. Test with `python build.py --list-builders`

### Debugging Builds

```bash
# Check available builders
python build.py --list-builders

# Test binary building
python build_binary.py

# Test specific package type
python build.py --packages-only --package-types pypi
```

## File Structure

```
build/
├── README.md                       # This file
├── build.py                        # Main build orchestrator (UnifiedBuilder)
├── publish.py                      # Main publishing orchestrator (UnifiedPublisher)
├── build_binary.py                 # Simple PyInstaller-based binary builder
│
├── core/                           # Core infrastructure
│   ├── __init__.py
│   ├── config.py                   # BuildConfig management
│   ├── version_manager.py          # Version handling
│   └── utils.py                    # Build utilities
│
├── pypi/                          # PyPI packages
│   └── build.py                   # PyPIBuilder (if implemented)
│
├── homebrew/                      # Homebrew formula
│   └── build.py                   # HomebrewBuilder (if implemented)
│
├── scoop/                         # Scoop manifest
│   └── build.py                   # ScoopBuilder (if implemented)
│
├── npm/                           # NPM wrapper package
│   └── build.py                   # NPMBuilder (if implemented)
│
├── snap/                          # Snap packages
│   └── build.py                   # SnapBuilder (if implemented)
│
├── flatpak/                       # Flatpak packages
│   └── build.py                   # FlatpakBuilder (if implemented)
│
└── giv-{platform}-{arch}/         # Built binary output
```

## Migration from Bash

The original Bash-based build system has been replaced with this Python implementation. Key improvements:

- **Better cross-platform support** - No shell dependencies
- **Improved error handling** - Detailed error messages and graceful fallbacks
- **Modern tooling** - Poetry, PyInstaller, dynamic builder loading
- **Maintainability** - Type hints, documentation, modular design
- **Simplified approach** - Focus on core functionality first

### Current State

- ✅ **Basic binary building** - Current platform using PyInstaller
- ✅ **Package manager framework** - Dynamic loading of builders
- ✅ **Version management** - Auto-detection and handling
- 🚧 **Multi-platform** - Individual builders need implementation
- 🚧 **CI/CD integration** - Framework ready, workflows pending
- 🚧 **Cross-compilation** - Future enhancement

## Troubleshooting

### Common Issues

1. **Builder not available**: Check with `python build.py --list-builders`
2. **Binary build fails**: Ensure PyInstaller and dependencies are installed
3. **Platform detection**: Check `build_binary.py` output for platform naming
4. **Package build fails**: Verify individual package builder implementation

### Getting Help

- Check available builders: `python build.py --list-builders`
- Test binary building: `python build_binary.py`
- Review build logs for detailed error messages
- Verify core dependencies are installed via Poetry

## Contributing

When contributing to the build system:

1. Follow existing code patterns in `UnifiedBuilder` and `UnifiedPublisher`
2. Add error handling with graceful fallbacks (see `_load_builders()`)
3. Update this README for significant changes
4. Test with `python build.py --list-builders` and individual commands
5. Ensure new package managers follow the builder interface patterns

### Implementation Notes

- Builders are loaded dynamically with ImportError handling
- Each package manager can have different method signatures
- The system prioritizes working functionality over feature completeness
- Current focus is on local development workflows