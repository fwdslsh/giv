# giv - Complete Application Specification

## Overview

**giv** (pronounced "give") is an AI-powered Git history assistant that transforms raw Git history into polished commit messages, summaries, changelogs, release notes, and announcements. This Python implementation provides cross-platform binary distribution with zero runtime dependencies.

### Primary Purpose

Transform Git history data into professional documentation using AI assistance. giv analyzes Git diffs, commit history, and repository metadata to generate context-aware documentation that maintains consistency and follows industry standards.

### Key Features

- **Self-contained binaries** - No Python installation required
- **Multiple AI backends** - OpenAI, Anthropic, Ollama, and custom endpoints  
- **Rich command suite** - Generate messages, summaries, changelogs, and release notes
- **Smart Git integration** - Support for revision ranges, pathspecs, and staged changes
- **Flexible configuration** - Project and user-level settings with inheritance
- **Template system** - Customizable prompts for all output types
- **Output modes** - Auto, append, prepend, update, overwrite options
- **Cache system** - Efficient handling of large Git histories

## Target Users

- **Software developers** who want professional commit messages and changelogs
- **Engineering teams** needing consistent documentation standards
- **Open source maintainers** creating release notes and announcements
- **DevOps engineers** integrating documentation into CI/CD pipelines
- **Project managers** tracking development progress through Git history

## Core Functionality

### Document Generation Types

1. **Commit Messages** - AI-generated commit messages from Git diffs
2. **Summaries** - Concise overviews of recent changes
3. **Changelogs** - Keep a Changelog format release documentation
4. **Release Notes** - Detailed feature and fix documentation for releases
5. **Announcements** - Marketing-style release announcements
6. **Custom Documents** - User-defined content using custom prompt templates

### Git Integration Capabilities

- **Revision Range Analysis** - Process specific commit ranges (e.g., `v1.0.0..HEAD`)
- **Pathspec Filtering** - Limit analysis to specific files or directories
- **Working Tree Analysis** - Analyze unstaged changes (`--current`)
- **Staged Changes Analysis** - Analyze staged changes (`--cached`)
- **Diff Processing** - Extract meaningful context from Git diffs
- **Commit History Processing** - Parse and summarize commit metadata

### AI Backend Support

- **OpenAI** - GPT-4, GPT-3.5-turbo models
- **Anthropic** - Claude 3.5 Sonnet, Claude 3 Opus models  
- **Ollama** - Local models including Llama 3.2, Code Llama, devstral
- **Custom endpoints** - Any OpenAI-compatible API

## Command Line Interface

### Application Name

`giv`

### Global Options

These options can be used with any command and must appear before the subcommand:

```bash
giv [global-options] <command> [command-options] [arguments]
```

#### Core Global Options

- `-h, --help` - Show help message and exit
- `-v, --version` - Show version number and exit
- `--verbose` - Enable debug/trace output (can be repeated for more verbosity)
- `--dry-run` - Preview only; don't write any files

#### Configuration Options

- `--config-file CONFIG_FILE` - Specify custom config file to source
- `--api-url API_URL` - Remote API endpoint URL
- `--api-key API_KEY` - API key for remote mode
- `--api-model API_MODEL` - Remote model name
- `--model MODEL` - Local or remote model name (alias for --api-model)

#### Content Options

- `--todo-files TODO_FILES` - Pathspec for files to scan for TODOs
- `--todo-pattern TODO_PATTERN` - Regex to match TODO lines
- `--version-file VERSION_FILE` - Pathspec of file(s) to inspect for version bumps
- `--version-pattern VERSION_PATTERN` - Custom regex to identify version strings

#### Output Options

- `--output-mode {auto,prepend,append,update,overwrite,none}` - Output mode
- `--output-version OUTPUT_VERSION` - Version string for release content
- `--output-file OUTPUT_FILE` - Write output to specified file instead of stdout
- `--prompt-file PROMPT_FILE` - Path to custom prompt template file

#### Utility Options

- `--list` - List available local models

## Commands

### 1. `config` - Configuration Management

Manage persistent configuration values with support for list, get, set, and unset operations.

