import pygetwindow
from pynput.keyboard import Controller, Key
from multiprocessing import Process
import math
import time
import json
import os
import threading

windows = pygetwindow.getWindowsWithTitle("Sky")

sky = None

for window in windows:
    if window.title == "Sky":
        sky = window

if sky == None:
    print("Sky was not detected, please open Sky before running this script.")
    quit()

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
    '1Key14': '/',
    '2Key0': 'y',
    '2Key1': 'u',
    '2Key2': 'i',
    '2Key3': 'o',
    '2Key4': 'p',
    '2Key5': 'h',
    '2Key6': 'j',
    '2Key7': 'k',
    '2Key8': 'l',
    '2Key9': ';',
    '2Key10': 'n',
    '2Key11': 'm',
    '2Key12': ',',
    '2Key13': '.',
    '2Key14': '/'
}

class KeyPressThread(threading.Thread):
    def __init__(self, note_time, note_key):
        super().__init__()
        self.note_time = note_time
        self.note_key = note_key

    def run(self):
        if self.note_key in key_maps:
            # uncomment the line below if you want spammed msgs during key presses
            # print(f'pressing "{key_maps[self.note_key]}"')
            keyboard.press(key_maps[self.note_key])
            time.sleep(0.02)  # short delay to ensure note is pressed
            keyboard.release(key_maps[self.note_key])  # release key
        else:
            print("Skipped: Key not found in mapping")


def progress_bar(current, total, song_name, replace_line, bar_length=40):
    fraction = current / total
    current = round(current)
    total = round(total)

    arrow = int(fraction * bar_length - 1) * '-' + '>'
    padding = int(bar_length - len(arrow)) * ' '

    ending = '\n' if current >= total else '\r'

    if (replace_line == 0):
        print(f'Now Playing: {song_name} [{arrow}{padding}] {math.floor(current/60)}:{math.floor(current%60):02}/{math.floor(total/60)}:{math.floor(total%60):02}')
    elif (replace_line == 1):
        print(f'Now Playing: {song_name} [{arrow}{padding}] {math.floor(current/60)}:{math.floor(current%60):02}/{math.floor(total/60)}:{math.floor(total%60):02}', end=ending)
    

def progress_loop(data):
    start_time = time.perf_counter()
    pause_time = 0
    elapsed_time = 0
    total = data['songNotes'][-1]["time"]/1000
    name = data["name"]
    paused = 1
    while (elapsed_time < total):
        if (sky.isActive):
            elapsed_time = time.perf_counter() - start_time - pause_time
            progress_bar(elapsed_time, total, name, paused)
            paused = 1
            time.sleep(1)
        else:
            pause_time_start = time.perf_counter()
            while (sky.isActive == False):
                time.sleep(1)
            pause_time_end = time.perf_counter()
            pause_time += pause_time_end - pause_time_start
            paused = 2

p_loop = Process(target=progress_loop)

def play_music(song_data):
    song_notes = song_data[0]['songNotes']

    # Start playing the music
    start_time = time.perf_counter()
    pause_time = 0

    # Start progress bar
    p_loop = Process(target=progress_loop, args=(song_data))
    p_loop.start()

    for i, note in enumerate(song_notes):
        if (sky.isActive):
            note_time = note['time']
            note_key = note['key']

            # Create a separate thread for pressing keys
            key_thread = KeyPressThread(note_time, note_key)
            key_thread.start()

            # Calculate the elapsed time since the start of the song
            elapsed_time = time.perf_counter() - start_time - pause_time

            if i < len(song_notes) - 1:
                next_note_time = song_notes[i + 1]['time']
                # Calculate the time to wait before playing the next note
                wait_time = (next_note_time - note_time) / 1000  # Convert milliseconds to seconds

                # Adjust wait time to maintain the desired tempo
                remaining_time = max(0, note_time / 1000 + wait_time - elapsed_time)

                # sleep until next key 
                time.sleep(remaining_time)

        else:
            print("\033[KSky is not focused, pausing... (Press Ctrl + C to exit the script)")
            paused_time_start = time.perf_counter()
            while (sky.isActive == False):
                time.sleep(1)
            paused_time_end = time.perf_counter()
            pause_time += paused_time_end - paused_time_start
            print("Resuming song...")
            progress_bar(elapsed_time + remaining_time, song_data[0]['songNotes'][-1]["time"]/1000, song_data[0]["name"], 1)

    final_time = round(song_data[0]['songNotes'][-1]["time"]/1000)
    progress_bar(final_time, final_time, song_data[0]["name"], 1)
    p_loop.terminate()
    print(f"Finished playing {song_data[0]['name']}")

#while (True):
if __name__ == '__main__':
    print("Please select a song with the corresponding number.")
    
    song_list = os.listdir("./songs/")

    for no, name in enumerate(song_list):
        if name.endswith(".json") or name.endswith(".skysheet"):
            print(f"{no+1}) {name.split('.')[0]}")

    selection = int(input("Please select a song: "))

    folder_name = "songs" #change this folder name if you are using a different folder

    if selection-1 in range(len(song_list)):
        try:
            with open(f'{folder_name}/{song_list[selection-1]}', 'r', encoding="utf-8") as file:
                song_data = json.load(file)

        except FileNotFoundError:
            print("Song not found.")

        for i in range(3, 0, -1):
            print(f"Playing song in {i}")
            time.sleep(1)

        #print(f"Now playing: '{song_data[0]['name']}'")

        focusWindow()
        play_music(song_data)

    else:
        print("invalid selection, exiting")
