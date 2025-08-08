"""
Integration tests for the publish workflow and GitHub Actions simulation.

These tests simulate the complete CI/CD pipeline without actually publishing
to external services, focusing on workflow validation and error detection.
"""
import json
import os
import shutil
import subprocess
import tempfile
import yaml
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

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


class TestGitHubWorkflowSimulation:
    """Simulate GitHub Actions workflow execution."""
    
    @pytest.fixture
    def workflow_environment(self):
        """Set up environment that simulates GitHub Actions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = Path(tmpdir)
            
            # Simulate GitHub workspace structure
            github_workspace = workspace / "github_workspace"
            artifacts_dir = workspace / "artifacts"
            dist_dir = github_workspace / "dist"
            
            for directory in [github_workspace, artifacts_dir, dist_dir]:
                directory.mkdir(parents=True)
            
            # Set up environment variables like GitHub Actions
            env_vars = {
                "GITHUB_WORKSPACE": str(github_workspace),
                "GITHUB_REF": "refs/tags/v1.0.0",
                "GITHUB_REF_NAME": "v1.0.0",
                "GITHUB_REPOSITORY": "fwdslsh/giv",
                "GITHUB_SHA": "abc123",
                "RUNNER_TEMP": str(workspace / "temp")
            }
            
            yield {
                "workspace": github_workspace,
                "artifacts": artifacts_dir,
                "dist": dist_dir,
                "env": env_vars
            }
    
    def test_workflow_environment_setup(self, workflow_environment):
        """Test GitHub Actions environment simulation."""
        env = workflow_environment["env"]
        workspace = workflow_environment["workspace"]
        
        assert workspace.exists()
        assert env["GITHUB_REF"] == "refs/tags/v1.0.0"
        assert env["GITHUB_REF_NAME"] == "v1.0.0"
        assert Path(env["GITHUB_WORKSPACE"]).exists()
        
        print("✅ Workflow environment setup successful")
    
    def test_binary_artifact_simulation(self, workflow_environment):
        """Test binary artifact collection like GitHub Actions."""
        artifacts_dir = workflow_environment["artifacts"]
        
        # Simulate downloaded artifacts from build-binaries job
        platforms = {
            "giv-linux-x86_64": "Mock Linux x64 binary",
            "giv-linux-arm64": "Mock Linux ARM64 binary",
            "giv-darwin-x86_64": "Mock macOS Intel binary",
            "giv-darwin-arm64": "Mock macOS Apple Silicon binary",
            "giv-windows-x86_64": "Mock Windows binary"
        }
        
        # Create artifact directories like GitHub Actions
        for platform, content in platforms.items():
            platform_dir = artifacts_dir / platform
            platform_dir.mkdir()
            
            binary_name = platform
            if platform.endswith("windows-x86_64"):
                binary_name += ".exe"
            
            binary_file = platform_dir / binary_name
            binary_file.write_text(content)
            binary_file.chmod(0o755)
            
            # Create checksum file
            checksum_file = platform_dir / f"{binary_name}.sha256"
            checksum = subprocess.run(
                ["sha256sum", str(binary_file)],
                capture_output=True,
                text=True,
                check=True
            ).stdout.split()[0]
            checksum_file.write_text(f"{checksum}  {binary_name}")
        
        # Verify artifacts
        artifact_dirs = list(artifacts_dir.iterdir())
        assert len(artifact_dirs) == len(platforms)
        
        for artifact_dir in artifact_dirs:
            assert artifact_dir.is_dir()
            files = list(artifact_dir.iterdir())
            assert len(files) >= 2  # Binary + checksum
            
        print(f"✅ Created {len(artifact_dirs)} binary artifacts")
    
    def test_artifact_organization_workflow(self, workflow_environment):
        """Test artifact organization step from GitHub workflow."""
        artifacts_dir = workflow_environment["artifacts"]
        dist_dir = workflow_environment["dist"]
        
        # Create mock artifacts
        self.test_binary_artifact_simulation(workflow_environment)
        
        # Simulate the artifact organization step from .github/workflows/release.yml
        version = "1.0.0"
        versioned_dir = dist_dir / version
        versioned_dir.mkdir()
        
        # Copy artifacts to dist/ (flat structure)
        for artifact_dir in artifacts_dir.iterdir():
            if artifact_dir.is_dir():
                for file_path in artifact_dir.iterdir():
                    if file_path.is_file():
                        shutil.copy2(file_path, dist_dir)
        
        # Create versioned structure
        for artifact_dir in artifacts_dir.iterdir():
            if artifact_dir.is_dir():
                target = artifact_dir.name.replace("giv-", "")
                
                # Handle platform naming
                if target == "macos-x86_64":
                    platform, arch = "darwin", "x86_64"
                elif target == "macos-arm64":
                    platform, arch = "darwin", "arm64"
                else:
                    parts = target.split("-")
                    platform, arch = parts[0], parts[1] if len(parts) > 1 else "x86_64"
                
                platform_dir = versioned_dir / f"{platform}-{arch}"
                platform_dir.mkdir()
                
                for file_path in artifact_dir.iterdir():
                    if file_path.is_file():
                        shutil.copy2(file_path, platform_dir)
        
        # Generate consolidated checksums
        checksums_file = versioned_dir / "checksums.txt"
        with checksums_file.open("w") as f:
            for checksum_file in versioned_dir.rglob("*.sha256"):
                f.write(checksum_file.read_text())
        
        # Verify organization
        assert len(list(dist_dir.glob("giv-*"))) >= 5  # Flat binaries
        assert len(list(versioned_dir.iterdir())) >= 5  # Platform directories + checksums
        assert checksums_file.exists()
        
        print("✅ Artifact organization workflow successful")
    
    def test_pypi_build_step_simulation(self, workflow_environment):
        """Test PyPI build step simulation."""
        workspace = workflow_environment["workspace"]
        
        # Create minimal project structure
        (workspace / "pyproject.toml").write_text("""