**Syntax:**
```bash
giv config [--list|--get|--set|--unset] [key] [value]
giv config list                    # List all configuration values
giv config get <key>               # Get a configuration value  
giv config set <key> <value>       # Set a configuration value
giv config unset <key>             # Remove a configuration value

# Bash-compatible syntax (automatically converted)
giv config                         # Lists all values
giv config <key>                   # Gets value for key
giv config <key> <value>           # Sets key to value
```

**Options:**
- `--list` - List all configuration values
- `--get` - Get a configuration value
- `--set` - Set a configuration value  
- `--unset` - Remove a configuration value

**Arguments:**
- `key` - Configuration key (optional, required for get/set/unset)
- `value` - Configuration value (optional, required for set)

**Examples:**
```bash
giv config list
giv config set api.key "your-api-key"
giv config set api.model "gpt-4"
giv config get api.url
giv config unset api.key
```

### 2. `message` (alias: `msg`) - Commit Message Generation

Generate AI-assisted commit messages from Git diffs.

**Syntax:**
```bash
giv message [options] [revision] [pathspec...]
```

**Options:**
- `--current` - Analyze working tree changes (default)
- `--cached` - Analyze staged changes only

**Arguments:**
- `revision` - Revision range to analyze (default: `--current`)
- `pathspec` - Limit analysis to specified paths (optional)

**Examples:**
```bash
giv message                        # Current working tree changes
giv message --cached               # Staged changes only
giv message HEAD~3..HEAD           # Last 3 commits
giv message HEAD~1 src/            # Last commit, src/ directory only
giv message --output-file commit.txt
```

### 3. `summary` - Change Summary Generation

Generate comprehensive summaries of recent changes.

**Syntax:**
```bash
giv summary [options] [revision] [pathspec...]
```

**Options:**
- `--current` - Analyze working tree changes (default)
- `--cached` - Analyze staged changes only

**Arguments:**
- `revision` - Revision range to summarize (default: `--current`)
- `pathspec` - Limit summary to specified paths (optional)

**Examples:**
```bash
giv summary                        # Current changes
giv summary HEAD~5..HEAD           # Last 5 commits
giv summary v1.0.0..HEAD src/      # Since v1.0.0, src/ only
giv summary --output-file SUMMARY.md
```

### 4. `changelog` - Changelog Generation

Generate or update changelogs in Keep a Changelog format.

**Syntax:**
```bash
giv changelog [options] [revision] [pathspec...]
```

**Arguments:**
- `revision` - Revision range for changelog (default: `--current`)
- `pathspec` - Limit changelog to specified paths (optional)

**Examples:**
```bash
giv changelog v1.0.0..HEAD         # Since last release
giv changelog --output-file CHANGELOG.md
giv changelog --output-mode append v2.0.0..HEAD
```

### 5. `release-notes` - Release Notes Generation

Generate detailed release notes for tagged releases.

**Syntax:**
```bash
giv release-notes [options] [revision] [pathspec...]
```

**Arguments:**
- `revision` - Revision range for release notes (default: `--current`)
- `pathspec` - Limit release notes to specified paths (optional)

**Examples:**
```bash
giv release-notes v1.2.0..HEAD     # Since v1.2.0
giv release-notes --output-file RELEASE_NOTES.md
giv release-notes --output-version "2.0.0"
```

### 6. `announcement` - Marketing Announcement Generation

Create marketing-style announcements for releases.

**Syntax:**
```bash
giv announcement [options] [revision] [pathspec...]
```

**Arguments:**
- `revision` - Revision range for announcement (default: `--current`)
- `pathspec` - Limit announcement to specified paths (optional)

**Examples:**
```bash
giv announcement v1.0.0..HEAD      # Since v1.0.0
giv announcement --output-file ANNOUNCEMENT.md
```

### 7. `document` - Custom Document Generation

Generate custom content using user-defined prompt templates.

**Syntax:**
```bash
giv document [options] [revision] [pathspec...]
```

**Required Options:**
- `--prompt-file PROMPT_FILE` - Path to custom prompt template (required)

**Arguments:**
- `revision` - Revision range to document (default: `--current`)
- `pathspec` - Limit documentation to specified paths (optional)

**Examples:**
```bash
giv document --prompt-file templates/security-review.md HEAD~10..HEAD
giv document --prompt-file custom.md --output-file REPORT.md
```

### 8. `init` - Configuration Initialization

