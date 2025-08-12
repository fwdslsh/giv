#!/bin/bash
set -euo pipefail

# giv CLI Installation Script
# Downloads and installs the appropriate binary for your platform

# Configuration
REPO="fwdslsh/giv"
BINARY_NAME="giv"
DEFAULT_INSTALL_DIR="/usr/local/bin"
USER_INSTALL_DIR="$HOME/.local/bin"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# ASCII banner function
show_banner() {
    echo -e "${CYAN}${BOLD}"
    cat << 'EOF'
    _____ _____ _   _ 
   |   __|     | | | |
   |  |  |-   -| | | |
   |_____|_____|_____| 
                       
   AI-Powered Git Assistant
   
EOF
    echo -e "${NC}"
    echo -e "${BLUE}Welcome to the giv installation script!${NC}"
    echo -e "${BLUE}This will download and install giv on your system.${NC}"
    echo
}

# Logging functions
log_info() {
    echo -e "${BLUE}INFO:${NC} $1"
}

log_success() {
    echo -e "${GREEN}SUCCESS:${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}WARNING:${NC} $1"
}

log_error() {
    echo -e "${RED}ERROR:${NC} $1" >&2
}

# Help message
show_help() {
    cat << EOF
giv CLI Installation Script

CORRECT INSTALLATION COMMAND:
    curl -fsSL https://raw.githubusercontent.com/fwdslsh/giv/main/install.sh | sh

USAGE:
    $0 [OPTIONS]

OPTIONS:
    -h, --help          Show this help message
    -v, --version TAG   Install specific version (default: latest)
    -d, --dir PATH      Installation directory (default: /usr/local/bin or ~/.local/bin)
    -u, --user          Install to user directory (~/.local/bin)
    -f, --force         Force reinstall even if already installed
    --dry-run           Show what would be done without installing

EXAMPLES:
    $0                          # Install latest version to /usr/local/bin
    $0 --user                   # Install to ~/.local/bin (no sudo required)
    $0 --version v1.0.0         # Install specific version
    $0 --dir ~/bin              # Install to custom directory
    $0 --dry-run                # Preview installation

ENVIRONMENT VARIABLES:
    GIV_INSTALL_DIR            Override default installation directory
    GIV_VERSION                Override version to install
    GIV_FORCE                  Force reinstall (set to any value)

COMMON MISTAKES:
    ❌ Using wrong repository URL (e.g., 'catalog' instead of 'giv')
    ❌ Missing 'main' branch in URL
    ❌ Using outdated installation instructions

For documentation and troubleshooting:
    https://github.com/fwdslsh/giv/blob/main/docs/installation.md

EOF
}

# Detect platform and architecture
detect_platform() {
    local os arch
    
    # Detect OS
    case "$(uname -s)" in
        Linux*)     os="linux";;
        Darwin*)    os="darwin";;
        CYGWIN*|MINGW*|MSYS*) os="windows";;
        *)          
            log_error "Unsupported operating system: $(uname -s)"
            exit 1
            ;;
    esac
    
    # Detect architecture
    case "$(uname -m)" in
        x86_64|amd64)   arch="x86_64";;
        arm64|aarch64)  arch="arm64";;
        *)              
            log_error "Unsupported architecture: $(uname -m)"
            exit 1
            ;;
    esac
    
    # Special case for Windows
    if [[ "$os" == "windows" ]]; then
        echo "${os}-${arch}.exe"
    else
        echo "${os}-${arch}"
    fi
}

# Check GLIBC compatibility on Linux
check_glibc_compatibility() {
    local dry_run="$1"
    
    if [[ "$(uname -s)" != "Linux" ]]; then
        return 0  # Not Linux, skip check
    fi
    
    # Check if ldd is available
    if ! command -v ldd >/dev/null 2>&1; then
        log_warning "Cannot check GLIBC version (ldd not found)"
        return 0
    fi
    
    # Get GLIBC version
    local glibc_version
    glibc_version=$(ldd --version 2>/dev/null | head -n1 | grep -oE '[0-9]+\.[0-9]+' | head -n1)
    
    if [[ -z "$glibc_version" ]]; then
        log_warning "Cannot determine GLIBC version"
        return 0
    fi
    
    log_info "Detected GLIBC version: $glibc_version"
    
    # Compare with minimum required version (2.31)
    local required_version="2.31"
    if ! printf '%s\n%s\n' "$required_version" "$glibc_version" | sort -V -C; then
        log_warning "GLIBC $glibc_version detected. Binary requires GLIBC $required_version or higher."
        log_warning "Consider using 'pip install giv' instead for better compatibility."
        
        # Skip interactive prompt in dry-run mode
        if [[ "$dry_run" == "true" ]]; then
            log_info "In dry-run mode, would ask user to continue with installation"
            return 0
        fi
        
        # Ask user if they want to continue
        echo -n "Continue with binary installation anyway? [y/N]: "
        read -r response
        case "$response" in
            [yY]|[yY][eE][sS])
                log_info "Continuing with binary installation..."
                return 0
                ;;
            *)
                log_info "Installation cancelled. Try: pip install giv"
                exit 1
                ;;
        esac
    fi
    
    return 0
}

