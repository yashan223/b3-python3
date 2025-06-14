#!/usr/bin/env python3

"""
Test RCON connection and status command output
"""

import sys
import socket
import time

def test_rcon_connection():
    """Test basic RCON connection and status command"""
    print("=== Testing RCON Connection ===")
    
    # RCON settings from b3.xml
    rcon_ip = "127.0.0.1"
    rcon_port = 28960
    rcon_password = "cod4host123"
    
    try:
        # Create UDP socket for RCON
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(5)
        
        # COD4 RCON command format
        rcon_command = f"\\rcon {rcon_password} status"
        
        print(f"Connecting to {rcon_ip}:{rcon_port}")
        print(f"Sending command: {rcon_command}")
        
        # Send RCON command
        sock.sendto(rcon_command.encode('utf-8'), (rcon_ip, rcon_port))
        
        # Receive response
        response, addr = sock.recvfrom(4096)
        response_str = response.decode('utf-8', errors='ignore')
        
        print(f"Response received from {addr}:")
        print("="*60)
        print(response_str)
        print("="*60)
        
        # Parse the response
        lines = response_str.split('\n')
        for i, line in enumerate(lines):
            print(f"Line {i}: {repr(line)}")
        
        sock.close()
        return response_str
        
    except socket.timeout:
        print("❌ RCON connection timed out")
        print("Possible issues:")
        print("1. Game server is not running")
        print("2. RCON is disabled on server")
        print("3. Wrong RCON password")
        print("4. Server is not listening on the specified port")
        return None
        
    except Exception as e:
        print(f"❌ RCON connection failed: {e}")
        return None

def test_regex_patterns(status_output):
    """Test regex patterns against actual status output"""
    if not status_output:
        return
        
    print("\n=== Testing Regex Patterns ===")
    
    import re
    
    # COD4 standard regex
    cod4_regex = re.compile(r'^\s*(?P<slot>[0-9]+)\s+'
                           r'(?P<score>[0-9-]+)\s+'
                           r'(?P<ping>[0-9]+)\s+'
                           r'(?P<guid>[0-9a-f]+)\s+'
                           r'(?P<name>.*?)\s+'
                           r'(?P<last>[0-9]+?)\s*'
                           r'(?P<ip>(?:(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}'
                           r'(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])):?'
                           r'(?P<port>-?[0-9]{1,5})\s*'
                           r'(?P<qport>-?[0-9]{1,5})\s+'
                           r'(?P<rate>[0-9]+)$', re.IGNORECASE | re.VERBOSE)
    
    # COD4X18 regex (with B3Hide)
    cod4x18_regex = re.compile(r'^\s*(?P<slot>[0-9]+)\s+'
                              r'(?P<score>[0-9-]+)\s+'
                              r'(?P<ping>[0-9]+)\s+'
                              r'(?P<guid>[0-9]+)\s+'
                              r'(?P<steam>[0-9]+)\s+'
                              r'(?P<name>.*?)\s+'
                              r'(?P<ip>(?:(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}'
                              r'(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])):?'
                              r'(?P<port>-?[0-9]{1,5})\s*', re.IGNORECASE | re.VERBOSE)
    
    lines = status_output.split('\n')
    
    print("Testing COD4 standard regex:")
    for line in lines:
        line = line.strip()
        if line and not line.startswith('map:') and not line.startswith('num '):
            match = cod4_regex.match(line)
            if match:
                print(f"✅ COD4 regex matched: {match.groupdict()}")
            else:
                print(f"❌ COD4 regex failed on: {repr(line)}")
    
    print("\nTesting COD4X18 regex:")
    for line in lines:
        line = line.strip()
        if line and not line.startswith('map:') and not line.startswith('num '):
            match = cod4x18_regex.match(line)
            if match:
                print(f"✅ COD4X18 regex matched: {match.groupdict()}")
            else:
                print(f"❌ COD4X18 regex failed on: {repr(line)}")

if __name__ == "__main__":
    status_output = test_rcon_connection()
    test_regex_patterns(status_output)
    
    print("\n=== Next Steps ===")
    print("1. If RCON connection failed, check:")
    print("   - Game server is running")
    print("   - RCON password is correct")
    print("   - Server port is correct")
    print("2. If regex patterns failed, we need to:")
    print("   - Update the regex patterns in cod4x18.py")
    print("   - Or fix the parser selection logic")
    print("3. Test with actual players in the game")