Initialize giv configuration interactively.

**Syntax:**
```bash
giv init
```

**Behavior:**
- Creates `.giv/` directory structure
- Prompts for basic configuration (API keys, models, etc.)
- Sets up default templates
- Configures project-specific settings

**Examples:**
```bash
giv init                           # Interactive setup
```

### 9. `version` - Version Information

Display version information and exit.

**Syntax:**
```bash
giv version
```

**Examples:**
```bash
giv version                        # Show version number
```

### 10. `help` - Command Help

Show help information for commands.

**Syntax:**
```bash
giv help [command_name]
```

**Arguments:**
- `command_name` - Command to show help for (optional)

**Examples:**
```bash
giv help                          # General help
giv help message                  # Help for message command
```

### 11. `available-releases` - List Available Versions

List all available giv versions from GitHub releases.

**Syntax:**
```bash
giv available-releases
```

**Examples:**
```bash
giv available-releases            # List all versions
```

### 12. `update` - Self-Update

Update giv to the latest or specified version.

**Syntax:**
```bash
giv update [version]
```

**Arguments:**
- `version` - Specific version to update to (optional, default: latest)

**Behavior:**
- For security reasons, provides manual update instructions
- Does not automatically execute scripts
- Shows available update methods (package managers, direct download, etc.)

**Examples:**
```bash
giv update                        # Update to latest
giv update v0.6.0                 # Update to specific version
```

### 13. `clear-cache` - Cache Management

Clear all cached summaries and metadata.

**Syntax:**
```bash
giv clear-cache
```

**Examples:**
```bash
giv clear-cache                   # Clear all caches
```

## Configuration System

### Configuration Hierarchy

giv uses a three-tier configuration hierarchy (highest to lowest precedence):

1. **Command-line arguments** - Highest precedence
2. **Project configuration** - `.giv/config` in project root (or nearest parent)
3. **User configuration** - `~/.giv/config` in user home directory
4. **Environment variables** - `GIV_*` prefixed variables
5. **Default values** - Built-in defaults

### Configuration File Format

Configuration files use simple `KEY=VALUE` format with support for quoted values:

```bash
# API Configuration
api.url=https://api.openai.com/v1/chat/completions
api.key="your-api-key-here"
api.model=gpt-4

# Project Configuration  
project.title="My Project"
project.description="A sample project"
project.url="https://github.com/user/project"

# Template Configuration
todo.pattern="TODO:|FIXME:|HACK:"
version.file="package.json|pyproject.toml"
```

### Environment Variables

All configuration keys can be set via environment variables using the `GIV_` prefix and uppercase, dot-separated keys:

```bash
export GIV_API_KEY="your-api-key"
export GIV_API_MODEL="gpt-4"
export GIV_API_URL="https://api.openai.com/v1/chat/completions"
export GIV_TODO_PATTERN="TODO:|FIXME:"
```

### Configuration Keys

#### API Configuration
- `api.url` - API endpoint URL (default: `http://localhost:11434/v1/chat/completions`)
- `api.key` - API authentication key
- `api.model` - Model name (default: `devstral`)
- `api.model.temperature` - Model temperature (default: 0.9 for creative, 0.7 for factual)
- `api.model.max_tokens` - Maximum tokens (default: 8192)
- `api.model.timeout` - Request timeout in seconds (default: 30)

#### Project Configuration
- `project.title` - Project title for documentation
- `project.description` - Project description
- `project.url` - Project URL
- `project.type` - Project type hint

#### Content Configuration
- `todo.file` - Files to scan for TODOs (pathspec)
- `todo.pattern` - Regex pattern for TODO detection
- `version.file` - Files to scan for version information (pathspec)
- `version.pattern` - Regex pattern for version detection

#### Output Configuration
- `output.mode` - Default output mode (`auto`, `append`, `prepend`, `update`, `overwrite`)
- `changelog.file` - Default changelog filename (default: `CHANGELOG.md`)
- `release_notes_file` - Default release notes filename (default: `RELEASE_NOTES.md`)
- `announcement_file` - Default announcement filename (default: `ANNOUNCEMENT.md`)

## Template System

### Template Discovery

Templates are discovered using the following search hierarchy:

