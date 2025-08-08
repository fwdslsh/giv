#!/usr/bin/env python3
"""
Integration test runner for giv CLI build and publish workflow.

This script runs comprehensive integration tests to validate the build,
package, and publish workflow without actually publishing to external services.
"""
import argparse
import subprocess
import sys
from pathlib import Path


def run_command(cmd, description, check=True):
    """Run a command and display results."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print('='*60)
    
    try:
        result = subprocess.run(cmd, check=check, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - SUCCESS")
        else:
            print(f"❌ {description} - FAILED (exit code: {result.returncode})")
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - FAILED (exit code: {e.returncode})")
        return False
    except FileNotFoundError:
        print(f"❌ {description} - COMMAND NOT FOUND")
        return False


def main():
    """Main test runner."""
    parser = argparse.ArgumentParser(description="Run giv CLI integration tests")
    parser.add_argument("--quick", action="store_true", help="Run only quick tests")
    parser.add_argument("--full", action="store_true", help="Run all integration tests")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    project_root = Path(__file__).parent.parent
    print(f"Running integration tests from: {project_root}")
    print(f"Python: {sys.version}")
    
    # Change to project directory
    import os
    original_cwd = os.getcwd()
    os.chdir(project_root)
    
    try:
        success_count = 0
        total_tests = 0
        
        # Test categories
        test_categories = [
            {
                "name": "System Requirements",
                "command": ["poetry", "run", "pytest", "tests/test_integration_simple_build.py::TestBasicBuildWorkflow::test_system_requirements", "-v"],
                "quick": True
            },
            {
                "name": "Project Structure Validation", 
                "command": ["poetry", "run", "pytest", "tests/test_integration_simple_build.py::TestBasicBuildWorkflow::test_project_structure_validation", "-v"],
                "quick": True
            },
            {
                "name": "Poetry Functionality",
                "command": ["poetry", "run", "pytest", "tests/test_integration_simple_build.py::TestBasicBuildWorkflow::test_poetry_functionality", "-v"],
                "quick": True
            },
            {
                "name": "Build Directory Structure",
                "command": ["poetry", "run", "pytest", "tests/test_integration_simple_build.py::TestBasicBuildWorkflow::test_build_directory_structure", "-v"],
                "quick": True
            },
            {
                "name": "Mock Binary Creation",
                "command": ["poetry", "run", "pytest", "tests/test_integration_simple_build.py::TestBasicBuildWorkflow::test_mock_binary_creation", "-v"],
                "quick": True
            },
            {
                "name": "Checksum Generation",
                "command": ["poetry", "run", "pytest", "tests/test_integration_simple_build.py::TestBasicBuildWorkflow::test_checksum_generation", "-v"],
                "quick": True
            },
            {
                "name": "Version Detection",
                "command": ["poetry", "run", "pytest", "tests/test_integration_simple_build.py::TestBasicBuildWorkflow::test_version_detection_simulation", "-v"],
                "quick": True
            },
            {
                "name": "Error Scenarios",
                "command": ["poetry", "run", "pytest", "tests/test_integration_simple_build.py::TestWorkflowErrorScenarios", "-v"],
                "quick": False
            },
            {
                "name": "Complete Workflow Simulation",
                "command": ["poetry", "run", "pytest", "tests/test_integration_simple_build.py::TestEndToEndWorkflowSimulation::test_complete_workflow_simulation", "-v", "-s"],
                "quick": False
            },
            {
                "name": "All Integration Tests (Simple)",
                "command": ["poetry", "run", "pytest", "tests/test_integration_simple_build.py", "-v", "--tb=short"],
                "quick": False
            }
        ]
        
        # Add full integration tests if requested
        if args.full:
            test_categories.extend([
                {
                    "name": "Build Workflow Integration",
                    "command": ["poetry", "run", "pytest", "tests/test_integration_build_workflow.py", "-v", "--tb=short"],
                    "quick": False
                },
                {
                    "name": "Package Manager Integration", 
                    "command": ["poetry", "run", "pytest", "tests/test_integration_package_managers.py", "-v", "--tb=short"],
                    "quick": False
                },
                {
                    "name": "Publish Workflow Integration",
                    "command": ["poetry", "run", "pytest", "tests/test_integration_publish_workflow.py", "-v", "--tb=short"],
                    "quick": False
                }
            ])
        
        # Filter tests based on mode
        if args.quick:
            tests_to_run = [t for t in test_categories if t.get("quick", True)]
        else:
            tests_to_run = test_categories
        
        print(f"\nRunning {len(tests_to_run)} test categories...")
        
        # Run tests
        for test_info in tests_to_run:
            total_tests += 1
            
            if run_command(test_info["command"], test_info["name"]):
                success_count += 1
        
        # Summary
        print(f"\n{'='*60}")
        print("INTEGRATION TEST SUMMARY")
        print('='*60)
        print(f"Total test categories: {total_tests}")
        print(f"Successful: {success_count}")
        print(f"Failed: {total_tests - success_count}")
        print(f"Success rate: {success_count/total_tests*100:.1f}%")
        
        if success_count == total_tests:
            print("\n🎉 All integration tests passed!")
            print("\nThe build, package, and publish workflow is ready for use.")
            print("\nNext steps:")
            print("1. The integration tests validate the workflow structure")
            print("2. Manual testing with actual builds is recommended")
            print("3. GitHub Actions workflow should work with these components")
            return 0
        else:
            print(f"\n⚠️  {total_tests - success_count} test categories failed")
            print("Review the failed tests above for issues in the build workflow.")
            return 1
            
    finally:
        os.chdir(original_cwd)


if __name__ == "__main__":
    sys.exit(main())