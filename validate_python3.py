#!/usr/bin/env python3
"""
B3 Python 3 Migration Validation Script
This script tests the basic functionality of B3 after Python 3 conversion.
"""

import sys
import os
import importlib.util

def test_python_version():
    """Test that we're running on Python 3.8+"""
    print("Testing Python version...")
    if sys.version_info < (3, 8):
        print(f"ERROR: Python {sys.version_info.major}.{sys.version_info.minor} detected. B3 requires Python 3.8+")
        return False
    print(f"OK: Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    return True

def test_imports():
    """Test importing key B3 modules"""
    print("\nTesting core imports...")
    
    try:
        import b3_run
        print("OK: b3_run imported successfully")
    except Exception as e:
        print(f"ERROR: Failed to import b3_run: {e}")
        return False
    
    try:
        import b3
        print("OK: b3 core module imported successfully")
    except Exception as e:
        print(f"ERROR: Failed to import b3: {e}")
        return False
    
    try:
        import b3.update
        print("OK: b3.update imported successfully")
    except Exception as e:
        print(f"ERROR: Failed to import b3.update: {e}")
        return False
    
    return True

def test_dependencies():
    """Test that required dependencies are available"""
    print("\nTesting dependencies...")
    
    dependencies = [
        'pymysql',
        'dateutil',
        'feedparser',
        'requests'
    ]
    
    for dep in dependencies:
        try:
            if dep == 'dateutil':
                import dateutil
            else:
                __import__(dep)
            print(f"OK: {dep} is available")
        except ImportError as e:
            print(f"ERROR: {dep} is not available: {e}")
            return False
    
    return True

def test_b3_version():
    """Test B3 version detection"""
    print("\nTesting B3 version detection...")
    
    try:
        import b3
        version = b3.getB3versionString()
        print(f"OK: B3 version {version}")
        return True
    except Exception as e:
        print(f"ERROR: Failed to get B3 version: {e}")
        return False

def test_basic_functionality():
    """Test basic B3 functionality without starting the server"""
    print("\nTesting basic functionality...")
    
    try:
        # Test configuration parsing
        from b3.config import XmlConfigParser
        print("OK: XmlConfigParser can be imported")
        
        # Test event system
        from b3.events import Event
        print("OK: Event system can be imported")
        
        # Test plugin system
        from b3.plugin import Plugin
        print("OK: Plugin system can be imported")
        
        return True
    except Exception as e:
        print(f"ERROR: Basic functionality test failed: {e}")
        return False

def main():
    print("B3 Python 3 Migration Validation")
    print("=" * 40)
    
    tests = [
        test_python_version,
        test_imports,
        test_dependencies,
        test_b3_version,
        test_basic_functionality
    ]
    
    all_passed = True
    for test in tests:
        if not test():
            all_passed = False
    
    print("\n" + "=" * 40)
    if all_passed:
        print("SUCCESS: All tests passed! B3 appears to be successfully converted to Python 3.")
    else:
        print("FAILURE: Some tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
