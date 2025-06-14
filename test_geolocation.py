#!/usr/bin/env python3
"""
Test script to validate geolocation plugin compatibility with Python 3.
"""

import sys
import os

# Add the B3 directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_geolocation_imports():
    """Test importing geolocation modules."""
    print("Testing geolocation module imports...")
    
    try:
        # Test main geolocation plugin import
        from b3.plugins.geolocation import GeolocationPlugin
        print("✓ GeolocationPlugin imported successfully")
        
        # Test geolocators import
        from b3.plugins.geolocation.geolocators import MaxMindGeolocator
        print("✓ MaxMindGeolocator imported successfully")
        
        # Test GeoIP library import
        from b3.plugins.geolocation.lib.geoip import GeoIP
        print("✓ GeoIP library imported successfully")
        
        # Test exceptions import
        from b3.plugins.geolocation.exceptions import GeolocalizationError
        print("✓ GeolocalizationError imported successfully")
        
        # Test location import
        from b3.plugins.geolocation.location import Location
        print("✓ Location imported successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_geoip_basic_functionality():
    """Test basic GeoIP functionality."""
    print("\nTesting GeoIP basic functionality...")
    
    try:
        from b3.plugins.geolocation.lib.geoip import GeoIP
        
        # Test IP address conversion
        test_ip = "8.8.8.8"
        ip_num = GeoIP.addr_to_num(test_ip)
        print(f"✓ IP {test_ip} converted to number: {ip_num}")
        
        # Test country codes (static methods)
        country_code = GeoIP.id_to_country_code(1)
        country_name = GeoIP.id_to_country_name(1)
        print(f"✓ Country ID 1 -> Code: {country_code}, Name: {country_name}")
        
        return True
        
    except Exception as e:
        print(f"✗ GeoIP test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_geolocation_plugin_creation():
    """Test creating geolocation plugin instance."""
    print("\nTesting geolocation plugin creation...")
    
    try:
        import b3
        from b3.plugins.geolocation import GeolocationPlugin
        
        # Create a mock console for testing
        class MockConsole:
            def isFrostbiteGame(self):
                return False
        
        console = MockConsole()
        plugin = GeolocationPlugin(console, None)
        print("✓ GeolocationPlugin instance created successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Plugin creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all geolocation tests."""
    print("=" * 60)
    print("B3 Geolocation Plugin Python 3 Compatibility Test")
    print("=" * 60)
    
    tests = [
        test_geolocation_imports,
        test_geoip_basic_functionality,
        test_geolocation_plugin_creation
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "=" * 60)
    print("Test Summary:")
    print(f"✓ Passed: {sum(results)}")
    print(f"✗ Failed: {len(results) - sum(results)}")
    
    if all(results):
        print("\n🎉 All geolocation tests PASSED! The plugin should work with Python 3.")
        return 0
    else:
        print("\n❌ Some tests FAILED. Check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
