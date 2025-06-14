#!/usr/bin/env python3
"""
Script to check Python syntax errors in all .py files
"""
import os
import py_compile
import sys

def check_syntax_errors(root_dir):
    """Check for syntax errors in all Python files"""
    errors = []
    
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)                try:
                    py_compile.compile(file_path, doraise=True)
                    print(f"OK {file_path}")
                except py_compile.PyCompileError as e:
                    print(f"ERROR {file_path}: {e}")
                    errors.append((file_path, str(e)))
                except Exception as e:
                    print(f"ERROR {file_path}: {e}")
                    errors.append((file_path, str(e)))
    
    return errors

if __name__ == "__main__":
    root_dir = os.getcwd()
    print(f"Checking Python syntax in: {root_dir}")
    
    errors = check_syntax_errors(root_dir)
    
    if errors:
        print(f"\n{len(errors)} files with syntax errors:")
        for file_path, error in errors:
            print(f"  {file_path}: {error}")
        sys.exit(1)
    else:
        print(f"\nOK All Python files have valid syntax!")
        sys.exit(0)
