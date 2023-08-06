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
        
        self._video_display = VideoDisplay(self, progress_bar_callback=self._seek_progress_bar, play_pause_callback=self._toggle_play_pause_controls, scaled=True, consistant_frame_rate=True, keep_aspect=True)
        self._video_display.grid(row=0, column=0, sticky="nsew")
        
        self._video_controls = VideoControls(self, video_display_callback=self._seek_video, play_pause_callback=self._toggle_play_pause_video, fast_forward_callback=self._fast_forward)
        self._video_controls.grid(row=1, column=0, sticky="nsew")
        
        self._video_progress_callback = video_progress_callback if video_progress_callback != None else lambda: None
        
        self._video_display.bind("<<Loaded>>", self._update_duration)
        self._video_display.bind("<<Ended>>", self._ended)
        
        self.update_video_bg()
        
    def load(self, path):
        self._video_path = path
        self._video_display.load(path)
        
    def stop(self):
        self._video_display.stop()
        self._toggle_play_pause_controls(False)
        self._seek_progress_bar(0)
        
    def get_current_timestamp(self):
        return self._video_display.current_duration()
        
    def update_progress_bar_color(self, colors):
        self._video_controls.update_section_colors(colors)
        
    def _ended(self, event):
        self._toggle_play_pause_controls(False)
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
        self._video_controls.seek(progress)
        self._video_controls.update_time_display(self._video_display.current_duration())
        self._video_progress_callback()
        
    def _toggle_play_pause_controls(self, state):
        self._video_controls.play_pause(state=state)
        
    def _toggle_play_pause_video(self, state):
        self._video_display.play_pause(state=state)
        
    def update_video_bg(self, mode=None):
        if mode is None:
            mode = ctk.get_appearance_mode()
        if mode == 'Light':
            self._video_display.configure(bg='#415A77')
        else:
            self._video_display.configure(bg='#0D1B2A')
         
if __name__ == "__main__":
    window = ctk.CTk()
    window.title("Video Playback Slider")
    window.geometry("800x600")

    video_display = VideoPlayer(window)
    video_display.pack(fill="both", expand=True)
    video_display.load('C:/Users/zedon/Documents/GitHub/PW-2023-LabAssist/Zedong_fullTitration_1.mp4')

    window.mainloop()