1. **Explicit path** - When `--prompt-file` specifies absolute/relative path
2. **Custom template directory** - If provided to TemplateEngine
3. **Project-level templates** - `.giv/templates/` directory
4. **User-level templates** - `~/.giv/templates/` directory  
5. **System templates** - Built-in templates shipped with giv

### Built-in Templates

- `commit_message_prompt.md` - Commit message generation
- `summary_prompt.md` - Change summary generation
- `changelog_prompt.md` - Changelog generation
- `release_notes_prompt.md` - Release notes generation
- `announcement_prompt.md` - Marketing announcement generation

### Template Variables

Templates support variable substitution using `{VARIABLE}` syntax:

#### Core Variables
- `{SUMMARY}` - Processed Git diff and commit information
- `{PROJECT_TITLE}` - Project title from configuration
- `{VERSION}` - Version string (for release content)
- `{DATE}` - Current date
- `{AUTHOR}` - Git author information
- `{COMMIT_ID}` - Git commit SHA
- `{DIFF}` - Raw Git diff output

#### Content Variables  
- `{TODOS}` - Extracted TODO items from code
- `{VERSION_CHANGES}` - Detected version bump information
- `{EXAMPLE}` - Example content (template-specific)
- `{RULES}` - Output formatting rules (template-specific)

### Template Customization

Users can customize templates by:

1. **Copying system templates** to project/user template directories
2. **Creating custom templates** for the `document` command
3. **Modifying prompt content** while preserving variable placeholders
4. **Adding custom variables** through configuration

### Template Format

Templates are Markdown files with:
- **Variable placeholders** using `{VARIABLE}` syntax
- **Instruction sections** for AI guidance
- **Example sections** showing desired output format
- **Rules sections** specifying formatting requirements

## Output System

### Output Modes

giv supports multiple output modes to handle different workflow requirements:

#### `auto` (Default)
- **New files**: Create new file
- **Existing files**: Intelligently merge content based on file type
- **Changelogs**: Prepend new entries
- **Other files**: Append content

#### `prepend`
- Add new content to the beginning of existing files
- Create new file if it doesn't exist
- Useful for changelogs and release notes

#### `append`  
- Add new content to the end of existing files
- Create new file if it doesn't exist
- Useful for continuous documentation

#### `update`
- Replace specific sections in existing files
- Create new file if it doesn't exist
- Useful for maintaining living documents

#### `overwrite`
- Replace entire file content
- Create new file if it doesn't exist
- Useful for generated reports

#### `none`
- Output to stdout only
- Never write to files
- Useful for previewing or piping to other commands

### File Handling

- **Backup creation** - Original files backed up before modification (when appropriate)
- **Atomic writes** - Files written atomically to prevent corruption
- **Permission preservation** - File permissions maintained during updates
- **Directory creation** - Output directories created automatically

### Dry Run Mode

When `--dry-run` is specified:
- No files are written or modified
- All output is sent to stdout with clear labels
- Template rendering and AI generation still occur
- Useful for previewing changes before applying

## AI Integration

### Model Selection

giv supports multiple AI backends through a unified interface:

#### OpenAI Models
- `gpt-4` - Highest quality, most expensive
- `gpt-4-turbo` - Fast, high quality
- `gpt-3.5-turbo` - Good quality, cost-effective

#### Anthropic Models  
- `claude-3-5-sonnet` - High quality, good for documentation
- `claude-3-opus` - Highest quality Anthropic model

#### Local Models (via Ollama)
- `devstral` - Code-focused model (default for local)
- `llama3.2` - General purpose model
- `codellama` - Code-specialized model

### API Configuration

#### OpenAI Configuration
```bash
giv config set api.url "https://api.openai.com/v1/chat/completions"
giv config set api.key "your-openai-api-key"
giv config set api.model "gpt-4"
```

#### Anthropic Configuration
```bash
giv config set api.url "https://api.anthropic.com/v1/messages"
giv config set api.key "your-anthropic-api-key"  
giv config set api.model "claude-3-5-sonnet"
```

#### Ollama Configuration (Local)
```bash
giv config set api.url "http://localhost:11434/v1/chat/completions"
giv config set api.model "devstral"
# No API key required for local models
```

#### Custom Endpoint Configuration
```bash
giv config set api.url "https://your-custom-endpoint.com/v1/chat/completions"
giv config set api.key "your-custom-api-key"
giv config set api.model "your-custom-model"
```

