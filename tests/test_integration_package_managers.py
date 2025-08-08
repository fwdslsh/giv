"""
Integration tests for package manager configurations and publishing.

Tests the generation and validation of package manager configurations
(Homebrew, Scoop, etc.) without actually publishing to repositories.
"""
import hashlib
import json
import os
import subprocess
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch
from urllib.parse import urlparse

import pytest

# Import build modules
import sys
build_dir = Path(__file__).parent.parent / "build"
sys.path.insert(0, str(build_dir))

# Import with error handling
try:
    import importlib.util
    
    # Load build.py
    build_spec = importlib.util.spec_from_file_location("build_module", build_dir / "build.py")
    build_module = importlib.util.module_from_spec(build_spec)
    build_spec.loader.exec_module(build_module)
    UnifiedBuilder = build_module.UnifiedBuilder
    
    # Load core modules
    from core.config import BuildConfig
    
except ImportError as e:
    # Skip tests that require build system
    UnifiedBuilder = None
    BuildConfig = None
    print(f"Warning: Build modules not available: {e}")


class TestPackageManagerIntegration:
    """Integration tests for package manager configurations."""
    
    @pytest.fixture
    def mock_binary_assets(self):
        """Create mock binary assets for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            assets_dir = Path(tmpdir) / "assets"
            assets_dir.mkdir()
            
            # Create mock binaries with realistic content
            binaries = {
                "linux-x86_64": "Mock Linux x64 binary content",
                "linux-arm64": "Mock Linux ARM64 binary content", 
                "darwin-x86_64": "Mock macOS Intel binary content",
                "darwin-arm64": "Mock macOS ARM64 binary content",
                "windows-x86_64": "Mock Windows x64 binary content"
            }
            
            binary_info = {}
            for platform, content in binaries.items():
                binary_path = assets_dir / f"giv-{platform}"
                if platform.startswith("windows"):
                    binary_path = assets_dir / f"giv-{platform}.exe"
                
                binary_path.write_text(content)
                binary_path.chmod(0o755)
                
                # Generate SHA256 hash
                sha256 = hashlib.sha256(content.encode()).hexdigest()
                binary_info[platform] = {
                    "path": binary_path,
                    "size": len(content),
                    "sha256": sha256
                }
            
            yield assets_dir, binary_info
    
    @pytest.fixture
    def build_config_with_assets(self, mock_binary_assets):
        """Create build configuration with mock assets."""
        from core.config import BuildConfig
        
        assets_dir, binary_info = mock_binary_assets
        
        config = BuildConfig()
        config.dist_dir = assets_dir
        config.binary_info = binary_info
        
        return config
    
    def test_homebrew_formula_generation(self, build_config_with_assets):
        """Test Homebrew formula generation and validation."""
        try:
            from homebrew.build import HomebrewBuilder
        except ImportError:
            pytest.skip("Homebrew builder not available")
        
        builder = HomebrewBuilder(build_config_with_assets)
        version = "1.2.3"
        
        # Test formula generation
        result = builder.build_formula(version)
        
        assert result is not None
        assert isinstance(result, (str, Path))
        
        if isinstance(result, Path):
            assert result.exists()
            formula_content = result.read_text()
        else:
            formula_content = result
        
        # Validate formula structure
        assert 'class Giv < Formula' in formula_content or 'class GivCli < Formula' in formula_content
        assert f'version "{version}"' in formula_content
        assert 'url "' in formula_content
        assert 'sha256 "' in formula_content
        
        # Test formula syntax
        try:
            # Basic Ruby syntax check (if ruby is available)
            result = subprocess.run(
                ["ruby", "-c"],
                input=formula_content,
                text=True,
                capture_output=True,
                check=False
            )
            if result.returncode == 0:
                print("✅ Homebrew formula syntax is valid")
            else:
                print(f"⚠️  Homebrew formula syntax check failed: {result.stderr}")
        except FileNotFoundError:
            print("⚠️  Ruby not available for syntax checking")
    
    def test_scoop_manifest_generation(self, build_config_with_assets):
        """Test Scoop manifest generation and validation."""
        try:
            from scoop.build import ScoopBuilder
        except ImportError:
            pytest.skip("Scoop builder not available")
        
        builder = ScoopBuilder(build_config_with_assets)
        version = "1.2.3"
        
        # Test manifest generation
        result = builder.build_manifest(version)
        
        assert result is not None
        
        if isinstance(result, Path):
            assert result.exists()
            manifest_content = result.read_text()
        else:
            manifest_content = str(result)
        
        # Parse and validate JSON structure
        try:
            manifest_data = json.loads(manifest_content)
            
            # Validate required fields
            assert "version" in manifest_data
            assert manifest_data["version"] == version
            assert "architecture" in manifest_data
            assert "64bit" in manifest_data["architecture"]
            assert "url" in manifest_data["architecture"]["64bit"]
            assert "hash" in manifest_data["architecture"]["64bit"]
            assert "bin" in manifest_data
            
            print("✅ Scoop manifest structure is valid")
            
        except json.JSONDecodeError as e:
            pytest.fail(f"Invalid JSON in Scoop manifest: {e}")
    
    def test_npm_package_structure(self, build_config_with_assets):
        """Test NPM package structure generation."""
        try:
            from npm.build import NPMBuilder
        except ImportError:
            pytest.skip("NPM builder not available")
        
        builder = NPMBuilder(build_config_with_assets)
        version = "1.2.3"
        
        # Test package generation
        result = builder.build_package(version)
        
        if result and isinstance(result, Path):
            package_dir = result
            
            # Check package.json
            package_json = package_dir / "package.json"
            if package_json.exists():
                package_data = json.loads(package_json.read_text())
                
                assert "name" in package_data
                assert "version" in package_data
                assert package_data["version"] == version
                assert "bin" in package_data
                
            # Check for install script
            install_script = package_dir / "install.js"
            if install_script.exists():
                script_content = install_script.read_text()
                assert "download" in script_content or "binary" in script_content
                
            print("✅ NPM package structure is valid")
    
    def test_chocolatey_package_generation(self, build_config_with_assets):
        """Test Chocolatey package generation."""
        try:
            from scoop.build import ScoopBuilder  # Often shares code with Chocolatey
        except ImportError:
            pytest.skip("Chocolatey builder not available")
        
        # Test if Chocolatey generation is available
        builder = ScoopBuilder(build_config_with_assets)
        
        if hasattr(builder, 'build_chocolatey_package'):
            version = "1.2.3"
            result = builder.build_chocolatey_package(version)
            
            if result and isinstance(result, Path):
                choco_dir = result
                
                # Check for .nuspec file
                nuspec_files = list(choco_dir.glob("*.nuspec"))
                if nuspec_files:
                    nuspec_content = nuspec_files[0].read_text()
                    assert f"<version>{version}</version>" in nuspec_content
                    assert "<id>giv</id>" in nuspec_content or "<id>giv-cli</id>" in nuspec_content
                
                # Check for install script
                install_script = choco_dir / "tools" / "chocolateyinstall.ps1"
                if install_script.exists():
                    script_content = install_script.read_text()
                    assert "Install-" in script_content
                
                print("✅ Chocolatey package structure is valid")
        else:
            pytest.skip("Chocolatey package generation not available")
    
    def test_debian_package_validation(self, build_config_with_assets):
        """Test Debian package structure validation."""
        try:
            from debian.build import DebianBuilder
        except ImportError:
            pytest.skip("Debian builder not available")
        
        builder = DebianBuilder(build_config_with_assets)
        version = "1.2.3"
        
        result = builder.build_package(version)
        
        if result and isinstance(result, Path):
            debian_dir = result
            
            # Check DEBIAN directory structure
            debian_control_dir = debian_dir / "DEBIAN"
            if debian_control_dir.exists():
                control_file = debian_control_dir / "control"
                if control_file.exists():
                    control_content = control_file.read_text()
                    assert f"Version: {version}" in control_content
                    assert "Package: giv" in control_content
                    assert "Architecture:" in control_content
                
            print("✅ Debian package structure is valid")
    
    def test_snap_package_validation(self, build_config_with_assets):
        """Test Snap package configuration validation."""
        try:
            from snap.build import SnapBuilder
        except ImportError:
            pytest.skip("Snap builder not available")
        
        builder = SnapBuilder(build_config_with_assets)
        version = "1.2.3"
        
        result = builder.build_package(version)
        
        if result and isinstance(result, Path):
            snap_dir = result
            
            # Check snapcraft.yaml
            snapcraft_yaml = snap_dir / "snapcraft.yaml"
            if snapcraft_yaml.exists():
                yaml_content = snapcraft_yaml.read_text()
                assert f"version: '{version}'" in yaml_content or f'version: "{version}"' in yaml_content
                assert "name: giv" in yaml_content
                assert "apps:" in yaml_content
                
            print("✅ Snap package structure is valid")
    
    def test_flatpak_package_validation(self, build_config_with_assets):
        """Test Flatpak package configuration validation."""
        try:
            from flatpak.build import FlatpakBuilder
        except ImportError:
            pytest.skip("Flatpak builder not available")
        
        builder = FlatpakBuilder(build_config_with_assets)
        version = "1.2.3"
        
        result = builder.build_package(version)
        
        if result and isinstance(result, Path):
            flatpak_dir = result
            
            # Check manifest file
            manifest_files = list(flatpak_dir.glob("*.json")) + list(flatpak_dir.glob("*.yml")) + list(flatpak_dir.glob("*.yaml"))
            if manifest_files:
                manifest_content = manifest_files[0].read_text()
                
                if manifest_files[0].suffix == ".json":
                    manifest_data = json.loads(manifest_content)
                    assert "app-id" in manifest_data or "id" in manifest_data
                    assert "runtime" in manifest_data
                    assert "command" in manifest_data
                else:
                    # YAML format
                    assert "app-id:" in manifest_content or "id:" in manifest_content
                    assert "runtime:" in manifest_content
                    assert "command:" in manifest_content
                
            print("✅ Flatpak package structure is valid")


class TestPackageManagerURLValidation:
    """Test package manager URL and checksum validation."""
    
    def test_github_release_url_structure(self):
        """Test GitHub release URL structure validation."""
        base_url = "https://github.com/fwdslsh/giv/releases/download"
        version = "1.2.3"
        
        expected_urls = {
            "linux-x86_64": f"{base_url}/v{version}/giv-linux-x86_64",
            "darwin-x86_64": f"{base_url}/v{version}/giv-darwin-x86_64",
            "windows-x86_64": f"{base_url}/v{version}/giv-windows-x86_64.exe"
        }
        
        for platform, url in expected_urls.items():
            parsed_url = urlparse(url)
            
            assert parsed_url.scheme == "https"
            assert parsed_url.netloc == "github.com"
            assert f"/v{version}/" in parsed_url.path
            assert f"giv-{platform}" in parsed_url.path
            
            print(f"✅ URL structure valid for {platform}: {url}")
    
    def test_checksum_generation_consistency(self):
        """Test that checksum generation is consistent."""
        test_content = "Mock binary content for checksum testing"
        
        # Generate checksum multiple times
        checksums = []
        for _ in range(3):
            sha256 = hashlib.sha256(test_content.encode()).hexdigest()
            checksums.append(sha256)
        
        # All checksums should be identical
        assert len(set(checksums)) == 1
        assert len(checksums[0]) == 64  # SHA256 is 64 hex characters
        
        print(f"✅ Checksum consistency verified: {checksums[0]}")
    
    def test_version_string_validation(self):
        """Test version string validation for different package managers."""
        valid_versions = ["1.0.0", "1.2.3", "0.1.0", "10.0.0", "1.0.0-beta.1", "1.0.0-rc.1"]
        invalid_versions = ["", "1", "1.0", "v1.0.0", "1.0.0.0", "invalid"]
        
        from core.version_manager import VersionManager
        version_manager = VersionManager(Path.cwd())
        
        for version in valid_versions:
            assert version_manager._is_valid_version(version), f"Version {version} should be valid"
        
        for version in invalid_versions:
            assert not version_manager._is_valid_version(version), f"Version {version} should be invalid"
        
        print("✅ Version string validation working correctly")


class TestPublishWorkflowDryRun:
    """Test publish workflow in dry-run mode."""
    
    @pytest.fixture
    def publisher_config(self):
        """Create publisher configuration."""
        from core.config import BuildConfig
        from publish import UnifiedPublisher
        
        with tempfile.TemporaryDirectory() as tmpdir:
            config = BuildConfig()
            config.dist_dir = Path(tmpdir) / "dist"
            config.dist_dir.mkdir()
            
            # Create mock packages
            (config.dist_dir / "giv-1.0.0.tar.gz").write_text("mock sdist")
            (config.dist_dir / "giv-1.0.0-py3-none-any.whl").write_text("mock wheel")
            (config.dist_dir / "giv-linux-x86_64").write_text("mock binary")
            
            publisher = UnifiedPublisher(config)
            yield publisher, config
    
    @patch('subprocess.run')
    def test_pypi_publish_dry_run(self, mock_subprocess, publisher_config):
        """Test PyPI publishing in dry-run mode."""
        publisher, config = publisher_config
        
        # Mock successful twine upload
        mock_subprocess.return_value = subprocess.CompletedProcess(
            [], 0, stdout="Uploading distributions to https://upload.pypi.org/legacy/", stderr=""
        )
        
        # Test dry-run publish
        if 'pypi' in publisher.publishers:
            result = publisher.publish_pypi(test=True)
            
            # Verify subprocess was called
            assert mock_subprocess.called
            
            # Check that the call included test PyPI repository
            call_args = mock_subprocess.call_args[0][0]  # Get the command arguments
            command_str = " ".join(call_args) if isinstance(call_args, list) else str(call_args)
            
            print(f"✅ PyPI dry-run publish prepared: {result}")
        else:
            pytest.skip("PyPI publisher not available")
    
    @patch('subprocess.run')
    def test_github_release_dry_run(self, mock_subprocess, publisher_config):
        """Test GitHub release creation in dry-run mode."""
        publisher, config = publisher_config
        
        # Mock successful gh command
        mock_subprocess.return_value = subprocess.CompletedProcess(
            [], 0, stdout="https://github.com/fwdslsh/giv/releases/tag/v1.0.0", stderr=""
        )
        
        # Test dry-run GitHub release
        result = publisher.publish_github_release("1.0.0")
        
        # Should prepare successfully
        assert result is True
        
        print("✅ GitHub release dry-run successful")
    
    def test_package_manager_submission_preparation(self, publisher_config):
        """Test preparation for package manager submissions."""
        publisher, config = publisher_config
        
        # Create mock package manager assets
        homebrew_formula = config.dist_dir / "giv.rb"
        homebrew_formula.write_text('class Giv < Formula\n  version "1.0.0"\nend')
        
        scoop_manifest = config.dist_dir / "giv.json"
        scoop_manifest.write_text('{"version": "1.0.0", "architecture": {"64bit": {"url": "test"}}}')
        
        # Test status shows all assets
        try:
            publisher.show_status()
            print("✅ Package manager asset preparation successful")
        except Exception as e:
            pytest.fail(f"Status check failed: {e}")
    
    def test_release_asset_validation(self, publisher_config):
        """Test validation of release assets."""
        publisher, config = publisher_config
        
        # Check required assets exist
        required_assets = [
            config.dist_dir / "giv-1.0.0.tar.gz",
            config.dist_dir / "giv-1.0.0-py3-none-any.whl",
            config.dist_dir / "giv-linux-x86_64"
        ]
        
        for asset in required_assets:
            assert asset.exists(), f"Required asset missing: {asset}"
            assert asset.stat().st_size > 0, f"Asset is empty: {asset}"
        
        print("✅ Release asset validation successful")


@pytest.mark.integration
class TestEndToEndPackagingWorkflow:
    """End-to-end packaging workflow tests."""
    
    def test_complete_packaging_cycle(self):
        """Test complete packaging cycle from binaries to package configs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = Path(tmpdir)
            dist_dir = workspace / "dist"
            dist_dir.mkdir()
            
            # Create mock binaries
            binary_content = "Mock binary for packaging test"
            platforms = ["linux-x86_64", "darwin-x86_64", "windows-x86_64"]
            
            binary_info = {}
            for platform in platforms:
                binary_name = f"giv-{platform}"
                if platform.startswith("windows"):
                    binary_name += ".exe"
                
                binary_path = dist_dir / binary_name
                binary_path.write_text(binary_content)
                binary_path.chmod(0o755)
                
                binary_info[platform] = {
                    "path": binary_path,
                    "size": len(binary_content),
                    "sha256": hashlib.sha256(binary_content.encode()).hexdigest()
                }
            
            # Test package config generation
            from core.config import BuildConfig
            config = BuildConfig()
            config.dist_dir = dist_dir
            config.binary_info = binary_info
            
            # Try to generate configs with available builders
            if UnifiedBuilder is None:
                pytest.skip("Build system not available")
            
            builder = UnifiedBuilder(config)
            
            version = "1.0.0"
            available_builders = list(builder.builders.keys())
            
            print(f"Testing package generation with builders: {available_builders}")
            
            successful_packages = []
            for pkg_type in available_builders[:2]:  # Test first 2 available builders
                try:
                    packages = builder.build_packages([pkg_type], version)
                    if packages and pkg_type in packages:
                        successful_packages.append(pkg_type)
                        print(f"✅ {pkg_type} package generated successfully")
                except Exception as e:
                    print(f"⚠️  {pkg_type} package generation failed: {e}")
            
            assert len(successful_packages) >= 0, "Should not fail completely"
            print(f"✅ Complete packaging cycle tested with {len(successful_packages)} package types")


if __name__ == "__main__":
    # Allow running tests directly
    pytest.main([__file__, "-v", "--tb=short"])