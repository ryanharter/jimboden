#!/bin/bash

# Copy audio files to Flask static directory
echo "Setting up Flask Soundboard..."

# Create directories
mkdir -p static/audio/themes
mkdir -p static/audio/jimbo  
mkdir -p static/audio/soundboard

# Copy theme files
cp "themes/"*.mp3 "static/audio/themes/"

# Copy jimbo voice files
cp "jimbo/"*.mp3 "static/audio/jimbo/"

# Copy soundboard effects
cp "soundboard/"*.mp3 "static/audio/soundboard/"

echo "Audio files copied!"
echo "Now run: pip install flask"
echo "Then run: python web_soundboard.py"
echo "Visit: http://localhost:5000"
