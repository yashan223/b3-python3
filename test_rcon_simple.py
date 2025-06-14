#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'b3'))

from b3.parsers.q3a.rcon import Rcon

def test_rcon():
    print("=== Testing RCON Status Command ===")
    
    try:        # Create RCON connection
        rcon = Rcon(None, ('127.0.0.1', 28960), 'cod4host123')
        
        print("RCON connection created successfully")
        
        # Send status command
        response = rcon.sendRcon('status')
        print(f"RCON status response: {repr(response)}")
        
        if response:
            print("\n=== Raw Response Lines ===")
            lines = response.split('\n')
            for i, line in enumerate(lines):
                print(f"Line {i}: {repr(line)}")
                
        # Try to send another command
        response2 = rcon.sendRcon('serverinfo')
        print(f"\nRCON serverinfo response: {repr(response2)}")
        
    except Exception as e:
        print(f"RCON test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_rcon()