### Model Parameters

- **Temperature** - Controls randomness (0.0-1.0)
  - Creative tasks (messages, announcements): 0.9
  - Factual tasks (changelogs, release notes): 0.7
- **Max Tokens** - Maximum response length (default: 8192)
- **Timeout** - Request timeout in seconds (default: 30)

## Git Integration

### Revision Specification

giv supports Git's full revision specification syntax:

#### Revision Ranges
- `HEAD~5..HEAD` - Last 5 commits
- `v1.0.0..HEAD` - All commits since v1.0.0 tag
- `main..feature-branch` - Commits in feature-branch not in main
- `--current` - Working tree changes (unstaged)
- `--cached` - Staged changes (index)

#### Single Revisions
- `HEAD` - Latest commit
- `HEAD~3` - 3 commits before HEAD
- `v1.2.0` - Specific tag
- `abc1234` - Specific commit SHA

### Pathspec Support

Limit analysis to specific files or directories:

```bash
giv message HEAD~3..HEAD src/           # Only src/ directory
giv changelog v1.0.0..HEAD "*.py"       # Only Python files
giv summary HEAD~5..HEAD docs/ tests/   # Multiple paths
```

### Git Repository Requirements

- **Valid Git repository** - Must be run within a Git repository
- **Commit history** - Requires accessible commit history
- **File access** - Read access to repository files and Git metadata

## Error Handling

### Error Types and Exit Codes

- **0** - Success
- **1** - General error
- **2** - Template error (missing template, invalid format)
- **3** - Git error (not in repository, invalid revision)
- **4** - Configuration error (invalid config, missing required values)
- **5** - API error (network issues, authentication failures)

### Error Messages

Error messages provide:
- **Clear description** of what went wrong
- **Context information** about where the error occurred
- **Suggested solutions** when possible
- **Exit codes** for programmatic handling

### Troubleshooting

Common error scenarios and solutions:

#### Template Errors
- **Missing template**: Check template search paths, verify template exists
- **Invalid template**: Validate template syntax, check variable names

#### Git Errors
- **Not in repository**: Run giv from within a Git repository
- **Invalid revision**: Verify revision syntax, check that commits exist

#### Configuration Errors
- **Missing API key**: Set API key via config or environment variable
- **Invalid API endpoint**: Verify URL format and endpoint accessibility

#### API Errors
- **Authentication failure**: Verify API key is correct and has permissions
- **Rate limiting**: Implement retry logic or reduce request frequency
- **Network issues**: Check internet connectivity and endpoint availability

## Security Considerations

### Template Security
- **Path traversal prevention** - Template paths validated to prevent directory traversal
- **Safe directories only** - Template loading restricted to safe directories
- **Input validation** - Template names validated for security

### API Security
- **Secure credential storage** - API keys stored in protected configuration files
- **HTTPS enforcement** - All API communications use HTTPS when possible
- **Input sanitization** - User input sanitized before sending to AI models

### File System Security
- **Safe file operations** - Atomic writes prevent corruption
- **Permission preservation** - File permissions maintained during operations
- **Backup creation** - Original files backed up before modification

## Installation and Distribution

### Installation Methods

#### Binary Installation (Recommended)
```bash
# Install script (detects platform automatically)
curl -fsSL https://raw.githubusercontent.com/fwdslsh/giv/main/install.sh | sh

# Manual binary download
# Download from https://github.com/fwdslsh/giv/releases
```

#### Package Manager Installation
```bash
# PyPI
pip install giv

# Homebrew (macOS/Linux)
brew install giv

# Scoop (Windows)  
scoop install giv
```

#### From Source
```bash
git clone https://github.com/fwdslsh/giv.git
cd giv
pip install .
```

### System Requirements

#### Supported Platforms
- **Linux**: GLIBC 2.31+ (Ubuntu 20.04+, RHEL 8+, Debian 10+)
- **macOS**: 10.15+ (Catalina and newer)
- **Windows**: Windows 10 1909+ (November 2019 Update)

#### Dependencies
- **Binary distribution**: No dependencies required
- **PyPI installation**: Python 3.9+ required
- **Source installation**: Python 3.9+, pip, build tools

