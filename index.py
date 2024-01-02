import pygetwindow
from pynput.keyboard import Controller
import time
import json
import os
import random

windows = pygetwindow.getWindowsWithTitle("Sky")

sky = None

for window in windows:
    if window.title == "Sky":
        sky = window

def focusWindow():
    try:
        sky.activate()
    except:
        sky.minimize()
        sky.restore()

keyboard = Controller()

# sky instrument mappings
key_maps = {
    '1Key0': 'y',
    '1Key1': 'u',
    '1Key2': 'i',
    '1Key3': 'o',
    '1Key4': 'p',
    '1Key5': 'h',
    '1Key6': 'j',
    '1Key7': 'k',
    '1Key8': 'l',
    '1Key9': ';',
    '1Key10': 'n',
    '1Key11': 'm',
    '1Key12': ',',
    '1Key13': '.',
    '1Key14': '/'
}

# Play Tunes
def play_music(song_data):
    song_notes = song_data[0]['songNotes']
    bpm = song_data[0]['bpm']

    # Start playing the music
    start_time = time.perf_counter()
    pause_time = 0

    for i, note in enumerate(song_notes):
        if (sky.isActive):
            note_time = note['time']
            note_key = note['key']

            if note_key in key_maps:
                keyboard.press(key_maps[note_key])
                time.sleep(0.02) # short delay to ensure note is pressed
                keyboard.release(key_maps[note_key]) #release key
            else:
                print("Skipped: Key not found in mapping")
                continue

            # Calculate the elapsed time since the start of the song
            elapsed_time = time.perf_counter() - start_time - pause_time

            if i < len(song_notes) - 1:
                next_note_time = song_notes[i + 1]['time']
                # Calculate the time to wait before playing the next note
                wait_time = (next_note_time - note_time) / 1000  # Convert milliseconds to seconds

                # Adjust wait time to maintain the desired tempo
                remaining_time = max(0, note_time / 1000 + wait_time - elapsed_time)

                print(f'pressing "{key_maps[note_key]}"')
                # hold down key for remaining time
                time.sleep(remaining_time)

        else:
            print("Sky is not focused, pausing...")
            paused_time_start = time.perf_counter()
            while (sky.isActive == False):
                time.sleep(1)
            paused_time_end = time.perf_counter()
            pause_time += paused_time_end - paused_time_start
            print("Resuming song...")

    print(f"Finished playing {song_data[0]['name']}")

if __name__ == '__main__':
    print("Please select a song with the corosponding number.")
    
    song_list = os.listdir("./songs/")

    for no, name in enumerate(song_list):
        if name.endswith(".json") or name.endswith(".skysheet"):
            print(f"{no+1}) {name.split('.')[0]}")

    selection = int(input("Please select a song: "))

    if selection-1 in range(len(song_list)):
        try:
            with open(f'songs/{song_list[selection-1]}', 'r', encoding="utf-8") as file:
                song_data = json.load(file)

        except FileNotFoundError:
            print("Song not found.")


        for i in range(3, 0, -1):
            print(f"Playing song in {i}")
            time.sleep(1)

        print(f"Now playing: '{song_data[0]['name']}'")

        focusWindow()
        play_music(song_data)

    else:
        print("invalid selection, exiting")
