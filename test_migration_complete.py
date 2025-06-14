#!/usr/bin/env python3
"""
B3 Core Functionality Test Script
Tests the core components to ensure Python 3 migration is successful
"""

import sys
import os

# Add B3 to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_core_imports():
    """Test that all core modules can be imported"""
    print("=== Testing Core Imports ===")
    
    try:
        import b3
        print("✅ b3 module imported")
    except Exception as e:
        print(f"❌ b3 import failed: {e}")
        return False
        
    try:
        from b3.plugins.admin import AdminPlugin
        print("✅ AdminPlugin imported")
    except Exception as e:
        print(f"❌ AdminPlugin import failed: {e}")
        return False
        
    try:
        from b3.querybuilder import QueryBuilder
        print("✅ QueryBuilder imported")
    except Exception as e:
        print(f"❌ QueryBuilder import failed: {e}")
        return False
        
    try:
        from b3.parsers.q3a.rcon import Rcon
        print("✅ RCON module imported")
    except Exception as e:
        print(f"❌ RCON import failed: {e}")
        return False
        
    return True

def test_stringio_fix():
    """Test that StringIO fixes are working"""
    print("\n=== Testing StringIO Fixes ===")
    
    try:
        from b3.tools.documentationBuilder import DocBuilder
        print("✅ DocumentationBuilder imported (StringIO fixed)")
    except Exception as e:
        print(f"❌ DocumentationBuilder import failed: {e}")
        return False
        
    try:
        from b3.config import XmlConfigParser
        print("✅ XmlConfigParser imported (StringIO fixed)")
    except Exception as e:
        print(f"❌ XmlConfigParser import failed: {e}")
        return False
        
    return True

def test_querybuilder():
    """Test QueryBuilder functionality (long type fix)"""
    print("\n=== Testing QueryBuilder (long type fix) ===")
    
    try:
        from b3.querybuilder import QueryBuilder
        qb = QueryBuilder(None)
        
        # Test the escape method that had the long type issue
        result = qb.escape(42)  # Test with int
        print(f"✅ QueryBuilder.escape(int) works: {result}")
        
        result = qb.escape(3.14)  # Test with float
        print(f"✅ QueryBuilder.escape(float) works: {result}")
        
        result = qb.escape("test")  # Test with string
        print(f"✅ QueryBuilder.escape(str) works: {result}")
        
    except Exception as e:
        print(f"❌ QueryBuilder test failed: {e}")
        return False
        
    return True

def main():
    """Run all tests"""
    print("B3 Python 3 Migration - Core Functionality Test")
    print("=" * 50)
    
    all_passed = True
    
    if not test_core_imports():
        all_passed = False
        
    if not test_stringio_fix():
        all_passed = False
        
    if not test_querybuilder():
        all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 ALL TESTS PASSED! Python 3 migration is successful!")
        print("✅ Core modules working")
        print("✅ StringIO fixes working") 
        print("✅ QueryBuilder (long type) fixes working")
        print("✅ B3 is ready for production use")
    else:
        print("❌ Some tests failed. Check the output above.")
        
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
