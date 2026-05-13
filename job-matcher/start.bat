@echo off
REM ============================================
REM JOB MATCHER - ONE-CLICK STARTER (Windows)
REM ============================================

echo.
echo =====================================
echo    JOB MATCHER - Starting Up...
echo =====================================
echo.

REM Check if Docker is available
docker --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker is not installed!
    echo.
    echo Please install Docker Desktop first:
    echo   1. Go to: https://www.docker.com/products/docker-desktop/
    echo   2. Click "Download for Windows"
    echo   3. Install it and restart your computer
    echo   4. Open Docker Desktop and wait until it says "Running"
    echo   5. Then double-click this file again
    echo.
    pause
    exit /b 1
)

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker is installed but not running!
    echo.
    echo Please open Docker Desktop and wait until it says "Running"
    echo Then double-click this file again.
    echo.
    pause
    exit /b 1
)

REM Create .env file if it doesn't exist
if not exist .env (
    echo Creating configuration file...
    copy .env.example .env >nul
    echo.
    echo =====================================
    echo   FIRST TIME SETUP
    echo =====================================
    echo.
    echo I created a .env file for you.
    echo.
    echo OPTIONAL: For SMART job matching, you need an OpenAI API key.
    echo The app works without it, just with basic matching.
    echo.
    set /p has_key="Do you have an OpenAI API key? (y/n): "
    if /i "%has_key%"=="y" (
        set /p api_key="Paste your OpenAI API key here: "
        if not "%api_key%"=="" (
            powershell -Command "(Get-Content .env) -replace 'OPENAI_API_KEY=sk-...', 'OPENAI_API_KEY=%api_key%' | Set-Content .env"
            echo Key saved!
        )
    ) else (
        echo No problem! The app will use basic matching.
    )
    echo.
    set /p email="What's your email? (for daily job digest, or press Enter to skip): "
    if not "%email%"=="" (
        powershell -Command "(Get-Content .env) -replace 'DIGEST_EMAIL_TO=your-email@gmail.com', 'DIGEST_EMAIL_TO=%email%' | Set-Content .env"
        powershell -Command "(Get-Content .env) -replace 'SMTP_USER=your-email@gmail.com', 'SMTP_USER=%email%' | Set-Content .env"
        echo Email saved!
    )
    echo.
)

echo Starting all services... (this may take 2-3 minutes the first time)
echo.

docker compose up --build -d

echo.
echo =====================================
echo   ALL DONE! Your Job Matcher is running!
echo =====================================
echo.
echo   Open your browser and go to:
echo.
echo   >>> http://localhost:3000 <<<
echo.
echo =====================================
echo.
echo   WHAT TO DO NEXT:
echo   1. Go to http://localhost:3000/settings
echo   2. Upload your CV (PDF or Word file)
echo   3. Set your job preferences
echo   4. Go back to Dashboard and click "Fetch New Jobs"
echo   5. Wait 30 seconds and refresh - you'll see matched jobs!
echo.
echo   TO STOP: Double-click stop.bat
echo.
pause
