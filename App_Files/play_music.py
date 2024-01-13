import os
import threading
import tkinter as tk

import pyglet.resource
from pytube import YouTube


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
    if self.music_player is None:
        print("Play music")
        self.music.config(text="Stop")
        self.music_player = pyglet.media.Player()
        self.music_player.queue(pyglet.resource.media("audio.mp3"))
        self.music_player.volume = 0.01
        self.music_player.seek(self.position)
        self.music_player.play()
        self.check_playback()
    else:
        if self.music_player.playing:
            print("Stop music")
            self.position = self.music_player.time
            self.music_player.pause()
            self.music.config(text="Play")
        else:
            print("Resume music")
            self.music.config(text="Stop")
            self.music_player.play()


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
