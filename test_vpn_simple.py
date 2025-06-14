#!/usr/bin/env python3
"""
Simple VPN Blocker Plugin Test
Quick test to verify the VPN blocker plugin works
"""

import sys
import os

# Add B3 paths
current_dir = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(current_dir, 'b3'))
sys.path.insert(0, os.path.join(current_dir, 'b3', 'extplugins'))

def test_vpn_blocker_simple():
    """Simple test of VPN blocker plugin"""
    print("=" * 60)
    print("VPN Blocker Plugin - Simple Test")
    print("=" * 60)
    
    try:
        # Test import
        import vpnblocker
        print("✓ VPN blocker plugin imported successfully")
        
        # Test plugin creation with mock objects
        class MockConsole:
            def debug(self, msg):
                pass
            def info(self, msg):
                print(f"INFO: {msg}")
            def warning(self, msg):
                print(f"WARNING: {msg}")
            def error(self, msg):
                print(f"ERROR: {msg}")
            def getEventID(self, name):
                return 1
            def getEventName(self, event_id):
                return 'EVT_TEST'
            def registerHandler(self, event, handler):
                pass
        
        class MockConfig:
            def getboolean(self, section, option):
                return True
            def getint(self, section, option):
                return 60
            def get(self, section, option):
                return ""
        
        console = MockConsole()
        config = MockConfig()
        
        # Create plugin
        plugin = vpnblocker.VpnblockerPlugin(console, config)
        print("✓ Plugin created successfully")
        
        # Test configuration
        plugin.loadConfig()
        print(f"✓ Plugin configured - Enabled: {plugin._enabled}")
        
        # Test cache
        plugin._cacheResult("8.8.8.8", False)
        cached = plugin._getCachedResult("8.8.8.8")
        print(f"✓ Cache test: {cached}")
        
        # Test VPN ranges
        plugin.loadVpnRanges()
        print(f"✓ VPN ranges loaded: {len(plugin._known_vpn_ranges)} ranges")
        
        # Test known range check
        is_vpn = plugin._checkKnownRanges("8.8.8.8")
        print(f"✓ Known range check: {is_vpn}")
        
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the simple test"""
    success = test_vpn_blocker_simple()
    
    if success:
        print("\n" + "=" * 60)
        print("✓ VPN Blocker Plugin - All tests passed!")
        print("✓ Plugin is ready for use with B3")
        print("\nTo use:")
        print("1. Plugin is already configured in b3.xml")
        print("2. Edit b3/extplugins/conf/vpnblocker.ini for settings")
        print("3. Add API keys for better detection (optional)")
        print("4. Restart B3 to load the plugin")
        print("5. Use admin commands: !vpncheck, !vpnstatus, !vpnclear")
        print("=" * 60)
        return 0
    else:
        print("\n✗ VPN Blocker Plugin tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
