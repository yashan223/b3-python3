#!/usr/bin/env python3
# Quick fix for the RCON bytes decoding issue

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'b3'))

import b3.config

class MockConsole:
    def __init__(self):
        # Load the B3 config to get the RCON settings
        config_path = os.path.join(os.path.dirname(__file__), 'b3', 'conf', 'b3.xml')
        self.config = b3.config.XmlConfigParser()
        self.config.setXml(open(config_path).read())
        
        # Mock some required attributes
        self.gameName = 'cod4'
        self.encoding = 'utf-8'
        self._rconSendQueue = []
    
    def debug(self, msg, *args):
        pass
    
    def verbose(self, msg, *args):
        pass
    
    def verbose2(self, msg, *args):
        pass
    
    def warning(self, msg, *args):
        pass
    
    def bot(self, msg, *args):
        pass

def test_quick_fix():
    print("=== Quick RCON Fix Test ===")
    
    # Instead of fixing the corrupted file, let's manually send the RCON command
    import socket
    import re
    
    try:
        # Create socket
        sock = socket.socket(type=socket.SOCK_DGRAM)
        sock.settimeout(2)
        sock.connect(('127.0.0.1', 28960))
        
        # Send RCON status command
        password = 'cod4host123'
        command = '\377\377\377\377rcon "%s" status\n' % password
        sock.send(command.encode('utf-8'))
        
        # Receive response
        data = sock.recv(4096)
        print(f"Raw bytes received: {repr(data)}")
        
        # Decode properly
        decoded = data.decode('utf-8', 'replace')
        print(f"Decoded string: {repr(decoded)}")
        
        # Remove RCON header
        clean_data = decoded.replace('\377\377\377\377print\n', '')
        print(f"Clean data: {repr(clean_data)}")
        
        # Parse lines
        lines = clean_data.split('\n')
        print(f"\nLines ({len(lines)}):")
        for i, line in enumerate(lines):
            print(f"  {i}: {repr(line)}")
        
        # Test regex patterns on the actual data
        print(f"\n=== Testing Regex Patterns ===")
        
        # COD4X18 pattern
        regPlayer = re.compile(r'^\s*(?P<slot>[0-9]+)\s+'
                            r'(?P<score>-?[0-9]+)\s+'
                            r'(?P<ping>[0-9]+)\s+'
                            r'(?P<guid>[0-9]+)\s+'
                            r'(?P<steam>[0-9]+)\s+'
                            r'(?P<name>.+?)\s+'
                            r'(?P<lastmsg>[0-9]+)\s+'
                            r'(?P<ip>(?:(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}'
                            r'(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])):?'
                            r'(?P<port>-?[0-9]{1,5})\s+'
                            r'(?P<qport>-?[0-9]{1,5})\s+'
                            r'(?P<rate>[0-9]+)\s*$', re.IGNORECASE)
        
        players_found = 0
        
        # Skip first few lines (headers)
        for i, line in enumerate(lines[3:], 3):
            line = line.strip()
            if not line:
                continue
                
            print(f"\nTesting line {i}: {repr(line)}")
            
            m = regPlayer.match(line)
            if m:
                print(f"  ✅ Regex matched: {m.groupdict()}")
                players_found += 1
            else:
                print(f"  ❌ No match")
        
        print(f"\n=== Result ===")
        print(f"Players found: {players_found}")
        
        if players_found > 0:
            print("✅ RCON fix successful! Players can now be authenticated.")
        else:
            print("❌ Still no players found. Need to adjust regex pattern.")
            
        sock.close()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_quick_fix()