# Validate installation source and provide helpful guidance
validate_install_source() {
    # Check if this script is being run from the correct repository
    if [[ "$REPO" != "fwdslsh/giv" ]]; then
        log_error "This installation script is for repository: $REPO"
        log_error "To install giv, please use the correct installation command:"
        echo
        echo "  curl -fsSL https://raw.githubusercontent.com/fwdslsh/giv/main/install.sh | sh"
        echo
        log_error "If you meant to install a different tool, please check the documentation"
        exit 1
    fi
    
    # Detect common mistakes in the download URL
    local script_url="${BASH_SOURCE[0]}"
    if [[ "$script_url" == *"catalog"* ]]; then
        log_error "It appears you're using the wrong repository URL"
        log_error "To install giv, please use:"
        echo
        echo "  curl -fsSL https://raw.githubusercontent.com/fwdslsh/giv/main/install.sh | sh"
        echo
        log_error "You used a URL containing 'catalog' - please check the documentation"
        exit 1
    fi
}

# Get latest release tag from GitHub
get_latest_version() {
    local api_url="https://api.github.com/repos/${REPO}/releases/latest"
    local version=""
    
    if command -v curl >/dev/null 2>&1; then
        version=$(curl -s --max-time 10 --fail "$api_url" 2>/dev/null | grep '"tag_name":' | sed -E 's/.*"([^"]+)".*/\1/' | head -n1)
    elif command -v wget >/dev/null 2>&1; then
        version=$(wget -qO- --timeout=10 "$api_url" 2>/dev/null | grep '"tag_name":' | sed -E 's/.*"([^"]+)".*/\1/' | head -n1)
    else
        log_error "Neither curl nor wget is available. Please install one of them."
        exit 1
    fi
    
    if [[ -z "$version" ]]; then
        log_error "Failed to get latest version from GitHub API"
        log_error "This could be due to network issues or API rate limiting"
        log_error "Please specify a version with --version flag or try again later"
        log_error ""
        log_error "If you're using the wrong installation URL, the correct command is:"
        echo "  curl -fsSL https://raw.githubusercontent.com/fwdslsh/giv/main/install.sh | sh"
        exit 1
    fi
    
    echo "$version"
}

# Check if binary is already installed
check_existing_installation() {
    local install_path="$1"
    
    if [[ -f "$install_path" ]]; then
        local current_version
        if current_version=$("$install_path" --version 2>/dev/null | head -n1); then
            echo "$current_version"
            return 0
        else
            return 1
        fi
    else
        return 1
    fi
}

# Download binary
download_binary() {
    local version="$1"
    local platform="$2"
    local temp_file="$3"
    
    local download_url="https://github.com/${REPO}/releases/download/${version}/giv-${platform}"
    
    log_info "Downloading giv ${version} for ${platform}..."
    log_info "URL: $download_url"
    
    if command -v curl >/dev/null 2>&1; then
        if ! curl -fL --progress-bar "$download_url" -o "$temp_file"; then
            log_error "Failed to download binary from: $download_url"
            log_error ""
            log_error "This could be due to:"
            log_error "  • Network connectivity issues"
            log_error "  • Invalid version: $version"
            log_error "  • Unsupported platform: $platform"
            log_error "  • Using wrong installation URL"
            log_error ""
            log_error "Correct installation command:"
            echo "  curl -fsSL https://raw.githubusercontent.com/fwdslsh/giv/main/install.sh | sh"
            return 1
        fi
    elif command -v wget >/dev/null 2>&1; then
        if ! wget --progress=bar:force "$download_url" -O "$temp_file"; then
            log_error "Failed to download binary from: $download_url"
            log_error ""
            log_error "This could be due to:"
            log_error "  • Network connectivity issues"
            log_error "  • Invalid version: $version"
            log_error "  • Unsupported platform: $platform"
            log_error "  • Using wrong installation URL"
            log_error ""
            log_error "Correct installation command:"
            echo "  curl -fsSL https://raw.githubusercontent.com/fwdslsh/giv/main/install.sh | sh"
            return 1
        fi
    else
        log_error "Neither curl nor wget is available"
        return 1
    fi
    
    return 0
}

# Install binary
install_binary() {
    local temp_file="$1"
    local install_path="$2"
    local use_sudo="$3"
    
    # Create directory if it doesn't exist
    local install_dir
    install_dir=$(dirname "$install_path")
    
    if [[ ! -d "$install_dir" ]]; then
        log_info "Creating directory: $install_dir"
        if [[ "$use_sudo" == "true" ]]; then
            sudo mkdir -p "$install_dir"
        else
            mkdir -p "$install_dir"
        fi
    fi
    
    # Install binary
    log_info "Installing to: $install_path"
    if [[ "$use_sudo" == "true" ]]; then
        sudo cp "$temp_file" "$install_path"
        sudo chmod +x "$install_path"
    else
        cp "$temp_file" "$install_path"
        chmod +x "$install_path"
    fi
    
    return 0
}

