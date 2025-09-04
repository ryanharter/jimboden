import pygame
import tkinter as tk
from tkinter import ttk
import os
from mutagen.mp3 import MP3
import time
import random
from pydub import AudioSegment
import numpy as np

# Set FFmpeg paths explicitly
AudioSegment.ffmpeg = r"C:\ffmpeg\bin\ffmpeg.exe"
AudioSegment.ffprobe = r"C:\ffmpeg\bin\ffprobe.exe"

# Initialize pygame mixer
pygame.mixer.init()

# Set number of channels
pygame.mixer.set_num_channels(9)

# Path to themes
theme_path = r"c:\Users\ryanm\Desktop\jimbos den\themes"

# Path to jimbo voices
jimbo_path = os.path.join(os.path.dirname(__file__), "jimbo")

# Path to soundboard sounds
soundboard_path = os.path.join(os.path.dirname(__file__), "soundboard")

# Load voice sounds
voice_files = [f for f in os.listdir(jimbo_path) if f.endswith('.mp3')]
voice_sounds = [pygame.mixer.Sound(os.path.join(jimbo_path, f)) for f in sorted(voice_files)]

# Load soundboard sounds
polychrome_sound = pygame.mixer.Sound(os.path.join(soundboard_path, "59-polychrome1-101soundboards.mp3"))
winner_sound = pygame.mixer.Sound(os.path.join(soundboard_path, "80-win-101soundboards.mp3"))

# Load slowed main theme for GAME OVER - simplified approach
try:
    boss_path = os.path.join(theme_path, "boss.mp3")
    original_boss = AudioSegment.from_file(boss_path)
    slowed_boss = original_boss._spawn(original_boss.raw_data, overrides={'frame_rate': int(original_boss.frame_rate * 0.65)}).set_frame_rate(original_boss.frame_rate)
    slowed_samples = np.array(slowed_boss.get_array_of_samples())
    if slowed_boss.channels == 2:
        slowed_samples = slowed_samples.reshape(-1, 2)
    else:
        slowed_samples = slowed_samples.reshape(-1, 1)
    slowed_sound = pygame.sndarray.make_sound(slowed_samples)
    print("Slowed audio created successfully")
except Exception as e:
    print(f"Error creating slowed audio: {e}")
    # Fallback: use normal sound
    slowed_sound = pygame.mixer.Sound(os.path.join(theme_path, "boss.mp3"))

# Assume BPM for 7/4 time signature (adjust as needed)
BPM = 120
beat_duration = 60 / BPM  # seconds per beat

# Get track length using mutagen
sample_file = os.path.join(theme_path, "main theme.mp3")
audio = MP3(sample_file)
track_length = audio.info.length

# Load sounds
sounds = {
    "Main": pygame.mixer.Sound(os.path.join(theme_path, "main theme.mp3")),
    "Shop": pygame.mixer.Sound(os.path.join(theme_path, "shop theme.mp3")),
    "Tarot": pygame.mixer.Sound(os.path.join(theme_path, "tarot pack.mp3")),
    "Planet": pygame.mixer.Sound(os.path.join(theme_path, "planet.mp3")),
    "Boss": pygame.mixer.Sound(os.path.join(theme_path, "boss.mp3")),
}

# Channels
channels = {}
for i, name in enumerate(sounds.keys()):
    channels[name] = pygame.mixer.Channel(i)

# Start time for position tracking
start_time = time.time()

# Start all tracks on loop, but mute all except Main
active = "Main"
paused = False
for name, sound in sounds.items():
    channels[name].play(sound, loops=-1)
    if name != active:
        channels[name].set_volume(0)

# GUI
root = tk.Tk()
root.title("Soundboard")

# Mapping
button_names = {
    "Main": "main theme",
    "Shop": "shop theme",
    "Tarot": "tarot pack",
    "Planet": "planet",
    "Boss": "boss"
}

# Time label
time_label = tk.Label(root, text="00:00 / 00:00", font=("Arial", 12))
time_label.pack(pady=10)

# Track length label
length_label = tk.Label(root, text=f"Track Length: {track_length:.2f}s", font=("Arial", 10))
length_label.pack(pady=5)

# Slider for position (display only)
slider = ttk.Scale(root, from_=0, to=track_length, orient="horizontal", length=300)
slider.pack(pady=10)

def count_syllables(word):
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

def switch_to(name):
    global active
    def after_fade():
        if name == "Tarot":
            fade_in(channels[name])
        else:
            channels[name].set_volume(1)
        global active
        active = name
        if paused:
            channels[active].pause()
    # Immediate fade for smooth transition
    fade_out(channels[active], after_fade)

def fade_out(channel, callback):
    num_steps = 5  # Very short fade: 5 steps
    vol_step = 1.0 / num_steps
    vol = 1.0
    def step():
        nonlocal vol
        vol -= vol_step
        if vol < 0.0:
            vol = 0.0
        channel.set_volume(vol)
        if vol > 0.0:
            root.after(25, step)  # 25ms intervals for fast fade
        else:
            callback()
    step()

def fade_in(channel):
    num_steps = 5  # Very short fade: 5 steps
    vol_step = 1.0 / num_steps
    vol = 0.0
    def step():
        nonlocal vol
        vol += vol_step
        if vol > 1.0:
            vol = 1.0
        channel.set_volume(vol)
        if vol < 1.0:
            root.after(25, step)  # 25ms intervals for fast fade
    step()

