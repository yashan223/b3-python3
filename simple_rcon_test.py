#!/usr/bin/env python3

"""
Simple RCON test using the exact same method as B3
"""

import socket
import time

def simple_rcon_test():
    """Simple UDP RCON test"""
    print("=== Simple RCON Test ===")
    
    host = "127.0.0.1"
    port = 28960
    password = "cod4host123"
    
    try:
        # Create UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(3)
        
        # Q3A/COD4 RCON format
        command = f"\\rcon {password} Status"
        print(f"Sending: {command}")
        
        sock.sendto(command.encode(), (host, port))
        
        # Receive response
        data, addr = sock.recvfrom(8192)
        response = data.decode('utf-8', errors='ignore')
        
        print(f"Response from {addr}:")
        print("="*60)
        print(response)
        print("="*60)
        
        # Analyze the format
        lines = response.split('\n')
        print(f"\nTotal lines: {len(lines)}")
        
        for i, line in enumerate(lines):
            if line.strip():
                print(f"Line {i}: {repr(line)}")
        
        # Look for player data (skip first few lines)
        print("\nPotential player lines (after skipping headers):")
        for i, line in enumerate(lines[3:], 3):  # Skip first 3 lines like B3 does
            line = line.strip()
            if line and not line.startswith('---') and 'map:' not in line:
                print(f"Player line {i}: {repr(line)}")
                
                # Try to split by spaces to see the format
                parts = line.split()
                if len(parts) >= 5:
                    print(f"  Parts: {parts}")
                    print(f"  Possible: slot={parts[0]}, score={parts[1]}, ping={parts[2]}, guid={parts[3]}")
        
        sock.close()
        return response
        
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    response = simple_rcon_test()
    
    if response:
        print("\n=== Analysis ===")
        print("If you see player data above, note the format:")
        print("- How many columns are there?")
        print("- What's the order of slot, score, ping, guid, name, etc.?")
        print("- Are there any extra fields like Steam ID?")
        print("This will help us fix the regex pattern in cod4x18.py")
