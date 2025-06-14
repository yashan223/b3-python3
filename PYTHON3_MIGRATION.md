# B3 Python 3 Conversion

This document describes the conversion of BigBrotherBot (B3) from Python 2.7 to Python 3.8+.

## What Was Changed

### Core Changes
1. **Python Version Requirements**:
   - Updated from Python 2.7 to Python 3.8+
   - Updated `setup.py` classifiers and `python_requires`
   - Updated version checks in `b3_run.py`

2. **Syntax Updates**:
   - Print statements → Print functions (`print "text"` → `print("text")`)
   - Exception handling (`except Exception, e:` → `except Exception as e:`)
   - Input functions (`raw_input()` → `input()`)
   - Print redirection (`print >> file` → `print(text, file=file)`)

3. **Import Updates**:
   - `urllib2` → `urllib.request` (with backward compatibility)
   - `types.StringType` → `str`
   - Removed Python 2 specific imports (`reload(sys)`, `sys.setdefaultencoding`)

4. **String Handling**:
   - Fixed bytes vs strings in file operations
   - Updated regex patterns for binary data

### Dependencies Updated
- `pymysql`: 0.6.6 → 1.0.2+
- `python-dateutil`: 2.4.2 → 2.8.0+  
- `feedparser`: 5.1.3 → 6.0.0+
- `requests`: 2.7.0 → 2.25.0+
- `psycopg2`: 2.6.1 → 2.9.0+ (optional)
- `paramiko`: 1.15.2 → 2.12.0+ (optional)

### Files Modified
- `b3_run.py` - Entry point version checks
- `setup.py` - Build configuration and requirements
- `requirements.txt` - Core dependencies
- `optional-requirements.txt` - Optional dependencies
- `b3/run.py` - Main runner exception handling
- `b3/update.py` - urllib2 imports and raw_input
- `b3/plugins/translator/__init__.py` - Python 2/3 compatibility
- Various test files - Print statements and exception syntax
- Debug tools in `b3/tools/debug/` - Print statements

## Installation

### Requirements
- Python 3.8 or higher
- pip (Python package installer)

### Fresh Installation
```bash
# Clone the repository
git clone https://github.com/BigBrotherBot/big-brother-bot.git
cd big-brother-bot

# Install dependencies
pip install -r requirements.txt

# Install optional dependencies (if needed)
pip install -r optional-requirements.txt

# Validate the installation
python validate_python3.py
```

### Upgrading from Python 2.7
1. **Backup your existing B3** installation and configuration files
2. Install Python 3.8+ on your system
3. Update your B3 installation with this converted version
4. Reinstall dependencies: `pip install -r requirements.txt`
5. Test with: `python validate_python3.py`
6. Restore your configuration files

## Validation

Run the validation script to ensure everything is working:
```bash
python validate_python3.py
```

This script tests:
- Python version compatibility
- Core module imports  
- Dependency availability
- Basic functionality

## Known Issues & Limitations

### Potential Compatibility Issues
1. **Custom Plugins**: Custom third-party plugins may need updating for Python 3
2. **Database Drivers**: Some database configurations may need driver updates
3. **Game Parser Plugins**: Individual game parsers may have Python 2 specific code

### Testing Required
- Game server connections (each parser needs testing)
- Database operations (MySQL, PostgreSQL, SQLite)
- All plugin functionality
- File I/O operations with various encodings

### Build System
- The cx_Freeze build system may need updates for Python 3
- InnoSetup installer scripts may need adjustment
- Some build dependencies are Python 2 specific

## Troubleshooting

### Import Errors
If you get import errors:
```bash
pip install --upgrade -r requirements.txt
```

### Encoding Issues
If you encounter encoding problems, ensure your system locale is set to UTF-8.

### Plugin Errors
For plugin-specific errors, check:
1. Plugin configuration files
2. Plugin dependencies 
3. Game-specific connection settings

## Compatibility Notes

### Backward Compatibility
- Configuration files remain compatible
- Database schemas are unchanged
- Plugin APIs are mostly unchanged

### Python Version Support
- **Minimum**: Python 3.8
- **Recommended**: Python 3.10+
- **Tested On**: Python 3.8, 3.9, 3.10, 3.11, 3.12

## Contributing

When making changes to the Python 3 version:
1. Ensure compatibility with Python 3.8+
2. Test with the validation script
3. Update tests as needed
4. Maintain backward compatibility for configs

## Migration Timeline

This conversion addresses the core Python 2 to 3 migration. Additional work may be needed for:
1. Full plugin ecosystem testing
2. Build system modernization  
3. Performance optimization
4. Modern Python features adoption
