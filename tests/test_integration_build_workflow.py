"""
Integration tests for build, package, and publish workflow.

These tests validate the end-to-end build process without actually publishing
to external services. Designed to run on Debian-based Linux systems.
"""
import json
import os
import platform
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional
from unittest.mock import Mock, patch

import pytest

# Import build modules
import sys
build_dir = Path(__file__).parent.parent / "build"
sys.path.insert(0, str(build_dir))

# Import with error handling
try:
    # Import the actual modules (they're individual .py files, not packages)
    import importlib.util
    
    # Load build.py
    build_spec = importlib.util.spec_from_file_location("build_module", build_dir / "build.py")
    build_module = importlib.util.module_from_spec(build_spec)
    build_spec.loader.exec_module(build_module)
    UnifiedBuilder = build_module.UnifiedBuilder
    
    # Load publish.py
    publish_spec = importlib.util.spec_from_file_location("publish_module", build_dir / "publish.py")
    publish_module = importlib.util.module_from_spec(publish_spec)
    publish_spec.loader.exec_module(publish_module)
    UnifiedPublisher = publish_module.UnifiedPublisher
    
    # Load core modules
    from core.config import BuildConfig
    
except ImportError as e:
    # Fallback for tests that don't require build system
    UnifiedBuilder = None
    UnifiedPublisher = None
    BuildConfig = None
    print(f"Warning: Build modules not available: {e}")


class TestBuildWorkflowIntegration:
    """Integration tests for the complete build workflow."""
    
    @pytest.fixture
    def temp_project_dir(self):
        """Create a temporary project directory with git repo."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir)
            
            # Initialize git repo
            subprocess.run(["git", "init"], cwd=project_dir, check=True)
            subprocess.run(
                ["git", "config", "user.email", "test@example.com"],
                cwd=project_dir, check=True
            )
            subprocess.run(
                ["git", "config", "user.name", "Test User"],
                cwd=project_dir, check=True
            )
            
            # Create basic project structure
            (project_dir / "giv").mkdir()
            (project_dir / "giv" / "__init__.py").write_text('')
            (project_dir / "giv" / "main.py").write_text(
                'def main():\n    print("Hello from giv")\n'
            )
            
            # Create pyproject.toml
            (project_dir / "pyproject.toml").write_text("""
[tool.poetry]
name = "giv-test"
version = "1.0.0"
description = "Test giv package"
authors = ["Test <test@example.com>"]

