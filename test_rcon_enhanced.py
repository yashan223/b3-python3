#!/usr/bin/env python3

"""
Enhanced RCON testing with B3's actual RCON implementation
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'b3'))

from b3.parsers.q3a.rcon import Rcon
import re

def test_rcon_with_b3():
    """Test RCON using B3's implementation"""
    print("=== Testing RCON with B3's Implementation ===")
    
    try:
        # Create RCON instance like B3 does
        rcon = Rcon(console=None, host="127.0.0.1", port=28960, password="cod4host123")
        
        print("Sending 'status' command...")
        response = rcon.write('status')
        
        print("Raw response:")
        print("="*60)
        print(repr(response))
        print("="*60)
        
        print("Formatted response:")
        print("="*60)
        print(response)
        print("="*60)
        
        # Split into lines and analyze
        lines = response.split('\n')
        print(f"Number of lines: {len(lines)}")
        
        for i, line in enumerate(lines):
            line = line.strip()
            if line:
                print(f"Line {i}: {repr(line)}")
        
        return response
        
    except Exception as e:
        print(f"❌ RCON test failed: {e}")
        return None

def test_regex_patterns_advanced(status_output):
    """Test various regex patterns against status output"""
    if not status_output:
        return
        
    print("\n=== Advanced Regex Pattern Testing ===")
    
    # COD4 standard regex (inherited from parent)
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
    
    # COD4X18 regex (current implementation)
    cod4x18_regex = re.compile(r'^\s*(?P<slot>[0-9]+)\s+'
                              r'(?P<score>[0-9-]+)\s+'
                              r'(?P<ping>[0-9]+)\s+'
                              r'(?P<guid>[0-9]+)\s+'
                              r'(?P<steam>[0-9]+)\s+'
                              r'(?P<name>.*?)\s+'
                              r'(?P<ip>(?:(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}'
                              r'(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])):?'
                              r'(?P<port>-?[0-9]{1,5})\s*', re.IGNORECASE | re.VERBOSE)
    
    # Alternative COD4X18 regex (more flexible)
    cod4x18_flexible = re.compile(r'^\s*(?P<slot>[0-9]+)\s+'
                                 r'(?P<score>[0-9-]+)\s+'
                                 r'(?P<ping>[0-9]+)\s+'
                                 r'(?P<guid>[0-9]+)\s+'
                                 r'(?P<steam>[0-9]+)\s+'
                                 r'(?P<name>.+?)\s+'
                                 r'(?P<lastmsg>[0-9]+)\s+'
                                 r'(?P<ip>(?:(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}'
                                 r'(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])):?'
                                 r'(?P<port>-?[0-9]{1,5})\s+'
                                 r'(?P<qport>-?[0-9]{1,5})\s+'
                                 r'(?P<rate>[0-9]+)\s*$', re.IGNORECASE | re.VERBOSE)
    
    lines = status_output.split('\n')
    
    player_lines = []
    for line in lines:
        line = line.strip()
        if line and not line.startswith('map:') and not line.startswith('num ') and line != 'disconnect':
            # Skip header lines
            if 'score' not in line and 'ping' not in line and 'guid' not in line:
                player_lines.append(line)
    
    print(f"Found {len(player_lines)} potential player lines:")
    for line in player_lines:
        print(f"  {repr(line)}")
    
    patterns = [
        ("COD4 Standard", cod4_regex),
        ("COD4X18 Current", cod4x18_regex), 
        ("COD4X18 Flexible", cod4x18_flexible)
    ]
    
    for pattern_name, pattern in patterns:
        print(f"\n--- Testing {pattern_name} ---")
        matches = 0
        for line in player_lines:
            match = pattern.match(line)
            if match:
                matches += 1
                print(f"✅ Matched: {match.groupdict()}")
            else:
                print(f"❌ Failed on: {repr(line)}")
        print(f"Total matches: {matches}/{len(player_lines)}")

if __name__ == "__main__":
    status_output = test_rcon_with_b3()
    test_regex_patterns_advanced(status_output)
    
    print("\n=== Recommendations ===")
    print("1. If RCON connection succeeded, check which regex pattern worked")
    print("2. Update the cod4x18.py parser with the correct pattern")
    print("3. Restart B3 and test in-game commands")
    print("4. Check B3 logs for successful authentication messages")
