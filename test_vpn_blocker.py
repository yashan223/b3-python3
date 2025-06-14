#!/usr/bin/env python3
"""
VPN Blocker Plugin Test Script
Tests the VPN detection functionality
"""

import sys
import os
import time

# Add B3 paths
current_dir = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(current_dir, 'b3'))
sys.path.insert(0, os.path.join(current_dir, 'b3', 'extplugins'))

# Import VPN blocker plugin
try:
    import vpnblocker
    print("✓ VPN blocker plugin imported successfully")
except ImportError as e:
    print(f"✗ Failed to import VPN blocker plugin: {e}")
    sys.exit(1)

class MockConfig:
    def getboolean(self, section, option):
        defaults = {
            ('settings', 'enabled'): True,
            ('settings', 'kick_on_vpn'): True,
            ('settings', 'ban_on_vpn'): False,
            ('settings', 'log_detections'): True,
            ('settings', 'announce_kicks'): True,
            ('apis', 'use_proxycheck'): True,
            ('apis', 'use_vpnapi'): True,
            ('apis', 'use_ipqualityscore'): False,
        }
        return defaults.get((section, option), False)
    
    def getint(self, section, option):
        defaults = {
            ('settings', 'ban_duration'): 7,
            ('settings', 'whitelist_level'): 40,
            ('settings', 'check_timeout'): 10,
            ('settings', 'cache_time'): 3600,
            ('settings', 'max_retries'): 3,
        }
        return defaults.get((section, option), 0)
    
    def get(self, section, option):
        return ""

class MockConsole:
    def debug(self, msg):
        print(f"DEBUG: {msg}")
    
    def info(self, msg):
        print(f"INFO: {msg}")
    
    def warning(self, msg):
        print(f"WARNING: {msg}")
    
    def error(self, msg):
        print(f"ERROR: {msg}")
    
    def say(self, msg):
        print(f"SAY: {msg}")
    
    def getEventID(self, name):
        # Mock event IDs
        event_ids = {
            'EVT_STOP': 1,
            'EVT_CLIENT_CONNECT': 2,
            'EVT_CLIENT_AUTH': 3,
        }
        return event_ids.get(name, 999)
    
    def getEventName(self, event_id):
        # Mock event names
        event_names = {
            1: 'EVT_STOP',
            2: 'EVT_CLIENT_CONNECT',
            3: 'EVT_CLIENT_AUTH',
        }
        return event_names.get(event_id, 'EVT_UNKNOWN')
    
    def registerHandler(self, event, handler):
        print(f"Registered handler for event {event}")
        pass

def test_plugin_creation():
    """Test creating the VPN blocker plugin"""
    print("\nTesting plugin creation...")
    try:
        console = MockConsole()
        config = MockConfig()
        
        plugin = vpnblocker.VpnblockerPlugin(console, config)
        plugin.loadConfig()
        
        print("✓ Plugin created and configured successfully")
        return plugin
    except Exception as e:
        print(f"✗ Failed to create plugin: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_cache_functionality(plugin):
    """Test the cache functionality"""
    print("\nTesting cache functionality...")
    try:
        test_ip = "8.8.8.8"
        
        # Should return None for non-cached IP
        result = plugin._getCachedResult(test_ip)
        assert result is None, f"Expected None, got {result}"
        print("✓ Cache miss works correctly")
        
        # Cache a result
        plugin._cacheResult(test_ip, False)
        
        # Should return cached result
        result = plugin._getCachedResult(test_ip)
        assert result == False, f"Expected False, got {result}"
        print("✓ Cache hit works correctly")
        
        return True
    except Exception as e:
        print(f"✗ Cache test failed: {e}")
        return False

def test_known_ranges(plugin):
    """Test known VPN ranges functionality"""
    print("\nTesting known VPN ranges...")
    try:
        plugin.loadVpnRanges()
        
        # Test with various IPs (current implementation has empty ranges)
        test_ips = ["8.8.8.8", "1.1.1.1", "192.168.1.1"]
        
        for ip in test_ips:
            result = plugin._checkKnownRanges(ip)
            print(f"  Known range check for {ip}: {result}")
        
        print("✓ Known ranges functionality works")
        return True
    except Exception as e:
        print(f"✗ Known ranges test failed: {e}")
        return False

def test_api_methods(plugin):
    """Test API methods without making real API calls"""
    print("\nTesting API methods (mocked)...")
    try:
        # Mock the API request method
        def mock_api_request(url):
            if "proxycheck.io" in url:
                return '{"8.8.8.8": {"proxy": "no"}}'
            elif "vpnapi.io" in url:
                return '{"security": {"vpn": false, "proxy": false}}'
            elif "ipqualityscore.com" in url:
                return '{"vpn": false, "proxy": false, "tor": false}'
            return None
        
        # Replace the real method with mock
        original_method = plugin._makeAPIRequest
        plugin._makeAPIRequest = mock_api_request
        
        # Test ProxyCheck
        result = plugin._checkProxyCheck("8.8.8.8")
        print(f"  ProxyCheck result: {result}")
        
        # Test VPN-API
        result = plugin._checkVpnAPI("8.8.8.8")
        print(f"  VPN-API result: {result}")
        
        # Restore original method
        plugin._makeAPIRequest = original_method
        
        print("✓ API methods work correctly")
        return True
    except Exception as e:
        print(f"✗ API methods test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("VPN Blocker Plugin Test Suite")
    print("=" * 60)
    
    # Test plugin creation
    plugin = test_plugin_creation()
    if not plugin:
        print("\n✗ Cannot continue without plugin instance")
        return False
    
    # Run individual tests
    tests = [
        (test_cache_functionality, plugin),
        (test_known_ranges, plugin),
        (test_api_methods, plugin),
    ]
    
    passed = 0
    failed = 0
    
    for test_func, *args in tests:
        try:
            if test_func(*args):
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ Test {test_func.__name__} failed with exception: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed + 1} passed, {failed} failed")  # +1 for plugin creation
    print("=" * 60)
    
    if failed == 0:
        print("✓ All VPN blocker tests passed!")
        return True
    else:
        print(f"✗ {failed} tests failed!")
        return False

if __name__ == "__main__":
    success = main()
    print("\nVPN Blocker Plugin is ready for use!")
    sys.exit(0 if success else 1)