## Docker Usage

### Official Docker Container

The official Docker container provides an easy way to use giv without installing it locally:

```bash
# Pull the Docker image
docker pull fwdslsh/giv:latest

# Run giv commands
docker run --rm fwdslsh/giv message

# Run an interactive shell
docker run -it fwdslsh/giv

# Mount local repository
docker run --rm -v $(pwd):/workspace -w /workspace fwdslsh/giv message
```

**Docker Hub:** [fwdslsh/giv](https://hub.docker.com/r/fwdslsh/giv)

## Integration Examples

### CI/CD Pipeline Integration

#### GitHub Actions
```yaml
name: Generate Changelog
on:
  release:
    types: [created]
jobs:
  changelog:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install giv
        run: curl -fsSL https://raw.githubusercontent.com/fwdslsh/giv/main/install.sh | sh
      - name: Generate changelog
        run: giv changelog --output-file CHANGELOG.md
        env:
          GIV_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

#### GitLab CI
```yaml
generate-docs:
  image: fwdslsh/giv:latest
  script:
    - giv changelog v1.0.0..HEAD --output-file CHANGELOG.md
    - giv release-notes --output-file RELEASE_NOTES.md
  variables:
    GIV_API_KEY: $CI_OPENAI_API_KEY
```

### Pre-commit Hook Integration

```bash
#!/bin/sh
# .git/hooks/prepare-commit-msg

# Only run for commits without existing message
if [ -z "$2" ]; then
    # Generate commit message and use as template
    giv message --output-mode none > "$1"
fi
```

### Development Workflow Integration

```bash
# Add to ~/.bashrc or ~/.zshrc
alias gc='git add . && giv message --cached --output-mode none | git commit -F -'
alias gr='giv release-notes --output-file RELEASE_NOTES.md'
alias gcl='giv changelog --output-file CHANGELOG.md'
```

## Usage Examples

### Basic Usage

```bash
# Initialize giv in a project
giv init

# Generate commit message for current changes
giv message

# Generate commit message for staged changes
giv message --cached

# Generate summary of last 5 commits
giv summary HEAD~5..HEAD

# Generate changelog since last release
giv changelog v1.0.0..HEAD
```

### Advanced Usage

```bash
# Generate release notes with custom model
giv release-notes v2.0.0..HEAD --api-model gpt-4 --output-file RELEASE_NOTES.md

# Generate changelog for specific directory
giv changelog HEAD~10..HEAD src/ --output-mode prepend

# Create custom documentation
giv document --prompt-file templates/security-review.md HEAD~20..HEAD

# Generate announcement with version
giv announcement v2.1.0..HEAD --output-version "2.1.0" --output-file ANNOUNCE.md
```

### Configuration Examples

```bash
# Set up OpenAI
giv config set api.url "https://api.openai.com/v1/chat/completions"
giv config set api.key "sk-your-openai-key"
giv config set api.model "gpt-4"

# Set up Anthropic
giv config set api.url "https://api.anthropic.com/v1/messages"  
giv config set api.key "your-anthropic-key"
giv config set api.model "claude-3-5-sonnet"

# Set up local Ollama
giv config set api.url "http://localhost:11434/v1/chat/completions"
giv config set api.model "devstral"

# Configure project settings
giv config set project.title "My Awesome Project"
giv config set project.description "A revolutionary new tool"
giv config set todo.pattern "TODO:|FIXME:|HACK:|NOTE:"
```

### Template Customization

```bash
# Initialize templates
giv init

# Edit commit message template
nano .giv/templates/commit_message_prompt.md

# Create custom template
cat > .giv/templates/feature-review.md << 'EOF'
# Feature Review

{SUMMARY}

## Instructions

Review the provided changes and create a feature review document that includes:

1. Feature overview
2. Technical changes
3. Testing recommendations
4. Documentation updates needed

Focus on technical accuracy and completeness.
EOF

# Use custom template
giv document --prompt-file .giv/templates/feature-review.md HEAD~5..HEAD
```

## Conclusion

This specification provides complete documentation for implementing the giv CLI tool. It covers all aspects from basic command usage to advanced configuration, template customization, and integration scenarios. The specification is designed to be comprehensive enough for complete reimplementation while serving as a definitive reference for users and contributors.