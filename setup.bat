@echo off
REM InfoFlow MCP Server Setup Script for Windows

echo ========================================================
echo         InfoFlow MCP Server Setup
echo    Combat Information Overload ^& Decision Fatigue
echo ========================================================
echo.

REM Check Python version
echo Checking Python version...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [OK] Python %PYTHON_VERSION% found
echo.

REM Create virtual environment
echo Creating virtual environment...
if exist "venv\" (
    echo [SKIP] Virtual environment already exists
) else (
    python -m venv venv
    echo [OK] Virtual environment created
)
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo [OK] Virtual environment activated
echo.

REM Install dependencies
echo Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt
echo [OK] Dependencies installed
echo.

REM Create config file
if not exist "config.json" (
    echo Creating configuration file...
    copy config.example.json config.json
    echo [OK] Configuration file created
) else (
    echo [SKIP] Configuration file already exists
)
echo.

REM Initialize database
echo Initializing database...
python -c "from server import DatabaseManager; db = DatabaseManager(); print('Database initialized successfully!')"
echo [OK] Database initialized
echo.

echo ========================================================
echo              Setup Complete!
echo ========================================================
echo.
echo Next Steps:
echo 1. Run the server: python server.py
echo 2. Configure ChatGPT Custom GPT using custom_gpt_instructions.md
echo 3. Test the integration
echo.
echo For detailed instructions, see README.md
echo.
echo To start the server now, run:
echo   venv\Scripts\activate.bat
echo   python server.py
echo.
pause