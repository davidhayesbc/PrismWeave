@echo off
REM PrismWeave CLI Setup Script for Windows
REM This script helps you set up the CLI quickly

echo.
echo ================================
echo PrismWeave CLI Setup
echo ================================
echo.

REM Check if Node.js is installed
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: Node.js is not installed
    echo Please install Node.js 18 or higher from https://nodejs.org/
    exit /b 1
)

for /f "tokens=*" %%i in ('node --version') do set NODE_VERSION=%%i
echo ✓ Node.js found: %NODE_VERSION%

REM Check if npm is installed
where npm >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: npm is not installed
    exit /b 1
)

for /f "tokens=*" %%i in ('npm --version') do set NPM_VERSION=%%i
echo ✓ npm found: %NPM_VERSION%
echo.

REM Install dependencies
echo Installing dependencies...
call npm install
if %ERRORLEVEL% NEQ 0 (
    echo Error: Failed to install dependencies
    exit /b 1
)

echo.
echo Building the project...
call npm run build
if %ERRORLEVEL% NEQ 0 (
    echo Error: Failed to build project
    exit /b 1
)

echo.
echo ✓ Build complete!
echo.

REM Offer to install globally
set /p INSTALL_GLOBAL="Do you want to install the CLI globally? (y/n): "
if /i "%INSTALL_GLOBAL%"=="y" (
    echo.
    echo Installing globally...
    call npm link
    if %ERRORLEVEL% NEQ 0 (
        echo Warning: Global installation failed. You may need administrator privileges.
        echo You can still use the CLI with: npm start -- ^<command^>
    ) else (
        echo ✓ Global installation complete!
        echo.
        echo You can now use 'prismweave' command from anywhere!
    )
) else (
    echo Skipping global installation.
    echo You can run commands with: npm start -- ^<command^>
)

echo.
echo ==========================================
echo ✅ Setup complete!
echo.
echo Next steps:
echo 1. Configure GitHub credentials:
echo    prismweave config --set githubToken=your_token
echo    prismweave config --set githubRepo=owner/repo
echo.
echo 2. Test the connection:
echo    prismweave config --test
echo.
echo 3. Capture your first URL:
echo    prismweave capture https://example.com
echo.
echo For more help, see README.md or run:
echo    prismweave --help
echo ==========================================
echo.

pause
