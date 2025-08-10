#!/usr/bin/env python3
"""
Ultra-simplified binary builder for giv CLI.
Uses PyInstaller with minimal configuration - relies on auto-detection.
"""
import platform
import subprocess
import sys
from pathlib import Path


def get_binary_name():
    """Get platform-specific binary name."""
    system = platform.system().lower()
    if system == "darwin":
        system = "macos"
    
    machine = platform.machine().lower()
    if machine in ("x86_64", "amd64"):
        arch = "x86_64"
    elif machine in ("aarch64", "arm64"):
        arch = "arm64"
    else:
        arch = machine
    
    binary_name = f"giv-{system}-{arch}"
    if system == "windows":
        binary_name += ".exe"
    
    return binary_name


def build_binary():
    """Build binary with minimal PyInstaller configuration."""
    project_root = Path(__file__).parent.parent
    main_script = project_root / "giv" / "__main__.py"
    templates_dir = project_root / "giv" / "templates"
    dist_dir = project_root / "dist"
    
    # Create dist directory
    dist_dir.mkdir(exist_ok=True)
    
    binary_name = get_binary_name()
    print(f"Building {binary_name}...")
    
    # Determine platform-specific settings
    is_windows = platform.system().lower() == "windows"
    
    # Use appropriate path separator for --add-data (Windows uses semicolon, Unix uses colon)
    path_separator = ";" if is_windows else ":"
    add_data_param = f"{templates_dir}{path_separator}giv/templates"
    
    # PyInstaller command optimized for compatibility
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--name", binary_name,
        "--distpath", str(dist_dir),
        "--add-data", add_data_param,
        "--collect-submodules", "giv",  # This handles most imports automatically
        "--noupx",  # Disable UPX compression for better compatibility
        str(main_script)
    ]
    
    # Add --strip flag only on Unix-like systems (not supported on Windows)
    if not is_windows:
        cmd.insert(-1, "--strip")  # Insert before the script path
    
    try:
        subprocess.run(cmd, check=True, cwd=project_root)
        print(f"Binary built successfully: {dist_dir / binary_name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Build failed with exit code: {e.returncode}")
        return False


def main():
    """Entry point for Poetry script."""
    if not build_binary():
        sys.exit(1)


if __name__ == "__main__":
    main()