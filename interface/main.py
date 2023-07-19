import tkinter as tk
from typing import Optional, Tuple, Union
import customtkinter as ctk
import os

from videoselector import video_selector
from videoplayer import video_player
from prediction_details import prediction_details

# ctk.set_appearance_mode('light')

class mainWindow(ctk.CTk):
    def __init__(self, fg_color: str | Tuple[str, str] | None = None, **kwargs):
        super().__init__(fg_color, **kwargs)    
        self.title("Titration Predictor")
        self.geometry("800x600")
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=15)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        
        self.top_bar = ctk.CTkFrame(self, corner_radius=0, bg_color='#a3a3a3')
        self.top_bar.grid(row=0, column=0, columnspan=2, sticky='nsew')
        self.upload_button = ctk.CTkButton(self.top_bar, text='Upload', command=self.upload, fg_color=('#a3a3a3','#4a4a4a'), corner_radius=0)
        self.upload_button.grid(row=0, column=0, sticky='nsew')
        self.export_button = ctk.CTkButton(self.top_bar, text='Export', command=self.export, fg_color=('#a3a3a3','#4a4a4a'), corner_radius=0)
        self.export_button.grid(row=0, column=1, sticky='nsew')
        
        self.video_selector = video_selector(self)
        self.video_selector.grid(row=1, column=0, sticky='nsew')
        
        self.video_player = video_player(self)
        self.video_player.grid(row=1, column=1, sticky='nsew')
        
        self.prediction_details = prediction_details(self)
        self.prediction_details.grid(row=1, column=2, columnspan=2, sticky='nsew')
        
        self.video_selector.active_video_change_callback = self.change_video
    
    def upload(self):
        file_paths = tk.filedialog.askopenfilenames(filetypes=[("Video Files", "*.mp4;*.avi;*.mov;*.mkv")])  
        for file_path in file_paths:
            self.video_selector.add_video(file_path) 
            
    def export(self):
        self.video_player.stop()
            
    def change_video(self):
        print('changing video')
        self.video_player.stop()
        self.video_player.progress_bar.update_section_colors(self.video_selector.active_video.parse_timeline())
        self.prediction_details.reset_bars()
        self.prediction_details.set_flask_swirl_probabilities(*self.video_selector.active_video.get_overall_prediction())
        self.after(100, lambda: self.video_player.load(self.video_selector.active_video.video_path))
        
if __name__ == '__main__':
    root = mainWindow()
    root.mainloop()