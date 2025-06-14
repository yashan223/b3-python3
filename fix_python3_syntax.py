#!/usr/bin/env python3
"""
Script to automatically fix Python 2 to Python 3 exception syntax
"""

import os
import re
import glob

def fix_exception_syntax(file_path):
    """Fix exception syntax in a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        original_content = content
        
        # Fix except syntax: except Exception as e: -> except Exception as e:
        content = re.sub(
            r'except\s+([^,:\n]+),\s*([^:\n]+):',
            r'except \1 as \2:',
            content
        )
        
        # Fix print(statements that aren't functions yet)
        content = re.sub(
            r'print\s+([^(][^,\n]*)',
            r'print(\1)',
            content
        )
        
        # Fix print(>> file syntax)
        content = re.sub(
            r'print\s*>>\s*([^,\n]+),\s*([^,\n]+)',
            r'print(\2, file=\1)',
            content
        )
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Fixed: {file_path}")
            return True
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Main function to process all Python files"""
    base_dir = "."
    python_files = []
    
    # Find all Python files
    for root, dirs, files in os.walk(base_dir):
        # Skip some directories
        if any(skip in root for skip in ['.git', '__pycache__', '.pytest_cache', 'node_modules']):
            continue
            
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    print(f"Found {len(python_files)} Python files to process...")
    
    fixed_count = 0
    for file_path in python_files:
        if fix_exception_syntax(file_path):
            fixed_count += 1
    
    print(f"Fixed {fixed_count} files")

if __name__ == "__main__":
    main()
