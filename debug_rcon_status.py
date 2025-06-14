#!/usr/bin/env python3
"""
B3 RCON Status Debug Tool
Helps debug why player authentication is failing
"""

import sys
import os
import re

# Add B3 to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_rcon_connection():
    """Test RCON connection and status command"""
    print("=== B3 RCON Status Debug Tool ===")
    print()
    
    try:
        from b3.parsers.q3a.rcon import Rcon
        
        # Try to connect to the same server B3 is using
        rcon = Rcon('127.0.0.1', 28960, '')  # No password for testing
        
        print("🔧 Testing RCON connection to 127.0.0.1:28960...")
        
        # Try status command
        try:
            response = rcon.write('status')
            print("✅ RCON connection successful!")
            print("📋 Raw status response:")
            print("-" * 50)
            print(response)
            print("-" * 50)
            
            return response
            
        except Exception as e:
            print(f"❌ RCON command failed: {e}")
            return None
            
    except Exception as e:
        print(f"❌ RCON connection failed: {e}")
        return None

def test_regex_patterns(status_output):
    """Test regex patterns against actual status output"""
    if not status_output:
        print("⚠️ No status output to test regex patterns")
        return
        
    print("\n=== Testing Regex Patterns ===")
    
    # Original Q3A pattern
    regPlayer_orig = re.compile(r'^(?P<slot>[0-9]+)\s+'
                               r'(?P<score>[0-9-]+)\s+'
                               r'(?P<ping>[0-9]+)\s+'
                               r'(?P<guid>[0-9a-zA-Z]+)\s+'
                               r'(?P<name>.*?)\s+'
                               r'(?P<last>[0-9]+)\s+'
                               r'(?P<ip>[0-9.]+):(?P<port>[0-9-]+)\s+'
                               r'(?P<qport>[0-9]+)'
                               r'\s+(?P<rate>[0-9]+)$', re.IGNORECASE)
    
    # CoD4X18 pattern
    regPlayer_cod4x18 = re.compile(r'^\s*(?P<slot>[0-9]+)\s+'
                                  r'(?P<score>[0-9-]+)\s+'
                                  r'(?P<ping>[0-9]+)\s+'
                                  r'(?P<guid>[0-9]+)\s+'
                                  r'(?P<steam>[0-9]+)\s+'
                                  r'(?P<name>.*?)\s+'
                                  r'(?P<ip>(?:(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}'
                                  r'(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])):?'
                                  r'(?P<port>-?[0-9]{1,5})\s*', re.IGNORECASE | re.VERBOSE)
    
    lines = status_output.split('\n')
    print(f"📝 Analyzing {len(lines)} lines of output...")
    
    for i, line in enumerate(lines):
        if line.strip():
            print(f"\nLine {i}: {repr(line)}")
            
            # Test original pattern
            match1 = regPlayer_orig.match(line.strip())
            if match1:
                print(f"✅ Original Q3A pattern matched: {match1.groupdict()}")
            else:
                print("❌ Original Q3A pattern no match")
            
            # Test CoD4X18 pattern
            match2 = regPlayer_cod4x18.match(line.strip())
            if match2:
                print(f"✅ CoD4X18 pattern matched: {match2.groupdict()}")
            else:
                print("❌ CoD4X18 pattern no match")

def test_manual_status():
    """Provide manual testing instructions"""
    print("\n=== Manual Testing Instructions ===")
    print()
    print("If RCON connection failed, manually test with these steps:")
    print()
    print("1. Use an RCON tool (like COD4 RCON, COD4X RCON client)")
    print("2. Connect to: 127.0.0.1:28960")
    print("3. Send command: status")
    print("4. Copy the output and paste it here for analysis")
    print()
    print("Expected output format should be like:")
    print("map: mp_crash")
    print("num score ping guid                     name            lastmsg address               qport rate")
    print("--- ----- ---- ------------------------ --------------- ------- --------------------- ----- -----")
    print("  2     0   29 2310346616790373275      deep                 50 127.0.0.1:28960       6597  5000")
    print()
    print("If the format is different, the regex patterns need to be updated.")

def analyze_authentication_flow():
    """Analyze the authentication flow"""
    print("\n=== Authentication Flow Analysis ===")
    print()
    print("B3 Authentication Process:")
    print("1. Player joins game → B3 sees 'J;guid;slot;name' in log")
    print("2. B3 adds player to authentication queue")
    print("3. B3 sends RCON 'status' command to get player details")
    print("4. B3 parses status response to find player info")
    print("5. If found → creates client object")
    print("6. If not found → retries up to 10 times")
    print()
    print("Current Issue:")
    print("- B3 sees the join event ✅")
    print("- B3 sends status command ✅") 
    print("- Status response parsing fails ❌")
    print("- Player never gets authenticated ❌")
    print()
    print("Solution: Fix the regex pattern to match server's status output format")

def suggest_fixes():
    """Suggest potential fixes"""
    print("\n=== Suggested Fixes ===")
    print()
    print("1. **Check Game Server Configuration:**")
    print("   - Verify RCON is enabled and working")
    print("   - Check if sv_usesteam64id setting affects output format")
    print()
    print("2. **Update Regex Pattern:**")
    print("   - Capture actual status output format")
    print("   - Modify _regPlayer pattern in cod4x18.py")
    print("   - Test with different player scenarios")
    print()
    print("3. **Test B3 Configuration:**")
    print("   - Verify parser is set to 'cod4x18'")
    print("   - Check RCON password/settings in b3.xml")
    print("   - Ensure game log path is correct")
    print()
    print("4. **Alternative Solutions:**")
    print("   - Try using standard 'cod4' parser instead of 'cod4x18'")
    print("   - Disable Steam64 ID support temporarily")
    print("   - Check if B3Hide plugin affects status output")

def main():
    """Main function"""
    print("B3 Player Authentication Debug Tool")
    print("=" * 50)
    
    # Test RCON connection
    status_output = test_rcon_connection()
    
    # Test regex patterns
    test_regex_patterns(status_output)
    
    # Provide manual testing info
    test_manual_status()
    
    # Analyze the authentication flow
    analyze_authentication_flow()
    
    # Suggest fixes
    suggest_fixes()
    
    print("\n" + "=" * 50)
    print("💡 Next Steps:")
    print("1. Manually test RCON status command")
    print("2. Compare output format with regex patterns")
    print("3. Update regex in cod4x18.py if needed")
    print("4. Test with actual players in game")

if __name__ == "__main__":
    main()
