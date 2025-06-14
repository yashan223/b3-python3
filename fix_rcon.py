# Let me create a minimal fix for the rcon.py readSocket method

def fix_rcon_file():
    """Apply the Python 3 bytes decoding fix to rcon.py"""
    
    rcon_file = 'b3/parsers/q3a/rcon.py'
    
    # First, let's see what the current corrupted state looks like
    with open(rcon_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find and fix the readSocket method
    # Look for the problematic str(sock.recv(size)) line
    
    if 'd = str(sock.recv(size))' in content:
        print("Found old Python 2 style sock.recv")
        content = content.replace(
            'd = str(sock.recv(size))',
            '''d_bytes = sock.recv(size)
            if d_bytes:
                # Decode bytes to string properly for Python 3
                d = d_bytes.decode(self.console.encoding or 'utf-8', 'replace')'''
        )
    
    # Also fix the if condition  
    if 'if d:' in content:
        content = content.replace(
            '''if d:
                # remove rcon header
                data += d.replace(self.rconreplystring, '')''',
            '''# Already handled in the if d_bytes block above
                # remove rcon header
                data += d.replace(self.rconreplystring, '')'''
        )
    
    # Check if the method is badly corrupted and needs complete replacement
    if 'def readSocket' in content and ('"""        if' in content or 'return data.strip()    def readSocket' in content):
        print("Method is corrupted, replacing entire readSocket method")
        
        # Find the method start and end
        import re
        
        # Pattern to match the entire readSocket method
        pattern = r'(    def readSocket\(self, sock, size=4096, socketTimeout=None\):.*?)(    def \w+|class \w+|\Z)'
        
        replacement_method = '''    def readSocket(self, sock, size=4096, socketTimeout=None):
        """
        Read data from the socket.
        :param sock: The socket from where to read data
        :param size: The read size
        :param socketTimeout: The socket timeout value
        """
        if socketTimeout is None:
            socketTimeout = self.socket_timeout

        data = ''
        readables, writeables, errors = select.select([sock], [], [sock], socketTimeout)

        if not len(readables):
            self.console.verbose('No readable socket')
            return ''

        while len(readables):
            d_bytes = sock.recv(size)

            if d_bytes:
                # Decode bytes to string properly for Python 3
                d = d_bytes.decode(self.console.encoding or 'utf-8', 'replace')
                # remove rcon header
                data += d.replace(self.rconreplystring, '')

            readables, writeables, errors = select.select([sock], [], [sock], socketTimeout)
            if len(readables):
                self.console.verbose('RCON: more data to read in socket')

        return data

'''
        
        match = re.search(pattern, content, re.DOTALL)
        if match:
            content = content[:match.start(1)] + replacement_method + match.group(2)
        else:
            print("Could not find method boundaries for replacement")
            return False
    
    # Write the fixed content back
    with open(rcon_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Fixed rcon.py readSocket method for Python 3")
    return True

if __name__ == '__main__':
    fix_rcon_file()