def play_voices():
    sentence = text_entry.get()
    if not sentence:
        return
    voices = []
    for word in sentence.split():
        syl = count_syllables(word)
        for _ in range(syl):
            voices.append(random.choice(voice_sounds))
    play_sequence(voices)

def play_sequence(voices):
    if not voices:
        return
    channel = pygame.mixer.Channel(5)  # Use channel 5 for voices
    # Play with random length for speed variation (0.5 to 1.0 of full length)
    speed_factor = random.uniform(0.5, 1.0)
    maxtime = int(voices[0].get_length() * 1000 * speed_factor)
    channel.play(voices[0], maxtime=maxtime)
    if len(voices) > 1:
        root.after(maxtime, lambda: play_sequence(voices[1:]))

def play_polychrome():
    pygame.mixer.Channel(6).play(polychrome_sound)

def play_winner():
    # Lower music volume by 1/3 (to 66% of current volume)
    lower_music_volume()
    # Play winner sound
    channel = pygame.mixer.Channel(7)
    channel.play(winner_sound)
    # Schedule volume restoration after sound finishes
    sound_length = int(winner_sound.get_length() * 1000)
    root.after(sound_length, restore_music_volume)

winner_playing = False

def lower_music_volume():
    global winner_playing
    winner_playing = True
    for name in sounds:
        current_vol = channels[name].get_volume()
        channels[name].set_volume(current_vol * 0.66)

def restore_music_volume():
    global winner_playing
    if winner_playing:
        winner_playing = False
        for name in sounds:
            if name == active and not paused:
                channels[name].set_volume(1.0)
            elif name != active:
                channels[name].set_volume(0.0)

def game_over():
    # Immediate switch to Boss
    switch_to("Boss")
    # Start gradual slowdown over 2 seconds
    start_slowdown()

game_over_active = False

def start_slowdown():
    global game_over_active
    game_over_active = True
    steps = 100  # 100 steps over 5 seconds (50ms each)
    current_step = 0
    
    def gradual_slow():
        nonlocal current_step
        if current_step < steps and game_over_active:
            # Gradually reduce volume of normal track
            fade_ratio = 1.0 - (current_step / steps)
            channels["Boss"].set_volume(fade_ratio)
            
            # Gradually increase volume of slowed track
            slow_ratio = current_step / steps
            if current_step == 0:
                pygame.mixer.Channel(8).play(slowed_sound, loops=-1)
                pygame.mixer.Channel(8).set_volume(0)
            pygame.mixer.Channel(8).set_volume(slow_ratio)
            
            current_step += 1
            root.after(50, gradual_slow)
        elif game_over_active:
            # Final state: mute normal, full volume slowed
            channels["Boss"].set_volume(0)
            pygame.mixer.Channel(8).set_volume(1.0)
    
    gradual_slow()

def start_slowed_mode():
    # This function is no longer needed, keeping for compatibility
    pass

def reset():
    global game_over_active, winner_playing
    game_over_active = False
    winner_playing = False
    # Stop slowed if playing
    pygame.mixer.Channel(8).stop()
    # Stop winner if playing
    pygame.mixer.Channel(7).stop()
    # Restore normal playback
    switch_to("Boss")
    # Restore normal volume levels
    restore_music_volume()

def pause_music():
    global paused
    paused = True
    for name in sounds:
        channels[name].pause()

def resume_music():
    global paused
    paused = False
    for name in sounds:
        channels[name].unpause()

def update_display():
    pos = (time.time() - start_time) % track_length
    slider.set(pos)
    minutes = int(pos // 60)
    seconds = int(pos % 60)
    total_min = int(track_length // 60)
    total_sec = int(track_length % 60)
    time_label.config(text=f"{minutes:02d}:{seconds:02d} / {total_min:02d}:{total_sec:02d}")
    root.after(100, update_display)

buttons = {}
for name in button_names.keys():
    btn = ttk.Button(root, text=name, command=lambda n=name: switch_to(n))
    btn.pack(pady=10)
    buttons[name] = btn

# Text entry for voices
text_entry = tk.Entry(root, width=50)
text_entry.pack(pady=10)

# Play voices button
play_button = ttk.Button(root, text="Play Voices", command=play_voices)
play_button.pack(pady=10)

# Soundboard buttons
polychrome_button = ttk.Button(root, text="Play Polychrome", command=play_polychrome)
polychrome_button.pack(pady=5)

winner_button = ttk.Button(root, text="Play Winner", command=play_winner)
winner_button.pack(pady=5)

# GAME OVER and RESET buttons
game_over_button = ttk.Button(root, text="GAME OVER", command=game_over)
game_over_button.pack(pady=10)

reset_button = ttk.Button(root, text="RESET", command=reset)
reset_button.pack(pady=5)

# Pause and Resume buttons
pause_button = ttk.Button(root, text="Pause Music", command=pause_music)
pause_button.pack(pady=5)

resume_button = ttk.Button(root, text="Resume Music", command=resume_music)
resume_button.pack(pady=5)

# Start display update
update_display()

root.mainloop()
