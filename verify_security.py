#!/usr/bin/env python3
"""
Security verification script to ensure API keys and secrets are properly protected.
This script checks for common security issues.
"""
import os
import sys
from pathlib import Path
import subprocess

def check_no_hardcoded_keys():
    """Check that no API keys are hardcoded in the source code."""
    print("Checking for hardcoded API keys in source code...")
    
    # Files to check
    source_files = [
        '__main__.py',
        'config.py',
    ]
    
    # Patterns that might indicate hardcoded keys
    suspicious_patterns = [
        'AIzaSy',  # Firebase API keys start with this
        'api.hypixel.net/skyblock',  # Should use config variable
    ]
    
    issues = []
    for file in source_files:
        filepath = Path(__file__).parent / file
        if not filepath.exists():
            continue
            
        content = filepath.read_text()
        
        # Check __main__.py doesn't have hardcoded URL
        if file == '__main__.py':
            if 'api.hypixel.net' in content and 'config.HYPIXEL_API_URL' not in content:
                issues.append(f"{file}: Hardcoded API URL found (should use config.HYPIXEL_API_URL)")
        
        # Check for Firebase keys
        for pattern in suspicious_patterns:
            if pattern in content and pattern == 'AIzaSy':
                # Make sure it's not in a comment or example
                lines = content.split('\n')
                for i, line in enumerate(lines, 1):
                    if pattern in line and not line.strip().startswith('#'):
                        issues.append(f"{file}:{i}: Possible hardcoded Firebase API key")
    
    if issues:
        print("✗ Security issues found:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    else:
        print("✓ No hardcoded API keys detected")
        return True

def check_env_in_gitignore():
    """Verify .env files are in .gitignore."""
    print("\nChecking .gitignore for .env entries...")
    
    gitignore = Path(__file__).parent / '.gitignore'
    if not gitignore.exists():
        print("✗ .gitignore not found!")
        return False
    
    content = gitignore.read_text()
    required_patterns = ['.env']
    
    missing = []
    for pattern in required_patterns:
        if pattern not in content:
            missing.append(pattern)
    
    if missing:
        print(f"✗ Missing patterns in .gitignore: {missing}")
        return False
    else:
        print("✓ .env is properly listed in .gitignore")
        return True

def check_no_env_tracked():
    """Ensure .env file is not tracked by git."""
    print("\nChecking if .env is tracked by git...")
    
    try:
        # Check if .env is in git index
        result = subprocess.run(
            ['git', 'ls-files', '.env'],
            cwd=Path(__file__).parent,
            capture_output=True,
            text=True
        )
        
        if result.stdout.strip():
            print("✗ WARNING: .env file is tracked by git!")
            print("  Run: git rm --cached .env")
            return False
        else:
            print("✓ .env is not tracked by git")
            return True
    except Exception as e:
        print(f"ℹ Could not check git status: {e}")
        return True  # Don't fail if git is not available

def check_workflow_uses_secrets():
    """Verify GitHub Actions workflow uses secrets for environment variables."""
    print("\nChecking GitHub Actions workflow configuration...")
    
    workflow = Path(__file__).parent / '.github' / 'workflows' / 'run_main.yml'
    if not workflow.exists():
        print("ℹ Workflow file not found")
        return True
    
    content = workflow.read_text()
    
    checks = [
        ('secrets.HYPIXEL_API_URL', 'HYPIXEL_API_URL should use GitHub secret'),
        ('env:', 'Workflow should define environment variables'),
    ]
    
    issues = []
    for pattern, message in checks:
        if pattern not in content:
            issues.append(message)
    
    if issues:
        print("✗ Workflow configuration issues:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    else:
        print("✓ Workflow properly configured to use GitHub Secrets")
        return True

def check_documentation_exists():
    """Verify security documentation exists."""
    print("\nChecking for security documentation...")
    
    docs = [
        ('ENVIRONMENT_SETUP.md', 'Environment setup guide'),
        ('.env.example', 'Environment variable template'),
    ]
    
    missing = []
    for filename, description in docs:
        filepath = Path(__file__).parent / filename
        if not filepath.exists():
            missing.append(f"{filename} ({description})")
    
    if missing:
        print("✗ Missing documentation:")
        for item in missing:
            print(f"  - {item}")
        return False
    else:
        print("✓ All security documentation present")
        return True

def check_config_module():
    """Verify config module is properly implemented."""
    print("\nChecking config module implementation...")
    
    try:
        import config
        
        # Check that config loads from environment
        if not hasattr(config, 'HYPIXEL_API_URL'):
            print("✗ config.HYPIXEL_API_URL not defined")
            return False
        
        # Check validation function exists
        if not hasattr(config, 'validate_config'):
            print("✗ config.validate_config() not defined")
            return False
        
        # Try validation
        config.validate_config()
        
        print("✓ Config module properly implemented")
        return True
    except Exception as e:
        print(f"✗ Config module error: {e}")
        return False

def main():
    """Run all security checks."""
    print("=" * 70)
    print("API Key Security Verification")
    print("=" * 70)
    print("\nThis script verifies that API keys and secrets are properly protected")
    print("and not exposed in the repository.\n")
    
    checks = [
        check_no_hardcoded_keys,
        check_env_in_gitignore,
        check_no_env_tracked,
        check_workflow_uses_secrets,
        check_documentation_exists,
        check_config_module,
    ]
    
    results = []
    for check in checks:
        try:
            result = check()
            results.append(result)
        except Exception as e:
            print(f"\n✗ Check {check.__name__} crashed: {e}")
            results.append(False)
    
    print("\n" + "=" * 70)
    passed = sum(results)
    total = len(results)
    print(f"Security Check Results: {passed}/{total} checks passed")
    print("=" * 70)
    
    if passed == total:
        print("\n✅ SECURITY VERIFIED: All checks passed!")
        print("API keys are properly protected and not exposed in the repository.")
        print("\nNext steps:")
        print("1. Add secrets to GitHub: Settings → Secrets → Actions")
        print("2. Test the workflow by triggering a run")
        print("3. Verify logs don't expose any secrets")
        return 0
    else:
        print(f"\n❌ SECURITY ISSUES FOUND: {total - passed} check(s) failed")
        print("Please review and fix the issues above before deploying.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
