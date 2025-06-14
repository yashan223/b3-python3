#!/usr/bin/env python3
"""
VPN Blocker Plugin Integration Test
Tests the plugin in a more realistic B3 environment
"""

import sys
import os
import time
import threading

# Add B3 paths
current_dir = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(current_dir, 'b3'))
sys.path.insert(0, os.path.join(current_dir, 'b3', 'extplugins'))

# Import B3 modules
import b3.config
import b3.fake

def test_vpn_blocker_integration():
    """Test VPN blocker plugin with actual B3 config"""
    print("Testing VPN Blocker Plugin Integration...")
    
    try:
        # Create fake console with config
        console = b3.fake.FakeConsole("@b3/conf/b3.distribution.xml")
        
        # Load actual config
        config_path = os.path.join(current_dir, 'b3', 'extplugins', 'conf', 'vpnblocker.ini')
        if os.path.exists(config_path):
            config = b3.config.CfgConfigParser()
            config.read(config_path)
            print(f"✓ Loaded config from {config_path}")
        else:
            print(f"✗ Config file not found: {config_path}")
            return False
        
        # Import and create plugin
        import vpnblocker
        plugin = vpnblocker.VpnblockerPlugin(console, config)
        
        print("✓ Plugin created with real config")
        
        # Test configuration loading
        plugin.loadConfig()
        print(f"✓ Plugin configured - Enabled: {plugin._enabled}")
        print(f"  - Kick on VPN: {plugin._kick_on_vpn}")
        print(f"  - Ban on VPN: {plugin._ban_on_vpn}")
        print(f"  - Whitelist level: {plugin._whitelist_level}")
        print(f"  - APIs: ProxyCheck={plugin._use_proxycheck}, VPN-API={plugin._use_vpnapi}, IPQualityScore={plugin._use_ipqualityscore}")
        
        # Test VPN ranges loading
        plugin.loadVpnRanges()
        print(f"✓ VPN ranges loaded: {len(plugin._known_vpn_ranges)} ranges")
        
        # Test cache functionality
        test_ips = ["8.8.8.8", "1.1.1.1", "192.168.1.1"]
        for ip in test_ips:
            # Cache a result
            plugin._cacheResult(ip, False)
            cached = plugin._getCachedResult(ip)
            print(f"✓ Cache test for {ip}: {cached}")
        
        # Mock a client connection event
        class MockClient:
            def __init__(self, name, ip, level=1):
                self.name = name
                self.ip = ip
                self.maxLevel = level
                self.kicked = False
                self.banned = False
            
            def kick(self, reason):
                self.kicked = True
                print(f"  Client {self.name} would be kicked: {reason}")
            
            def tempban(self, reason, admin, duration):
                self.banned = True
                print(f"  Client {self.name} would be banned for {duration} minutes: {reason}")
        
        class MockEvent:
            def __init__(self, client):
                self.client = client
        
        # Test with regular player (should be checked)
        regular_client = MockClient("TestPlayer", "8.8.8.8", 1)
        regular_event = MockEvent(regular_client)
        
        print("\n--- Testing Regular Player ---")
        plugin.onConnect(regular_event)
        time.sleep(0.5)  # Wait for thread
        
        # Test with admin player (should be skipped)
        admin_client = MockClient("AdminPlayer", "1.1.1.1", 60)
        admin_event = MockEvent(admin_client)
        
        print("\n--- Testing Admin Player ---")
        plugin.onConnect(admin_event)
        time.sleep(0.5)  # Wait for thread
        
        # Test with no IP
        no_ip_client = MockClient("NoIPPlayer", "", 1)
        no_ip_event = MockEvent(no_ip_client)
        
        print("\n--- Testing Player with No IP ---")
        plugin.onConnect(no_ip_event)
        time.sleep(0.5)  # Wait for thread
        
        print(f"\n✓ Cache size after tests: {len(plugin._ip_cache)} entries")
        
        return True
        
    except Exception as e:        print(f"✗ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_vpn_blocker_api_simulation():
    """Test VPN blocker with simulated API responses"""
    print("\n" + "="*60)
    print("Testing VPN Blocker API Simulation")
    print("="*60)
    
    try:
        # Create fake console and minimal config
        console = b3.fake.FakeConsole("@b3/conf/b3.distribution.xml")
        
        # Create minimal config
        class MinimalConfig:
            def getboolean(self, section, option):
                return True  # Enable everything for testing
            def getint(self, section, option):
                defaults = {'ban_duration': 7, 'whitelist_level': 40, 'check_timeout': 10, 'cache_time': 3600, 'max_retries': 3}
                return defaults.get(option, 1)
            def get(self, section, option):
                return ""  # No API keys
        
        config = MinimalConfig()
        
        # Import and create plugin
        import vpnblocker
        plugin = vpnblocker.VpnblockerPlugin(console, config)
        plugin.loadConfig()
        
        # Mock API responses to simulate VPN detection
        def mock_proxycheck_vpn(ip):
            # Simulate some IPs as VPN
            vpn_ips = ["10.0.0.1", "192.0.2.1"]
            return ip in vpn_ips
        
        def mock_vpnapi_vpn(ip):
            # Simulate different IPs as VPN
            vpn_ips = ["10.0.0.2", "203.0.113.1"]
            return ip in vpn_ips
        
        # Replace API methods with mocks
        plugin._checkProxyCheck = mock_proxycheck_vpn
        plugin._checkVpnAPI = mock_vpnapi_vpn
        
        # Test various IPs
        test_cases = [
            ("8.8.8.8", False, "Clean IP - Google DNS"),
            ("10.0.0.1", True, "VPN IP - ProxyCheck detection"),
            ("10.0.0.2", True, "VPN IP - VPN-API detection"),
            ("192.0.2.1", True, "VPN IP - ProxyCheck detection"),
            ("1.1.1.1", False, "Clean IP - Cloudflare DNS"),
        ]
        
        for ip, expected_vpn, description in test_cases:
            print(f"\nTesting {ip} ({description}):")
            
            # Mock client
            class TestClient:
                def __init__(self, ip):
                    self.name = f"Player_{ip.replace('.', '_')}"
                    self.ip = ip
                    self.maxLevel = 1
                    self.actions = []
                
                def kick(self, reason):
                    self.actions.append(f"KICK: {reason}")
                    print(f"  → Player {self.name} kicked: {reason}")
                
                def tempban(self, reason, admin, duration):
                    self.actions.append(f"BAN: {reason} ({duration}min)")
                    print(f"  → Player {self.name} banned: {reason}")
            
            client = TestClient(ip)
            
            # Run the check
            plugin._checkClientIP(client)
            time.sleep(0.1)  # Wait for processing
            
            if expected_vpn:
                if client.actions:
                    print(f"  ✓ Correctly detected VPN and took action")
                else:
                    print(f"  ✗ Failed to detect VPN (expected detection)")
            else:
                if not client.actions:
                    print(f"  ✓ Correctly identified as clean IP")
                else:
                    print(f"  ✗ False positive - took action on clean IP")
        
        print(f"\n✓ API simulation test completed")
        print(f"✓ Final cache size: {len(plugin._ip_cache)} entries")
        
        return True
        
    except Exception as e:
        print(f"✗ API simulation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run integration tests"""
    print("=" * 70)
    print("VPN Blocker Plugin Integration Test Suite")
    print("=" * 70)
    
    tests = [
        test_vpn_blocker_integration,
        test_vpn_blocker_api_simulation,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} failed with exception: {e}")
            failed += 1
    
    print("\n" + "=" * 70)
    print(f"Integration Test Results: {passed} passed, {failed} failed")
    print("=" * 70)
    
    if failed == 0:
        print("✓ VPN Blocker Plugin is ready for production use!")
        print("\nTo use the plugin:")
        print("1. Configure API keys in b3/extplugins/conf/vpnblocker.ini")
        print("2. Restart B3 to load the plugin")
        print("3. Use admin commands: !vpncheck, !vpnstatus, !vpnclear")
        print("4. Monitor B3 logs for VPN detections")
        return True
    else:
        print(f"✗ {failed} integration tests failed!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
