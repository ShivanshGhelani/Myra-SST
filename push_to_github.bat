@echo off
REM Script to help push to GitHub

echo Preparing to push to GitHub...

REM Initialize git if not already done
if not exist ".git" (
    echo Initializing git repository...
    git init
)

REM Run directory setup to ensure all required directories exist
python setup_dirs.py

REM Add all files
echo Adding files to git...
git add .

REM Prompt for commit message
set /p commit_msg="Enter commit message: "
git commit -m "%commit_msg%"

REM Check if remote exists
git remote -v | findstr "origin" > nul
if %errorlevel% neq 0 (
    echo Remote 'origin' not found.
    set /p repo_url="Enter your GitHub repository URL: "
    git remote add origin %repo_url%
)

REM Push to GitHub
echo Pushing to GitHub...
git push -u origin main

echo Done!
pause