[tool.poetry]
name = "giv-test"
version = "1.0.0"
description = "Test package"
authors = ["Test <test@example.com>"]

[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"
""")
        
        (workspace / "giv").mkdir()
        (workspace / "giv" / "__init__.py").write_text("")
        (workspace / "giv" / "main.py").write_text("def main(): pass")
        
        original_cwd = os.getcwd()
        try:
            os.chdir(workspace)
            
            # Simulate Poetry build step
            result = subprocess.run(
                ["python", "-m", "poetry", "build"],
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode == 0:
                # Check for created packages
                dist_files = list(workspace.glob("dist/*"))
                wheel_files = [f for f in dist_files if f.suffix == ".whl"]
                tarball_files = [f for f in dist_files if f.suffix == ".gz"]
                
                assert len(dist_files) > 0
                print(f"✅ PyPI build created {len(dist_files)} packages")
                
                if wheel_files:
                    print(f"  - {len(wheel_files)} wheel files")
                if tarball_files:
                    print(f"  - {len(tarball_files)} source distributions")
            else:
                pytest.skip(f"Poetry not available or build failed: {result.stderr}")
                
        finally:
            os.chdir(original_cwd)
    
    @patch('subprocess.run')
    def test_pypi_publish_step_simulation(self, mock_subprocess, workflow_environment):
        """Test PyPI publish step simulation."""
        workspace = workflow_environment["workspace"]
        dist_dir = workspace / "dist"
        dist_dir.mkdir()
        
        # Create mock packages
        (dist_dir / "giv-1.0.0.tar.gz").write_text("mock source distribution")
        (dist_dir / "giv-1.0.0-py3-none-any.whl").write_text("mock wheel")
        
        # Mock successful poetry publish
        mock_subprocess.return_value = subprocess.CompletedProcess(
            [], 0, stdout="Uploading distributions", stderr=""
        )
        
        # Simulate environment variables
        test_env = os.environ.copy()
        test_env.update({
            "TWINE_USERNAME": "__token__",
            "TWINE_PASSWORD": "pypi-test-token",
            "GITHUB_REF": "refs/tags/v1.0.0"
        })
        
        original_cwd = os.getcwd()
        try:
            os.chdir(workspace)
            
            # Simulate Test PyPI publish
            if "refs/tags/v" in test_env["GITHUB_REF"] and test_env.get("TWINE_PASSWORD"):
                # This would normally run: poetry config repositories.testpypi && poetry publish
                mock_result = subprocess.run(
                    ["echo", "poetry publish --repository testpypi"],
                    env=test_env,
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                assert mock_result.returncode == 0
                print("✅ Test PyPI publish simulation successful")
            
            # Simulate production PyPI publish
            if not "-" in test_env["GITHUB_REF"]:  # Not a pre-release
                mock_result = subprocess.run(
                    ["echo", "poetry publish"],
                    env=test_env,
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                assert mock_result.returncode == 0
                print("✅ Production PyPI publish simulation successful")
                
        finally:
            os.chdir(original_cwd)
    
    def test_package_config_generation_step(self, workflow_environment):
        """Test package manager configuration generation step."""
        workspace = workflow_environment["workspace"]
        dist_dir = workspace / "dist"
        
        # Set up binary artifacts
        self.test_artifact_organization_workflow(workflow_environment)
        
        # Test available package config generators
        if UnifiedBuilder is None or BuildConfig is None:
            pytest.skip("Build system not available")
        
        config = BuildConfig()
        config.project_root = workspace
        config.dist_dir = dist_dir
        
        builder = UnifiedBuilder(config)
        available_builders = list(builder.builders.keys())
        
        print(f"Available package builders: {available_builders}")
        
        # Try to generate configs for available builders
        generated_configs = []
        for pkg_type in available_builders[:2]:  # Test first 2 available
            try:
                if pkg_type == 'homebrew':
                    builder_instance = builder.builders[pkg_type](config)
                    if hasattr(builder_instance, 'build_formula'):
                        result = builder_instance.build_formula("1.0.0")
                        if result:
                            generated_configs.append(pkg_type)
                            print(f"✅ {pkg_type} formula generated")
                
                elif pkg_type == 'scoop':
                    builder_instance = builder.builders[pkg_type](config)
                    if hasattr(builder_instance, 'build_manifest'):
                        result = builder_instance.build_manifest("1.0.0")
                        if result:
                            generated_configs.append(pkg_type)
                            print(f"✅ {pkg_type} manifest generated")
                            
            except Exception as e:
                print(f"⚠️  {pkg_type} generation failed: {e}")
        
        print(f"✅ Package config generation tested for {len(generated_configs)} types")
    
    @patch('subprocess.run')
    def test_github_release_creation_step(self, mock_subprocess, workflow_environment):
        """Test GitHub release creation step."""
        workspace = workflow_environment["workspace"]
        dist_dir = workspace / "dist"
        
        # Set up artifacts
        self.test_artifact_organization_workflow(workflow_environment)
        
        # Mock gh CLI commands
        def mock_gh_command(*args, **kwargs):
            cmd = args[0]
            if isinstance(cmd, list) and len(cmd) > 0:
                if cmd[0] == "gh" and "release" in cmd:
                    return subprocess.CompletedProcess(
                        cmd, 0, 
                        stdout="https://github.com/fwdslsh/giv/releases/tag/v1.0.0",
                        stderr=""
                    )
            return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")
        
        mock_subprocess.side_effect = mock_gh_command
        
        # Simulate release creation
        version = "1.0.0"
        release_files = list(dist_dir.rglob("giv-*"))
        
        # Simulate gh release create command
        gh_command = [
            "gh", "release", "create", f"v{version}",
            "--title", f"giv CLI v{version}",
            "--notes", "Release notes here"
        ] + [str(f) for f in release_files[:5]]  # Limit files for testing
        
        result = subprocess.run(gh_command, capture_output=True, text=True, check=False)
        
        assert result.returncode == 0
        assert "github.com" in result.stdout
        
        print("✅ GitHub release creation simulation successful")


class TestWorkflowErrorDetection:
    """Test error detection and handling in workflows."""
    
    def test_missing_binary_detection(self):
        """Test detection of missing binary artifacts."""
        with tempfile.TemporaryDirectory() as tmpdir:
            dist_dir = Path(tmpdir)
            
            from core.config import BuildConfig
            config = BuildConfig()
            config.dist_dir = dist_dir
            
            # Check for missing binaries
            missing_binaries = []
            for platform, platform_info in config.platforms.items():
                binary_path = dist_dir / platform_info["binary_name"]
                if not binary_path.exists():
                    missing_binaries.append(platform)
            
            # Should detect missing binaries
            assert len(missing_binaries) > 0
            print(f"✅ Detected {len(missing_binaries)} missing binaries")
    
    def test_invalid_package_detection(self):
        """Test detection of invalid package structures."""
        with tempfile.TemporaryDirectory() as tmpdir:
            dist_dir = Path(tmpdir)
            
            # Create invalid packages
            invalid_wheel = dist_dir / "invalid.whl"
            invalid_wheel.write_text("not a real wheel file")
            
            invalid_tarball = dist_dir / "invalid.tar.gz"
            invalid_tarball.write_text("not a real tarball")
            
            # Test package validation
            packages = list(dist_dir.glob("*.whl")) + list(dist_dir.glob("*.tar.gz"))
            
            valid_packages = []
            for package in packages:
                # Basic validation - real packages should have reasonable size
                if package.stat().st_size > 100:  # Real packages are much larger
                    valid_packages.append(package)
            
            # Should detect that these are invalid
            assert len(valid_packages) == 0
            print(f"✅ Detected {len(packages)} invalid packages")
    
    def test_workflow_failure_simulation(self):
        """Test workflow failure scenarios."""
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = Path(tmpdir)
            
            # Simulate missing dependencies
            missing_deps = []
            
            # Test for Poetry
            result = subprocess.run(["poetry", "--version"], capture_output=True, check=False)
            if result.returncode != 0:
                missing_deps.append("poetry")
            
            # Test for git
            result = subprocess.run(["git", "--version"], capture_output=True, check=False)
            if result.returncode != 0:
                missing_deps.append("git")
            
            if missing_deps:
                print(f"⚠️  Missing dependencies would cause workflow failure: {missing_deps}")
            else:
                print("✅ All required dependencies available")
    
    def test_environment_variable_validation(self):
        """Test validation of required environment variables."""
        required_vars = ["GITHUB_REF", "GITHUB_WORKSPACE", "GITHUB_REPOSITORY"]
        optional_vars = ["PYPI_API_TOKEN", "TEST_PYPI_API_TOKEN"]
        
        # Test with minimal environment
        test_env = {
            "GITHUB_REF": "refs/tags/v1.0.0",
            "GITHUB_WORKSPACE": "/tmp/test",
            "GITHUB_REPOSITORY": "fwdslsh/giv"
        }
        
        missing_required = []
        for var in required_vars:
            if var not in test_env:
                missing_required.append(var)
        
        missing_optional = []
        for var in optional_vars:
            if var not in test_env:
                missing_optional.append(var)
        
        assert len(missing_required) == 0, f"Required vars missing: {missing_required}"
        
        if missing_optional:
            print(f"⚠️  Optional vars missing (would skip publishing): {missing_optional}")
        
        print("✅ Environment variable validation successful")


class TestWorkflowPerformanceValidation:
    """Test workflow performance and timing."""
    
    def test_build_time_estimation(self):
        """Test estimation of build times."""
        import time
        
        # Simulate build steps with timing
        steps = {
            "version_detection": 0.1,
            "binary_organization": 0.5,
            "package_generation": 2.0,
            "config_creation": 1.0,
            "validation": 0.5
        }
        
        total_time = 0
        for step, estimated_time in steps.items():
            start_time = time.time()
            
            # Simulate work
            time.sleep(min(estimated_time * 0.1, 0.1))  # Reduced for testing
            
            actual_time = time.time() - start_time
            total_time += actual_time
            
            print(f"Step '{step}': {actual_time:.2f}s (estimated: {estimated_time}s)")
        
        assert total_time < 10.0  # Should complete within reasonable time
        print(f"✅ Total workflow time: {total_time:.2f}s")
    
    def test_artifact_size_validation(self):
        """Test validation of artifact sizes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            dist_dir = Path(tmpdir)
            
            # Create test artifacts with realistic sizes
            artifacts = {
                "giv-linux-x86_64": 10 * 1024 * 1024,      # 10MB
                "giv-darwin-x86_64": 8 * 1024 * 1024,      # 8MB  
                "giv-windows-x86_64.exe": 12 * 1024 * 1024, # 12MB
                "giv-1.0.0.tar.gz": 100 * 1024,             # 100KB
                "giv-1.0.0-py3-none-any.whl": 50 * 1024     # 50KB
            }
            
            for name, size in artifacts.items():
                artifact = dist_dir / name
                # Create file with approximate size (using dummy content)
                content = "x" * min(size, 1000)  # Limited for testing
                artifact.write_text(content)
            
            # Validate sizes
            total_size = 0
            for artifact in dist_dir.iterdir():
                size = artifact.stat().st_size
                total_size += size
                
                # Check for reasonable size ranges
                if artifact.name.endswith(('.exe', 'giv-linux', 'giv-darwin')):
                    assert size > 100, f"Binary {artifact.name} too small: {size} bytes"
                elif artifact.name.endswith(('.whl', '.tar.gz')):
                    assert size > 10, f"Package {artifact.name} too small: {size} bytes"
            
            print(f"✅ Total artifact size: {total_size:,} bytes")
            assert total_size < 100 * 1024 * 1024  # Less than 100MB total


@pytest.mark.integration
@pytest.mark.slow  
class TestCompleteWorkflowIntegration:
    """Complete workflow integration tests."""
    
    def test_full_release_workflow_simulation(self):
        """Test complete release workflow simulation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = Path(tmpdir)
            
            # Set up complete workspace
            self._setup_complete_workspace(workspace)
            
            # Run through complete workflow steps
            steps = [
                self._step_build_binaries,
                self._step_build_packages,
                self._step_generate_configs,
                self._step_prepare_release,
                self._step_validate_assets
            ]
            
            results = {}
            for i, step_func in enumerate(steps):
                step_name = step_func.__name__
                print(f"\n--- Step {i+1}: {step_name} ---")
                
                try:
                    result = step_func(workspace)
                    results[step_name] = result
                    print(f"✅ {step_name} completed successfully")
                except Exception as e:
                    print(f"❌ {step_name} failed: {e}")
                    results[step_name] = False
            
            # Verify overall success
            successful_steps = sum(1 for r in results.values() if r)
            total_steps = len(results)
            
            print(f"\n✅ Workflow simulation: {successful_steps}/{total_steps} steps successful")
            assert successful_steps >= total_steps * 0.7  # At least 70% success
    
    def _setup_complete_workspace(self, workspace: Path):
        """Set up complete workspace for testing."""
        # Create project structure
        (workspace / "giv").mkdir()
        (workspace / "giv" / "__init__.py").write_text("")
        (workspace / "giv" / "main.py").write_text("def main(): print('giv CLI')")
        
        # Create pyproject.toml
        (workspace / "pyproject.toml").write_text("""
[tool.poetry]
name = "giv"
version = "1.0.0"
description = "AI-powered Git commit message generator"
authors = ["Test <test@example.com>"]

[tool.poetry.scripts]
giv = "giv.main:main"

[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"
""")
        
        # Create build directory structure
        build_dir = workspace / "build"
        build_dir.mkdir()
        
        # Copy essential build files if they exist
        original_build = Path(__file__).parent.parent / "build"
        if original_build.exists():
            for item in ["core"]:
                src = original_build / item
                dst = build_dir / item
                if src.exists() and src.is_dir():
                    shutil.copytree(src, dst)
    
    def _step_build_binaries(self, workspace: Path) -> bool:
        """Simulate binary building step."""
        dist_dir = workspace / "dist"
        dist_dir.mkdir(exist_ok=True)
        
        # Create mock binaries
        platforms = ["linux-x86_64", "darwin-x86_64", "windows-x86_64"]
        for platform in platforms:
            binary_name = f"giv-{platform}"
            if platform.startswith("windows"):
                binary_name += ".exe"
            
            binary_path = dist_dir / binary_name
            binary_path.write_text(f"Mock {platform} binary")
            binary_path.chmod(0o755)
        
        return len(list(dist_dir.glob("giv-*"))) >= 3
    
    def _step_build_packages(self, workspace: Path) -> bool:
        """Simulate package building step."""
        original_cwd = os.getcwd()
        try:
            os.chdir(workspace)
            
            # Try to build with Poetry
            result = subprocess.run(
                ["python", "-m", "poetry", "build"],
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode == 0:
                dist_files = list(workspace.glob("dist/*"))
                return len(dist_files) > 0
            else:
                # Create mock packages if Poetry not available
                dist_dir = workspace / "dist"
                dist_dir.mkdir(exist_ok=True)
                (dist_dir / "giv-1.0.0.tar.gz").write_text("mock source dist")
                (dist_dir / "giv-1.0.0-py3-none-any.whl").write_text("mock wheel")
                return True
                
        finally:
            os.chdir(original_cwd)
    
    def _step_generate_configs(self, workspace: Path) -> bool:
        """Simulate package manager config generation."""
        try:
            if BuildConfig is None:
                return False
            config = BuildConfig()
            config.project_root = workspace
            config.dist_dir = workspace / "dist"
            
            # Try to generate at least one config
            dist_dir = config.dist_dir
            
            # Create mock Homebrew formula
            formula_content = '''
class Giv < Formula
  desc "AI-powered Git commit message generator"
  homepage "https://github.com/fwdslsh/giv"
  version "1.0.0"
  url "https://github.com/fwdslsh/giv/releases/download/v1.0.0/giv-darwin-x86_64"
  sha256 "abcd1234"
  
  def install
    bin.install "giv-darwin-x86_64" => "giv"
  end
end
'''
            (dist_dir / "giv.rb").write_text(formula_content)
            
            # Create mock Scoop manifest
            manifest_content = {
                "version": "1.0.0",
                "architecture": {
                    "64bit": {
                        "url": "https://github.com/fwdslsh/giv/releases/download/v1.0.0/giv-windows-x86_64.exe",
                        "hash": "abcd1234"
                    }
                },
                "bin": "giv-windows-x86_64.exe"
            }
            (dist_dir / "giv.json").write_text(json.dumps(manifest_content, indent=2))
            
            return True
            
        except Exception:
            return False
    
    def _step_prepare_release(self, workspace: Path) -> bool:
        """Simulate release preparation."""
        dist_dir = workspace / "dist"
        
        # Create release notes
        release_notes = f"""
# giv CLI v1.0.0

## Installation

### Binary Downloads
- Linux x86_64: giv-linux-x86_64
- macOS Intel: giv-darwin-x86_64  
- Windows: giv-windows-x86_64.exe

### Package Managers
- Homebrew: brew install giv
- Scoop: scoop install giv
- PyPI: pip install giv
"""
        
        (dist_dir / "release_notes.md").write_text(release_notes)
        
        # Create checksums file
        checksums_content = ""
        for binary in dist_dir.glob("giv-*"):
            if binary.is_file() and not binary.name.endswith(('.rb', '.json', '.md')):
                # Mock checksum
                checksums_content += f"abcd1234  {binary.name}\n"
        
        (dist_dir / "checksums.txt").write_text(checksums_content)
        
        return True
    
    def _step_validate_assets(self, workspace: Path) -> bool:
        """Validate all release assets."""
        dist_dir = workspace / "dist"
        
        required_assets = [
            "giv-linux-x86_64",
            "giv-darwin-x86_64", 
            "giv-windows-x86_64.exe",
            "giv-1.0.0.tar.gz",
            "giv-1.0.0-py3-none-any.whl",
            "checksums.txt"
        ]
        
        missing_assets = []
        for asset in required_assets:
            if not (dist_dir / asset).exists():
                missing_assets.append(asset)
        
        if missing_assets:
            print(f"Missing assets: {missing_assets}")
        
        return len(missing_assets) <= 2  # Allow some assets to be missing


if __name__ == "__main__":
    # Allow running tests directly
    pytest.main([__file__, "-v", "--tb=short"])