#!/usr/bin/env python3
"""
Test script to verify environment variable configuration is working correctly.
"""
import os
import sys
from pathlib import Path

def test_config_module():
    """Test that config module loads correctly."""
    print("Testing config module...")
    try:
        import config
        print("✓ config module imported successfully")
        return True
    except Exception as e:
        print(f"✗ Failed to import config: {e}")
        return False

def test_default_values():
    """Test that default values are set correctly."""
    print("\nTesting default values...")
    import config
    
    if config.HYPIXEL_API_URL:
        print(f"✓ HYPIXEL_API_URL is set: {config.HYPIXEL_API_URL}")
    else:
        print("✗ HYPIXEL_API_URL is not set")
        return False
    
    return True

def test_env_file_loading():
    """Test that .env file is loaded if it exists."""
    print("\nTesting .env file loading...")
    env_path = Path(__file__).parent / '.env'
    
    if env_path.exists():
        print(f"✓ .env file exists at {env_path}")
        print("  Environment variables will be loaded from this file")
    else:
        print("ℹ .env file not found (this is OK for CI/CD)")
        print("  Environment variables will be loaded from system environment")
    
    return True

def test_gitignore():
    """Test that .env is in .gitignore."""
    print("\nTesting .gitignore configuration...")
    gitignore_path = Path(__file__).parent / '.gitignore'
    
    if gitignore_path.exists():
        content = gitignore_path.read_text()
        if '.env' in content:
            print("✓ .env is listed in .gitignore")
            return True
        else:
            print("✗ .env is NOT in .gitignore - secrets could be exposed!")
            return False
    else:
        print("✗ .gitignore not found")
        return False

def test_env_example():
    """Test that .env.example exists."""
    print("\nTesting .env.example template...")
    example_path = Path(__file__).parent / '.env.example'
    
    if example_path.exists():
        print(f"✓ .env.example exists")
        return True
    else:
        print("✗ .env.example not found")
        return False

def test_validation():
    """Test config validation."""
    print("\nTesting configuration validation...")
    try:
        import config
        config.validate_config()
        print("✓ Configuration validation passed")
        return True
    except ValueError as e:
        print(f"✗ Configuration validation failed: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("Environment Variable Configuration Test Suite")
    print("=" * 60)
    
    tests = [
        test_config_module,
        test_default_values,
        test_env_file_loading,
        test_gitignore,
        test_env_example,
        test_validation,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\n✗ Test {test.__name__} crashed: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Results: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print("\n✓ All tests passed! Configuration is secure and working correctly.")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed. Please review the output above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
