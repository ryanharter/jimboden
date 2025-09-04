from flask import Flask, render_template, request, jsonify, send_file
import os
import random
import re

app = Flask(__name__)

# Configuration
AUDIO_FOLDER = 'static/audio'
THEMES_FOLDER = os.path.join(AUDIO_FOLDER, 'themes')
JIMBO_FOLDER = os.path.join(AUDIO_FOLDER, 'jimbo')
SOUNDBOARD_FOLDER = os.path.join(AUDIO_FOLDER, 'soundboard')

# Create directories if they don't exist
os.makedirs(THEMES_FOLDER, exist_ok=True)
os.makedirs(JIMBO_FOLDER, exist_ok=True)
os.makedirs(SOUNDBOARD_FOLDER, exist_ok=True)

# Track mapping
TRACKS = {
    "Main": "main theme.mp3",
    "Shop": "shop theme.mp3", 
    "Tarot": "tarot pack.mp3",
    "Planet": "planet.mp3",
    "Boss": "boss.mp3"
}

def count_syllables(word):
    """Count syllables in a word for voice synthesis"""
    word = word.lower()
    count = 0
    vowels = "aeiouy"
    if word and word[0] in vowels:
        count += 1
    for i in range(1, len(word)):
        if word[i] in vowels and word[i-1] not in vowels:
            count += 1
    if word.endswith("e"):
        count -= 1
    if count == 0:
        count += 1
    return count

@app.route('/')
def index():
    return render_template('soundboard.html')

@app.route('/switch_track', methods=['POST'])
def switch_track():
    """Handle track switching"""
    data = request.get_json()
    track = data.get('track')
    
    if track in TRACKS:
        audio_file = f'/static/audio/themes/{TRACKS[track]}'
        return jsonify({
            'success': True,
            'audio_file': audio_file,
            'track': track
        })
    
    return jsonify({'success': False, 'error': 'Invalid track'})

@app.route('/play_voices', methods=['POST'])
def play_voices():
    """Generate voice sequence from text"""
    data = request.get_json()
    sentence = data.get('sentence', '')
    
    if not sentence:
        return jsonify({'success': False, 'error': 'No text provided'})
    
    voices = []
    # Voice file mapping based on actual files
    voice_files = [
        '65-voice1-101soundboards.mp3',
        '66-voice10-101soundboards.mp3', 
        '67-voice11-101soundboards.mp3',
        '68-voice2-101soundboards.mp3',
        '69-voice3-101soundboards.mp3',
        '70-voice4-101soundboards.mp3',
        '72-voice6-101soundboards.mp3',
        '73-voice7-101soundboards.mp3',
        '74-voice8-101soundboards.mp3',
        '75-voice9-101soundboards.mp3'
    ]
    
    for word in sentence.split():
        syllables = count_syllables(word)
        for _ in range(syllables):
            # Get random voice file
            voice_file = random.choice(voice_files)
            voices.append(f'/static/audio/jimbo/{voice_file}')
    
    return jsonify({
        'success': True,
        'voices': voices
    })

@app.route('/play_sound/<sound_type>')
def play_sound(sound_type):
    """Play special sound effects"""
    sound_files = {
        'polychrome': '/static/audio/soundboard/59-polychrome1-101soundboards.mp3',
        'winner': '/static/audio/soundboard/80-win-101soundboards.mp3'
    }
    
    if sound_type in sound_files:
        return jsonify({
            'success': True,
            'audio_file': sound_files[sound_type]
        })
    
    return jsonify({'success': False, 'error': 'Invalid sound type'})

@app.route('/static/audio/<path:filename>')
def serve_audio(filename):
    """Serve audio files"""
    return send_file(os.path.join('static', 'audio', filename))

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
