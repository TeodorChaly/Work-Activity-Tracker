import tkinter as tk
from tkinter import messagebox
from pytube import YouTube
import os


def download_audio(video_url, self, second_window):
    try:
        yt = YouTube(video_url)

        audio_stream = yt.streams.filter(only_audio=True).first()

        audio_stream.download(output_path="./", filename="audio.mp3")

        print("Music saved")

        second_window.destroy()
        self.music.config(text="Play")
        self.music.bind("<Button-1>", lambda event: play_music_switcher(self))

    except Exception as e:
        print("Error: ", e)


def play_music_switcher(self):
    print("Play music")
    self.music.config(text="Stop")
    self.music.bind("<Button-1>", lambda event: stop_music_switcher(self))


def stop_music_switcher(self):
    print("Stop music")
    self.music.config(text="Play")
    self.music.bind("<Button-1>", lambda event: play_music_switcher(self))


def audio_check(self):
    # Check if audio.mp3 exists
    if os.path.exists("audio.mp3"):
        return True
    else:
        return False


def audio_download(self):
    second_window = tk.Toplevel(self.root)
    second_window.title("Choose audio")

    url_label = tk.Label(second_window, text="Enter link of audio from Youtube:")
    url_label.pack()

    url_entry = tk.Entry(second_window, width=40)
    url_entry.pack()

    download_button = tk.Button(second_window, text="Save audio",
                                command=lambda: download_audio(url_entry.get(), self, second_window))
    download_button.pack()

    status_label = tk.Label(second_window, text="")
    status_label.pack()
