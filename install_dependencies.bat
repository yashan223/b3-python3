@echo off
echo ================================================
echo BigBrotherBot (B3) - Dependency Installation
echo ================================================
echo.
echo Installing required Python packages...
echo.

REM Check if pip is available
pip --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: pip is not installed or not in PATH
    echo Please install Python 3.8+ with pip included
    pause
    exit /b 1
)

REM Install core dependencies
echo Installing core dependencies...
pip install pymysql>=1.0.2 python-dateutil>=2.8.0 feedparser>=6.0.0 requests>=2.25.0 packaging>=21.0

if errorlevel 1 (
    echo.
    echo Installation failed! Trying with --user flag...
    pip install --user pymysql>=1.0.2 python-dateutil>=2.8.0 feedparser>=6.0.0 requests>=2.25.0 packaging>=21.0
)

echo.
echo Installing optional dependencies...
pip install psycopg2-binary>=2.9.0 paramiko>=2.12.0 langdetect>=1.0.9
if errorlevel 1 (
    pip install --user psycopg2-binary>=2.9.0 paramiko>=2.12.0 langdetect>=1.0.9
)

echo.
echo ================================================
echo Installation completed!
echo.
echo You can now run B3 with:
echo python b3_run.py
echo ================================================
pause
