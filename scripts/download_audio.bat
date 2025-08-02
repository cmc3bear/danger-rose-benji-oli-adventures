@echo off
REM Danger Rose Audio Download Script for Windows
REM Downloads high-quality family-friendly audio

echo 🎵 Danger Rose Audio Download Script
echo =====================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python from https://python.org
    pause
    exit /b 1
)

REM Check if we're in the right directory
if not exist "assets\" (
    echo ❌ Please run this script from the project root directory
    pause
    exit /b 1
)

REM Create directories
if not exist "assets\downloads\temp_audio" mkdir "assets\downloads\temp_audio"
if not exist "assets\audio\music" mkdir "assets\audio\music"
if not exist "assets\audio\sfx" mkdir "assets\audio\sfx"

echo ✓ Created directories

REM Run the Python download script
echo 📥 Starting download process...
python scripts\download_audio.py

if errorlevel 1 (
    echo ❌ Download script failed
    echo 💡 Manual download instructions are in AUDIO_DOWNLOAD_GUIDE.md
    pause
    exit /b 1
)

echo 🎉 Audio download complete!
echo 📁 Check assets\audio\music\ and assets\audio\sfx\ for new files
pause
