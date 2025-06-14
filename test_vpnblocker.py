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
        return ""  # No API keys for testing

class MockConsole:
    def debug(self, msg): print(f"DEBUG: {msg}")
    def info(self, msg): print(f"INFO: {msg}")
    def warning(self, msg): print(f"WARNING: {msg}")
    def error(self, msg): print(f"ERROR: {msg}")

class MockClient:
    def __init__(self, name, ip, level=0):
        self.name = name
        self.ip = ip
        self.maxLevel = level
    
    def kick(self, reason):
        print(f"KICK: {self.name} - {reason}")
    
    def tempban(self, reason, admin, duration):
        print(f"TEMPBAN: {self.name} - {reason} - {duration} minutes")

def test_vpn_detection():
    """Test VPN detection functionality"""
    print("=== VPN Blocker Plugin Test ===\n")
    
    # Create mock plugin
    console = MockConsole()
    config = MockConfig()
    plugin = VpnblockerPlugin(console, config)
    plugin.loadConfig()
    
    # Test IPs
    test_cases = [
        ("8.8.8.8", "Google DNS (should be clean)"),
        ("1.1.1.1", "Cloudflare DNS (should be clean)"),
        ("192.168.1.1", "Private IP (should be clean)"),
        ("127.0.0.1", "Localhost (should be clean)"),
    ]
    
    print("Testing IP ranges check:")
    for ip, description in test_cases:
        result = plugin._checkKnownRanges(ip)
        print(f"  {ip:15} ({description}): {'VPN' if result else 'Clean'}")
    
    print("\nTesting cache functionality:")
    plugin._cacheResult("1.2.3.4", True)
    cached = plugin._getCachedResult("1.2.3.4")
    print(f"  Cached result for 1.2.3.4: {cached}")
    
    print("\nTesting client handling:")
    clean_client = MockClient("CleanPlayer", "8.8.8.8", 0)
    admin_client = MockClient("AdminPlayer", "1.2.3.4", 60)
    
    print(f"  Clean client check (should pass): {clean_client.name}")
    print(f"  Admin client check (should be skipped): {admin_client.name}")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_vpn_detection()
