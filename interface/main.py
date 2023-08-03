import tkinter as tk
import customtkinter as ctk
from typing import Tuple
import numpy as np
import json

from video_selector import VideoSelector
from video_player import VideoPlayer
from prediction_details import PredictionDetails

from scripts import deploy

ctk.set_default_color_theme('dark-blue')
ctk.set_appearance_mode('light')

class mainWindow(ctk.CTk):
    def __init__(self, fg_color: str | Tuple[str, str] | None = None, **kwargs):
        super().__init__(fg_color, **kwargs)    
        self.title("Titration Predictor")
        self.geometry("1920x1080")
        
        self._active_video = None
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=15)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        
        self.predictor = deploy.multiThreadedVideoPredictor()
        
        self.top_bar = ctk.CTkFrame(self, corner_radius=0, bg_color='#a3a3a3')
        self.top_bar.grid(row=0, column=0, columnspan=2, sticky='nsew')
        self.upload_button = ctk.CTkButton(self.top_bar, text='Upload', command=self.upload, fg_color=('#a3a3a3','#4a4a4a'), corner_radius=0)
        self.upload_button.grid(row=0, column=0, sticky='nsew')
        self.export_button = ctk.CTkButton(self.top_bar, text='Export', command=self.export, fg_color=('#a3a3a3','#4a4a4a'), corner_radius=0)
        self.export_button.grid(row=0, column=1, sticky='nsew')
        
        self.video_selector = VideoSelector(self, active_video_change_callback=self.change_video, start_prediction_callback=self.predict_video)
        self.video_selector.grid(row=1, column=0, sticky='nsew')
        
        self.video_player = VideoPlayer(self, video_progress_callback=self.update_predictions)
        self.video_player.grid(row=1, column=1, sticky='nsew')
        
        self.prediction_details = PredictionDetails(self)
        self.prediction_details.grid(row=1, column=2, columnspan=2, sticky='nsew')
    
    def upload(self):
        file_paths = tk.filedialog.askopenfilenames(filetypes=[("Video Files", "*.mp4;*.avi;*.mov;*.mkv")])  
        for file_path in file_paths:
            self.video_selector.add_video(file_path) 
            
    def export(self):
        def convert_np_array_to_list(arr):
            if isinstance(arr, np.ndarray):
                return arr.tolist()
            elif isinstance(arr, np.float32):
                return float(arr)
            raise TypeError(f"Object of type {type(arr)} is not JSON serializable")
        json_data = {}
        for video in self.video_selector.video_list:
            json_data[video.get_video_path()] = video.get_item_metadata()
        
        # removing illegal things from json
        filtered_json = {
            str(key): value for key, value in json_data.items()
            if value is not None and not isinstance(key, (int, float))
        }
        
        export_location = tk.filedialog.asksaveasfilename(filetypes=[("JSON Files", "*.json")])
        with open(export_location+'.json', 'w') as outfile:
            json.dump(filtered_json, outfile, default=convert_np_array_to_list, indent=4)
            
    def change_video(self, video):
        self._active_video = video
        self.video_player.stop()
        self.video_player.update_progress_bar_color(video.parse_timeline_colors())
        self.after(100, self.video_player.load, video.get_video_path())
        metadata = self._active_video.get_item_metadata()
        if 'softmax_preds' in metadata:
            self.prediction_details.set_flask_swirl_probabilities(*metadata['softmax_preds'][0])
        else:
            self.prediction_details.set_flask_swirl_probabilities(0,0,0)
        
    def predict_video(self, video):
        self.predictor.predict_video(video.get_video_path())
        self.predictor.remove_entry(video.get_video_path())
        video.prediction_callback(self.predictor)
        video.update_state('Predicting')
        video.set_progress(0)
        
    def update_predictions(self):
        if self._active_video != None:
            metadata = self._active_video.get_item_metadata()
            if 'softmax_preds' in metadata:
                try:
                    current_timestamp = self.video_player.get_current_timestamp()//2*2 
                    self.prediction_details.set_flask_swirl_probabilities(*metadata['softmax_preds'][current_timestamp])
                except:
                    pass
                    
        
if __name__ == '__main__':
    def on_closing():
        root.predictor.kill_workers()
        root.destroy()
        root.quit()
    root = mainWindow()
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()