# Troubleshooting Guide

This guide covers common issues and their solutions when installing and using giv.

## Installation Issues

### Wrong Installation URL

**Problem:** Error like `Failed to download binary` or seeing `-e` prefixes in installation output.

**Cause:** Using an incorrect repository URL in the installation command.

**Symptoms:**
- Error messages with `-e` prefixes appearing literally
- Download failures from wrong repository
- Script trying to install from `catalog` instead of `giv`

**Solution:**
Always use the correct installation command:
```bash
curl -fsSL https://raw.githubusercontent.com/fwdslsh/giv/main/install.sh | sh
```

**Common Mistakes:**
❌ `curl -fsSL https://raw.githubusercontent.com/fwdslsh/catalog/main/install.sh | sh`
❌ `curl -fsSL https://raw.githubusercontent.com/fwdslsh/giv/master/install.sh | sh`
❌ `curl -fsSL https://github.com/fwdslsh/giv/install.sh | sh`

✅ `curl -fsSL https://raw.githubusercontent.com/fwdslsh/giv/main/install.sh | sh`

**Verification:**
After installation, verify it worked:
```bash
giv --version
```

### Linux: GLIBC Version Compatibility

**Problem:** Error like `GLIBC_2.XX not found` when running the binary.

**Cause:** The binary was built on a newer system and requires a newer version of GLIBC than your system provides.

**Solutions:**

1. **Check your GLIBC version:**
   ```bash
   ldd --version
   ```

2. **If GLIBC < 2.31, use alternative installation methods:**

   **Option A: Install via pip (recommended)**
   ```bash
   pip install giv
   ```

   **Option B: Use the install script (auto-detects compatibility)**
   ```bash
   curl -fsSL https://raw.githubusercontent.com/fwdslsh/giv/main/install.sh | sh
   ```

   **Option C: Build from source**
   ```bash
   git clone https://github.com/fwdslsh/giv.git
   cd giv
   pip install .
   ```

**System Compatibility:**
- **Supported:** Ubuntu 20.04+, RHEL 8+, Debian 10+, SUSE 15+
- **Minimum GLIBC:** 2.31 (released in 2020)
- **If unsure:** Run `ldd --version` to check your version

### macOS: Security and Permissions

**Problem:** "giv cannot be opened because the developer cannot be verified"

**Solutions:**

1. **Allow the binary to run:**
   ```bash
   sudo spctl --master-disable
   # Or for this specific file:
   sudo xattr -rd com.apple.quarantine /usr/local/bin/giv
   ```

2. **Alternative: Install via Homebrew (signed)**
   ```bash
   brew tap giv-cli/tap
   brew install giv
   ```

### Windows: Antivirus False Positives

**Problem:** Antivirus software flags the binary as suspicious.

**Cause:** PyInstaller-created executables sometimes trigger heuristic detection.

**Solutions:**

1. **Add exception to antivirus** for the giv.exe file
2. **Install via Scoop (verified):**
   ```powershell
   scoop bucket add giv-cli https://github.com/giv-cli/scoop-bucket
   scoop install giv
   ```
3. **Install via pip:**
   ```powershell
   pip install giv
   ```

## Runtime Issues

### API Configuration

**Problem:** "API key not found" or connection errors.

**Solutions:**

1. **Set up your API key:**
   ```bash
   # OpenAI
   giv config set api.key sk-your-key-here
   
   # Custom endpoint
   giv config set api.base_url https://your-api.com/v1
   giv config set api.key your-key
   ```

2. **Test connection:**
   ```bash
   giv config test
   ```

3. **Check configuration:**
   ```bash
   giv config list
   ```

### Git Repository Issues

**Problem:** "Not a git repository" or permission errors.

**Solutions:**

1. **Ensure you're in a git repository:**
   ```bash
   git status
   ```

2. **Initialize git if needed:**
   ```bash
   git init
   ```

3. **Check file permissions:**
   ```bash
   ls -la .git/
   ```

### Performance Issues

**Problem:** Commands are slow or hang.

**Debugging:**

1. **Enable verbose mode:**
   ```bash
   giv --verbose message
   ```

2. **Check diff size:**
   ```bash
   git diff --stat
   ```

3. **Use path limiting for large repos:**
   ```bash
   giv message -- src/
   ```

## 🐳 Docker Troubleshooting

### Common Issues

#### Permission Denied
If you encounter a permission denied error when running Docker commands, ensure your user is added to the `docker` group:

```bash
sudo usermod -aG docker $USER
newgrp docker
```

#### Network Issues
If the container cannot access the internet, check your Docker network settings or try restarting the Docker service:

```bash
sudo systemctl restart docker
```

## Getting Help

If you're still experiencing issues:

1. **Check existing issues:** [GitHub Issues](https://github.com/fwdslsh/giv/issues)
2. **Create a new issue** with:
   - Your operating system and version
   - GLIBC version (Linux): `ldd --version`
   - Python version (if using pip): `python --version`
   - Complete error message
   - Steps to reproduce

3. **Community support:** [GitHub Discussions](https://github.com/fwdslsh/giv/discussions)

## Diagnostic Information

When reporting issues, include this diagnostic information:

```bash
# System information
uname -a
ldd --version  # Linux only

# giv information
giv --version
giv config list

# Git information
git --version
git status
```