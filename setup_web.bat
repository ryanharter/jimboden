@echo off
echo Setting up Flask Soundboard...

REM Create directories
mkdir "static\audio\themes" 2>nul
mkdir "static\audio\jimbo" 2>nul
mkdir "static\audio\soundboard" 2>nul

REM Copy theme files
copy "themes\*.mp3" "static\audio\themes\" >nul 2>&1

REM Copy jimbo voice files
copy "jimbo\*.mp3" "static\audio\jimbo\" >nul 2>&1

REM Copy soundboard effects
copy "soundboard\*.mp3" "static\audio\soundboard\" >nul 2>&1

echo Audio files copied!
echo Now run: pip install flask
echo Then run: python web_soundboard.py
echo Visit: http://localhost:5000
pause
