import tkinter as tk
import customtkinter as ctk

import logging
import tkinter as tk

# logging.getLogger('libav').setLevel(logging.ERROR)  # removes warning: deprecated pixel format used
from video_controls import VideoControls
from video_display import VideoDisplay

class VideoPlayer(ctk.CTkFrame):
    def __init__(self, *args, video_progress_callback = None, **kwargs):
        super().__init__(*args, **kwargs)
        
        self._video_path = None
        self._paused = False
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        
        self._video_display = VideoDisplay(self, bg='black', progress_bar_callback=self._seek_progress_bar, play_pause_callback=self._toggle_play_pause, scaled=True, consistant_frame_rate=True, keep_aspect=True)
        self._video_display.grid(row=0, column=0, sticky="nsew")
        
        self._progress_bar = VideoControls(self, video_display_callback=self._seek_video, play_pause_callback=self._toggle_play_pause, fast_forward_callback=self._fast_forward)
        self._progress_bar.grid(row=1, column=0, sticky="nsew")
        
        self._video_progress_callback = video_progress_callback if video_progress_callback != None else lambda: None
        
        self._video_display.bind("<<Loaded>>", self._update_duration)
        self._video_display.bind("<<Ended>>", self._ended)
        
    def load(self, path):
        self._video_path = path
        self._video_display.load(path)
        
    def stop(self):
        self._video_display.stop()
        self._toggle_play_pause(False)
        self._seek_progress_bar(0)
        
    def get_current_timestamp(self):
        return self._video_display.current_duration()
        
    def update_progress_bar_color(self, colors):
        self._progress_bar.update_section_colors(colors)
        
    def _ended(self, event):
        self._toggle_play_pause(False)
        self._seek_progress_bar(1)
        
    def _update_duration(self, event):
        self._duration = self._video_display.video_info()["duration"]
        
    def _seek_video(self, progress):
        self._video_display.seek(progress*self._duration)
        self._video_progress_callback()
        
    def _fast_forward(self, val):
        new_timestamp = min(max(self._video_display.current_duration() + val, 0), self._duration)
        self._video_display.seek(new_timestamp)
        
    def _seek_progress_bar(self, progress):
        self._progress_bar.seek(progress)
        self._video_progress_callback()
        
    def _toggle_play_pause(self, state):
        if state:
            self._video_display.play()
            self._progress_bar.play_pause(True)
        else:
            self._video_display.pause()
            self._progress_bar.play_pause(False)
        
         
if __name__ == "__main__":
    window = ctk.CTk()
    window.title("Video Playback Slider")
    window.geometry("800x600")

    video_display = VideoPlayer(window, fg_color="black")
    video_display.pack(fill="both", expand=True)
    video_display.load('C:/Users/zedon/Documents/GitHub/PW-2023-LabAssist/Zedong_fullTitration_1.mp4')

    window.mainloop()