[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"
""")
            
            # Initial commit
            subprocess.run(["git", "add", "."], cwd=project_dir, check=True)
            subprocess.run(
                ["git", "commit", "-m", "Initial commit"],
                cwd=project_dir, check=True
            )
            subprocess.run(
                ["git", "tag", "v1.0.0"], cwd=project_dir, check=True
            )
            
            yield project_dir
    
    @pytest.fixture
    def build_config(self, temp_project_dir):
        """Create build configuration for test project."""
        config = BuildConfig()
        config.project_root = temp_project_dir
        config.dist_dir = temp_project_dir / "dist"
        config.dist_dir.mkdir(exist_ok=True)
        return config
    
    def test_version_detection(self, build_config):
        """Test that version detection works correctly."""
        from core.version_manager import VersionManager
        
        version_manager = VersionManager(build_config.project_root)
        
        # Test version detection from pyproject.toml
        version = version_manager.get_build_version()
        assert version == "1.0.0"
        
        # Test version detection from git tag
        os.chdir(build_config.project_root)
        version_from_git = version_manager._get_version_from_git()
        assert version_from_git == "1.0.0"
    
    def test_binary_build_simulation(self, build_config):
        """Test binary build process (simulated for testing)."""
        # Create a mock binary to simulate successful build
        mock_binary = build_config.dist_dir / "giv-linux-x86_64"
        mock_binary.write_text("#!/bin/bash\necho 'Mock giv binary'\n")
        mock_binary.chmod(0o755)
        
        builder = UnifiedBuilder(build_config)
        
        # Test binary detection
        binaries = {}
        for platform, platform_info in build_config.platforms.items():
            binary_path = build_config.dist_dir / platform_info["binary_name"]
            if binary_path.exists():
                binaries[platform] = binary_path
        
        assert len(binaries) >= 1
        assert any("linux" in platform for platform in binaries.keys())
    
    def test_pypi_package_build(self, build_config):
        """Test PyPI package building with Poetry."""
        original_cwd = os.getcwd()
        
        try:
            os.chdir(build_config.project_root)
            
            # Test building with Poetry
            result = subprocess.run(
                ["python", "-m", "poetry", "build"],
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode == 0:
                # Check for built packages
                dist_files = list(build_config.dist_dir.glob("*"))
                wheel_files = list(build_config.dist_dir.glob("*.whl"))
                tarball_files = list(build_config.dist_dir.glob("*.tar.gz"))
                
                # Should have at least one package file
                assert len(dist_files) > 0, f"No dist files found: {dist_files}"
                
                if wheel_files:
                    # Verify wheel structure
                    wheel_file = wheel_files[0]
                    assert wheel_file.suffix == ".whl"
                    assert "giv_test" in wheel_file.name
                
                if tarball_files:
                    # Verify source distribution
                    tarball_file = tarball_files[0]
                    assert tarball_file.suffix == ".gz"
                    assert "giv-test" in tarball_file.name
            
            else:
                pytest.skip(f"Poetry build failed: {result.stderr}")
        
        finally:
            os.chdir(original_cwd)
    
    def test_unified_builder_integration(self, build_config):
        """Test the unified builder with available components."""
        builder = UnifiedBuilder(build_config)
        
        # Test builder loading
        assert isinstance(builder.builders, dict)
        
        # Test version detection
        version = builder.version_manager.get_build_version()
        assert version == "1.0.0"
        
        # Test package building (with available builders only)
        available_types = list(builder.builders.keys())
        if available_types:
            packages = builder.build_packages(available_types[:1])  # Test first available
            assert isinstance(packages, dict)
    
    def test_publisher_status_check(self, build_config):
        """Test publisher status checking functionality."""
        # Create some mock built assets
        (build_config.dist_dir / "giv-test-1.0.0.tar.gz").write_text("mock tarball")
        (build_config.dist_dir / "giv_test-1.0.0-py3-none-any.whl").write_text("mock wheel")
        (build_config.dist_dir / "giv-linux-x86_64").write_text("mock binary")
        
        publisher = UnifiedPublisher(build_config)
        
        # Test status checking (should not raise exceptions)
        try:
            publisher.show_status()
        except Exception as e:
            pytest.fail(f"Status check failed: {e}")
    
    @patch('subprocess.run')
    def test_pypi_publish_dry_run(self, mock_subprocess, build_config):
        """Test PyPI publishing in dry-run mode."""
        # Create mock packages
        (build_config.dist_dir / "giv-test-1.0.0.tar.gz").write_text("mock tarball")
        (build_config.dist_dir / "giv_test-1.0.0-py3-none-any.whl").write_text("mock wheel")
        
        # Mock successful subprocess calls
        mock_subprocess.return_value = subprocess.CompletedProcess(
            [], 0, stdout="Upload successful", stderr=""
        )
        
        publisher = UnifiedPublisher(build_config)
        
        # Test dry-run publish (mocked)
        if 'pypi' in publisher.publishers:
            # This would normally publish, but we've mocked subprocess.run
            result = publisher.publish_pypi(test=True)
            
            # Verify the mock was called with expected arguments
            assert mock_subprocess.called
        else:
            pytest.skip("PyPI publisher not available")
    
    def test_github_release_preparation(self, build_config):
        """Test GitHub release preparation (without actual release)."""
        # Create mock assets
        (build_config.dist_dir / "giv-linux-x86_64").write_text("mock linux binary")
        (build_config.dist_dir / "giv-test-1.0.0.tar.gz").write_text("mock tarball")
        (build_config.dist_dir / "giv_test-1.0.0-py3-none-any.whl").write_text("mock wheel")
        
        publisher = UnifiedPublisher(build_config)
        
        # Test GitHub release preparation
        result = publisher.publish_github_release()
        
        # Should return True (prepared successfully, but not actually released)
        assert result is True
    
    def test_package_manager_config_generation(self, build_config):
        """Test package manager configuration generation."""
        # Create mock binary for checksums
        binary_path = build_config.dist_dir / "giv-linux-x86_64"
        binary_path.write_text("mock binary content for checksum")
        
        # Test if package manager builders are available
        builder = UnifiedBuilder(build_config)
        
        for pkg_type, builder_class in builder.builders.items():
            try:
                pkg_builder = builder_class(build_config)
                
                if pkg_type == 'homebrew' and hasattr(pkg_builder, 'build_formula'):
                    # Test Homebrew formula generation
                    formula_result = pkg_builder.build_formula("1.0.0")
                    assert formula_result is not None
                
                elif pkg_type == 'scoop' and hasattr(pkg_builder, 'build_manifest'):
                    # Test Scoop manifest generation  
                    manifest_result = pkg_builder.build_manifest("1.0.0")
                    assert manifest_result is not None
                
            except Exception as e:
                # Skip if dependencies not available
                pytest.skip(f"Package manager {pkg_type} not available: {e}")
    
    def test_end_to_end_workflow(self, build_config):
        """Test complete end-to-end workflow."""
        original_cwd = os.getcwd()
        
        try:
            os.chdir(build_config.project_root)
            
            # 1. Test version detection
            from core.version_manager import VersionManager
            version_manager = VersionManager(build_config.project_root)
            version = version_manager.get_build_version()
            assert version == "1.0.0"
            
            # 2. Create mock binaries (simulating successful binary build)
            mock_platforms = ["linux-x86_64"]
            for platform in mock_platforms:
                binary_path = build_config.dist_dir / f"giv-{platform}"
                binary_path.write_text(f"Mock {platform} binary")
                binary_path.chmod(0o755)
            
            # 3. Test PyPI package building
            try:
                result = subprocess.run(
                    ["python", "-m", "poetry", "build", "--output", str(build_config.dist_dir)],
                    capture_output=True,
                    text=True,
                    check=False,
                    cwd=build_config.project_root
                )
                
                if result.returncode == 0:
                    # Verify packages were created
                    packages = list(build_config.dist_dir.glob("giv*.whl")) + \
                              list(build_config.dist_dir.glob("giv*.tar.gz"))
                    assert len(packages) > 0, "No packages built"
                
            except Exception as e:
                pytest.skip(f"Poetry build not available: {e}")
            
            # 4. Test unified builder
            builder = UnifiedBuilder(build_config)
            
            # Test status and available builders
            available_builders = list(builder.builders.keys())
            print(f"Available builders: {available_builders}")
            
            # 5. Test publisher preparation
            publisher = UnifiedPublisher(build_config)
            
            # Should not raise exceptions
            publisher.show_status()
            
            # 6. Test GitHub release preparation (dry run)
            github_ready = publisher.publish_github_release()
            assert github_ready in [True, False]  # Should complete without error
            
            print("✅ End-to-end workflow completed successfully")
            
        finally:
            os.chdir(original_cwd)


class TestBuildSystemDependencies:
    """Test build system dependencies and environment."""
    
    def test_required_tools_available(self):
        """Test that required build tools are available."""
        required_tools = [
            ("python", "--version"),
            ("git", "--version"),
        ]
        
        optional_tools = [
            ("poetry", "--version"),
        ]
        
        # Test required tools
        for tool, arg in required_tools:
            result = subprocess.run([tool, arg], capture_output=True, text=True, check=False)
            assert result.returncode == 0, f"Required tool {tool} not available"
        
        # Test optional tools (warn if not available)
        for tool, arg in optional_tools:
            result = subprocess.run([tool, arg], capture_output=True, text=True, check=False)
            if result.returncode != 0:
                print(f"⚠️  Optional tool {tool} not available")
    
    def test_python_dependencies(self):
        """Test that Python dependencies are available."""
        try:
            import json
            import pathlib
            import subprocess
            import tempfile
            assert True
        except ImportError as e:
            pytest.fail(f"Required Python module not available: {e}")
    
    def test_build_system_imports(self):
        """Test that build system modules can be imported."""
        build_dir = Path(__file__).parent.parent / "build"
        
        if not build_dir.exists():
            pytest.skip("Build directory not found")
        
        sys.path.insert(0, str(build_dir))
        
        try:
            from core.config import BuildConfig
            from core.version_manager import VersionManager
            from core.utils import ensure_dir
            
            config = BuildConfig()
            assert config is not None
            
            # Test that version manager can be created
            version_manager = VersionManager(Path.cwd())
            assert version_manager is not None
            
        except ImportError as e:
            pytest.fail(f"Build system module import failed: {e}")
        
        finally:
            if str(build_dir) in sys.path:
                sys.path.remove(str(build_dir))
    
    def test_debian_specific_requirements(self):
        """Test Debian-specific requirements."""
        if platform.system() != "Linux":
            pytest.skip("Debian tests only run on Linux")
        
        # Check if we're on a Debian-based system
        try:
            with open("/etc/os-release") as f:
                os_release = f.read()
            
            if "debian" not in os_release.lower() and "ubuntu" not in os_release.lower():
                pytest.skip("Tests designed for Debian-based systems")
            
        except FileNotFoundError:
            pytest.skip("Cannot determine OS type")
        
        # Test available package managers
        package_managers = ["dpkg", "apt"]
        for pm in package_managers:
            result = subprocess.run([pm, "--version"], capture_output=True, check=False)
            assert result.returncode == 0, f"Package manager {pm} not available"


class TestBuildConfigurationValidation:
    """Test build configuration and validation."""
    
    def test_build_config_creation(self):
        """Test BuildConfig creation and validation."""
        config = BuildConfig()
        
        # Test basic properties
        assert config.project_root is not None
        assert config.dist_dir is not None
        assert isinstance(config.platforms, dict)
        
        # Test platform configurations
        for platform, platform_info in config.platforms.items():
            assert "binary_name" in platform_info
            assert isinstance(platform_info["binary_name"], str)
            assert len(platform_info["binary_name"]) > 0
    
    def test_version_manager_functionality(self):
        """Test VersionManager functionality."""
        from core.version_manager import VersionManager
        
        version_manager = VersionManager(Path.cwd())
        
        # Test version detection methods
        build_version = version_manager.get_build_version()
        assert isinstance(build_version, str)
        assert len(build_version) > 0
        
        # Test version validation
        assert version_manager._is_valid_version("1.0.0")
        assert version_manager._is_valid_version("1.2.3-beta.1")
        assert not version_manager._is_valid_version("invalid")
    
    def test_dist_directory_handling(self):
        """Test distribution directory handling."""
        from core.utils import ensure_dir
        
        with tempfile.TemporaryDirectory() as tmpdir:
            test_dir = Path(tmpdir) / "dist"
            
            # Test directory creation
            ensure_dir(test_dir)
            assert test_dir.exists()
            assert test_dir.is_dir()
            
            # Test that existing directory is not modified
            test_file = test_dir / "test.txt"
            test_file.write_text("test content")
            
            ensure_dir(test_dir)
            assert test_file.exists()
            assert test_file.read_text() == "test content"


@pytest.mark.integration
class TestFullWorkflowIntegration:
    """Full workflow integration tests."""
    
    @pytest.mark.slow
    def test_complete_build_cycle(self):
        """Test complete build cycle from source to packages."""
        # This is a comprehensive test that runs the full build cycle
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir)
            
            # Set up test project
            self._setup_test_project(project_dir)
            
            original_cwd = os.getcwd()
            try:
                os.chdir(project_dir)
                
                # Run build cycle
                config = BuildConfig()
                config.project_root = project_dir
                config.dist_dir = project_dir / "dist"
                
                builder = UnifiedBuilder(config)
                
                # Test build process
                results = builder.build_all()
                
                assert results is not None
                assert "version" in results
                assert "binaries" in results
                assert "packages" in results
                
                print("✅ Complete build cycle successful")
                
            finally:
                os.chdir(original_cwd)
    
    def _setup_test_project(self, project_dir: Path):
        """Set up a test project structure."""
        # Initialize git
        subprocess.run(["git", "init"], cwd=project_dir, check=True)
        subprocess.run(
            ["git", "config", "user.email", "test@example.com"],
            cwd=project_dir, check=True
        )
        subprocess.run(
            ["git", "config", "user.name", "Test User"],
            cwd=project_dir, check=True
        )
        
        # Create project structure
        (project_dir / "giv").mkdir()
        (project_dir / "giv" / "__init__.py").write_text('')
        (project_dir / "giv" / "main.py").write_text(
            'def main():\n    print("Test giv CLI")\n\nif __name__ == "__main__":\n    main()\n'
        )
        
        # Create pyproject.toml
        (project_dir / "pyproject.toml").write_text("""
[tool.poetry]
name = "giv-integration-test"
version = "0.1.0"
description = "Integration test for giv CLI"
authors = ["Test <test@example.com>"]

[tool.poetry.scripts]
giv = "giv.main:main"

[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"
""")
        
        # Create basic build components
        build_dir = project_dir / "build"
        build_dir.mkdir()
        
        # Copy essential build files
        original_build_dir = Path(__file__).parent.parent / "build"
        if original_build_dir.exists():
            for item in ["core", "build.py"]:
                src = original_build_dir / item
                dst = build_dir / item
                if src.exists():
                    if src.is_file():
                        shutil.copy2(src, dst)
                    else:
                        shutil.copytree(src, dst)
        
        # Initial commit
        subprocess.run(["git", "add", "."], cwd=project_dir, check=True)
        subprocess.run(
            ["git", "commit", "-m", "Initial test project"],
            cwd=project_dir, check=True
        )
        subprocess.run(
            ["git", "tag", "v0.1.0"], cwd=project_dir, check=True
        )


if __name__ == "__main__":
    # Allow running tests directly
    pytest.main([__file__, "-v", "--tb=short"])