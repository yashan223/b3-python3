#!/usr/bin/env python3

import sys
import os
import re
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'b3'))

# Import B3 config and create a minimal console mock
import b3.config

class MockConsole:
    def __init__(self):
        # Load the B3 config to get the RCON settings
        config_path = os.path.join(os.path.dirname(__file__), 'b3', 'conf', 'b3.xml')
        self.config = b3.config.XmlConfigParser()
        self.config.setXml(open(config_path).read())
          # Mock some required attributes
        self.gameName = 'cod4'
        self.encoding = 'utf-8'  # Required by RCON
        self._rconSendQueue = []
    
    def debug(self, msg, *args):
        if args:
            msg = msg % args
        print(f"DEBUG: {msg}")
    
    def verbose(self, msg, *args):
        if args:
            msg = msg % args
        print(f"VERBOSE: {msg}")
    
    def verbose2(self, msg, *args):
        if args:
            msg = msg % args
        print(f"VERBOSE2: {msg}")
    
    def warning(self, msg, *args):
        if args:
            msg = msg % args
        print(f"WARNING: {msg}")
    
    def bot(self, msg, *args):
        if args:
            msg = msg % args
        print(f"BOT: {msg}")

def test_real_rcon():
    print("=== Testing Real B3 RCON Status Parsing ===")
    
    try:
        from b3.parsers.q3a.rcon import Rcon
        
        # Create mock console
        console = MockConsole()
        
        # Get RCON settings from config
        rcon_ip = console.config.get('server', 'rcon_ip')
        rcon_password = console.config.get('server', 'rcon_password') 
        port = int(console.config.get('server', 'port'))
        
        print(f"Connecting to {rcon_ip}:{port} with password '{rcon_password}'")
        
        # Create RCON connection (same way B3 does it)
        rcon = Rcon(console, (rcon_ip, port), rcon_password)
        
        print("RCON connection created successfully")
        
        # Send status command (same way B3 does it)
        print("Sending 'status' command...")
        response = rcon.sendRcon('status')
        
        print(f"Raw RCON response: {repr(response)}")
        print(f"Response length: {len(response) if response else 0}")
        
        if response:
            print("\n=== Response Lines ===")
            lines = response.split('\n')
            for i, line in enumerate(lines):
                print(f"Line {i}: {repr(line)}")
            
            # Test the COD4X18 regex patterns
            print("\n=== Testing Regex Patterns ===")
            
            # COD4X18 full pattern (what I added)
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
                                r'(?P<rate>[0-9]+)\s*$', re.IGNORECASE | re.VERBOSE)
            
            # COD4X18 short pattern
            regPlayerShort = re.compile(r'^\s*(?P<slot>[0-9]+)\s+'
                                     r'(?P<score>-?[0-9]+)\s+'
                                     r'(?P<ping>[0-9]+)\s+'
                                     r'(?P<guid>[0-9]+)\s+'
                                     r'(?P<steam>[0-9]+)\s+'
                                     r'(?P<name>.+)', re.IGNORECASE | re.VERBOSE)
            
            # Standard COD4 pattern (from parent class)
            regPlayerStandard = re.compile(r'^\s*(?P<slot>[0-9]+)\s+'
                                      r'(?P<score>[0-9-]+)\s+'
                                      r'(?P<ping>[0-9]+)\s+'
                                      r'(?P<guid>[0-9]+)\s+'
                                      r'(?P<name>.*?)\s+'
                                      r'(?P<lastmsg>[0-9]+)\s+'
                                      r'(?P<ip>(?:(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}'
                                      r'(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])):?'
                                      r'(?P<port>-?[0-9]{1,5})\s*', re.IGNORECASE | re.VERBOSE)
            
            players_found = 0
            
            # Skip first 3 lines like B3 does
            for i, line in enumerate(lines[3:], 3):
                line = line.strip()
                if not line:
                    continue
                
                print(f"\nTesting line {i}: {repr(line)}")
                
                # Test COD4X18 full pattern
                m = regPlayer.match(line)
                if m:
                    print(f"  ✅ COD4X18 Full regex matched: {m.groupdict()}")
                    players_found += 1
                    continue
                
                # Test COD4X18 short pattern  
                m = regPlayerShort.match(line)
                if m:
                    print(f"  ✅ COD4X18 Short regex matched: {m.groupdict()}")
                    players_found += 1
                    continue
                
                # Test standard COD4 pattern
                m = regPlayerStandard.match(line)
                if m:
                    print(f"  ✅ Standard COD4 regex matched: {m.groupdict()}")
                    players_found += 1
                    continue
                    
                print(f"  ❌ No regex patterns matched")
            
            print(f"\n=== Summary ===")
            print(f"Total players found: {players_found}")
            
            if players_found == 0:
                print("❌ No players were matched by any regex pattern!")
                print("This explains why in-game commands don't work - players can't be authenticated.")
                print("\nTo fix this:")
                print("1. The regex patterns need to be updated to match the actual server output format")
                print("2. Or the server configuration needs to be changed to match expected format")
        
        else:
            print("❌ No response from RCON status command")
            print("This could mean:")
            print("1. RCON password is incorrect")
            print("2. Server is not responding to RCON commands")
            print("3. Network/firewall issue")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_real_rcon()
