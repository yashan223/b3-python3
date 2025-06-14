#!/usr/bin/env python3
"""
Fix remaining iteritems() usage in Python files
"""

import os
import re

def fix_iteritems_in_file(filepath):
    """Fix iteritems usage in a single file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        try:
            with open(filepath, 'r', encoding='latin-1') as f:
                content = f.read()
        except:
            print(f"Could not read {filepath}")
            return False
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return False

    original_content = content
    
    # Fix .items() -> .items()
    content = re.sub(r'\.iteritems\(\)', '.items()', content)
    
    if content != original_content:
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Fixed iteritems usage in {filepath}")
            return True
        except Exception as e:
            print(f"Error writing {filepath}: {e}")
            return False
    
    return False

def main():
    """Main function"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    files_fixed = 0
    
    for root, dirs, files in os.walk(base_dir):
        # Skip certain directories
        skip_dirs = ['.git', '__pycache__', '.pytest_cache', 'venv', 'env']
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                if fix_iteritems_in_file(filepath):
                    files_fixed += 1
    
    print(f"\nFixed iteritems usage in {files_fixed} files")

if __name__ == '__main__':
    main()