# Verify installation
verify_installation() {
    local install_path="$1"
    
    if [[ ! -f "$install_path" ]]; then
        log_error "Binary not found at $install_path"
        return 1
    fi
    
    if [[ ! -x "$install_path" ]]; then
        log_error "Binary is not executable: $install_path"
        return 1
    fi
    
    local version
    if ! version=$("$install_path" --version 2>/dev/null); then
        log_error "Binary does not execute correctly"
        return 1
    fi
    
    log_success "Installation verified: $version"
    return 0
}

# Add to PATH if needed
check_path() {
    local install_dir="$1"
    
    if [[ ":$PATH:" != *":$install_dir:"* ]]; then
        log_warning "Directory $install_dir is not in your PATH"
        
        local shell_rc
        case "$SHELL" in
            */bash) shell_rc="$HOME/.bashrc";;
            */zsh)  shell_rc="$HOME/.zshrc";;
            */fish) shell_rc="$HOME/.config/fish/config.fish";;
            *)      shell_rc="$HOME/.profile";;
        esac
        
        echo
        log_info "To add it to your PATH, run:"
        echo "    echo 'export PATH=\"$install_dir:\$PATH\"' >> $shell_rc"
        echo "    source $shell_rc"
        echo
        log_info "Or restart your shell"
    fi
}

# Main installation function
main() {
    local version=""
    local install_dir=""
    local force=false
    local dry_run=false
    local user_install=false
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -v|--version)
                version="$2"
                shift 2
                ;;
            -d|--dir)
                install_dir="$2"
                shift 2
                ;;
            -u|--user)
                user_install=true
                shift
                ;;
            -f|--force)
                force=true
                shift
                ;;
            --dry-run)
                dry_run=true
                shift
                ;;
            *)
                log_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # Check environment variables
    if [[ -n "${GIV_VERSION:-}" ]]; then
        version="$GIV_VERSION"
    fi
    
    if [[ -n "${GIV_INSTALL_DIR:-}" ]]; then
        install_dir="$GIV_INSTALL_DIR"
    fi
    
    if [[ -n "${GIV_FORCE:-}" ]]; then
        force=true
    fi
    
    # Validate installation source early
    validate_install_source
    
    # Show banner (but not for help or dry-run)
    if [[ "$dry_run" != "true" ]]; then
        show_banner
    fi
    
    # Determine installation directory
    if [[ -z "$install_dir" ]]; then
        if [[ "$user_install" == "true" ]]; then
            install_dir="$USER_INSTALL_DIR"
        else
            install_dir="$DEFAULT_INSTALL_DIR"
        fi
    fi
    
    local install_path="$install_dir/$BINARY_NAME"
    local use_sudo=false
    
    # Check if we need sudo
    if [[ ! -w "$install_dir" ]] && [[ "$install_dir" != "$USER_INSTALL_DIR"* ]]; then
        use_sudo=true
        log_info "Installation to $install_dir requires sudo privileges"
    fi
    
    # Detect platform
    local platform
    platform=$(detect_platform)
    log_info "Detected platform: $platform"
    
    # Check GLIBC compatibility on Linux
    check_glibc_compatibility "$dry_run"
    
    # Get version
    if [[ -z "$version" ]]; then
        log_info "Getting latest release version..."
        version=$(get_latest_version)
        if [[ -z "$version" ]]; then
            log_error "Failed to get latest version"
            exit 1
        fi
    fi
    
    log_info "Installing giv version: $version"
    
    # Check existing installation
    if [[ "$force" == "false" ]]; then
        local current_version
        if current_version=$(check_existing_installation "$install_path"); then
            log_info "Found existing installation: $current_version"
            if [[ "$current_version" == *"$version"* ]]; then
                log_success "giv $version is already installed at $install_path"
                exit 0
            else
                log_info "Upgrading from $current_version to $version"
            fi
        fi
    fi
    
    if [[ "$dry_run" == "true" ]]; then
        echo
        log_info "DRY RUN - Would perform the following actions:"
        echo "  • Download: giv-$platform from $version"
        echo "  • Install to: $install_path"
        echo "  • Use sudo: $use_sudo"
        echo "  • Platform: $platform"
        exit 0
    fi
    
    # Create temporary file
    local temp_file
    temp_file=$(mktemp)
    trap "rm -f '$temp_file'" EXIT
    
    # Download binary
    if ! download_binary "$version" "$platform" "$temp_file"; then
        exit 1
    fi
    
    # Install binary
    if ! install_binary "$temp_file" "$install_path" "$use_sudo"; then
        exit 1
    fi
    
    # Verify installation
    if ! verify_installation "$install_path"; then
        exit 1
    fi
    
    # Check PATH
    check_path "$install_dir"
    
    echo
    log_success "giv has been installed successfully!"
    log_info "Run 'giv --help' to get started"
    
    # Show quick start
    echo
    echo "Quick start:"
    echo "  giv init                    # Initialize giv in your project"
    echo "  giv config set api.key KEY  # Set your API key"
    echo "  giv message --dry-run       # Test without API call"
}

# Run main function
main "$@"