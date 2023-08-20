import tkinter as tk
import customtkinter as ctk
from typing import Tuple
import numpy as np
import json

from video_selector import VideoSelector
from video_player import VideoPlayer
from prediction_details import PredictionDetails
from side_bar import SideBar
from settings_menu import SettingsMenu

from app.scripts import deploy

class mainWindow(ctk.CTk):
    def __init__(self, fg_color: str | Tuple[str, str] | None = None, **kwargs):
        super().__init__(fg_color, **kwargs)    
        self.title("LabAssist Titration Predictor")
        self.geometry("1920x1080")
        
        self._active_video = None
        
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=5)
        self.grid_columnconfigure(2, weight=20)
        self.grid_columnconfigure(3, weight=4)
        self.grid_rowconfigure(0, weight=1)
        
        self.predictor = deploy.multiThreadedVideoPredictor(num_workers=2)
        
        self.side_bar = SideBar(self, upload_callback=self.upload, export_callback=self.export, settings_callback=self.open_settings)
        self.side_bar.grid(row=0, column=0, sticky='nsew')
        
        self.video_selector = VideoSelector(self, active_video_change_callback=self.change_video, start_prediction_callback=self.predict_video)
        self.video_selector.grid(row=0, column=1, sticky='nsew')
        
        self.video_player = VideoPlayer(self, video_progress_callback=self.update_predictions)
        self.video_player.grid(row=0, column=2, sticky='nsew')
        
        self.prediction_details = PredictionDetails(self)
        self.prediction_details.grid(row=0, column=3, sticky='nsew')
        
        self.video_player.update_video_bg(ctk.get_appearance_mode())
        
        self.settings_menu = None
        self.prediction_details.log("Welcome to using LabAssist Titration Predictor")
        self.settings_update()
        
    def open_settings(self, event=None):
        if self.settings_menu is None or not self.settings_menu.winfo_exists():
            self.settings_menu = SettingsMenu(close_callback=self.settings_update, mode_switch_callback=self.video_player.update_video_bg)
        else:
            self.settings_menu.focus()

    def settings_update(self):
        with open('settings.json', 'r') as f:
            settings = json.load(f)
        self.predictor.update_workers(settings['num_workers'])
        ctk.set_appearance_mode(settings['appearance_mode'])
        self.video_player.update_video_bg()
        self.prediction_details.log("Settings updated")
        self.prediction_details.log(f"Number of prediction threads: {self.predictor.get_num_workers()}")
        self.prediction_details.log(f"Appearance mode: {settings['appearance_mode']}")
        
    def upload(self, event=None):
        file_paths = tk.filedialog.askopenfilenames(filetypes=[("Video Files", "*.mp4;*.avi;*.mov;*.mkv")])  
        for file_path in file_paths:
            self.video_selector.add_video(file_path) 
        self.prediction_details.log(f"Uploaded {len(file_paths)} videos")
            
    def export(self, event=None):
        def convert_np_array_to_list(arr):
            if isinstance(arr, np.ndarray):
                return arr.tolist()
            elif isinstance(arr, np.float32):
                return float(arr)
            raise TypeError(f"Object of type {type(arr)} is not JSON serializable")
        json_data = {}
        for video in self.video_selector._video_list:
            json_data[video.get_video_path()] = video.get_item_metadata()
        
        # removing illegal things from json
        filtered_json = {
            str(key): value for key, value in json_data.items()
            if value is not None and not isinstance(key, (int, float))
        }
        
        export_location = tk.filedialog.asksaveasfilename(filetypes=[("JSON Files", "*.json")])
        with open(export_location+'.json', 'w') as outfile:
            json.dump(filtered_json, outfile, default=convert_np_array_to_list, indent=4)
        self.prediction_details.log(f"Exported {len(filtered_json)} videos")
            
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
        self.prediction_details.log(f"Loaded {video.get_video_path()}")
        
        if 'yolo_preds' in metadata:
            self.prediction_details.set_tile_prediction(metadata['yolo_preds']['white_tile_present'])
            self.prediction_details.set_funnel_prediction(metadata['yolo_preds']['funnel_present'])
            self.prediction_details.set_burette_prediction(metadata['yolo_preds']['burette_too_high'])
        else:
            self.prediction_details.set_tile_prediction(None)
            self.prediction_details.set_funnel_prediction(None)
            self.prediction_details.set_burette_prediction(None)
        
    def predict_video(self, video):
        self.predictor.predict_video(video.get_video_path())
        self.predictor.remove_entry(video.get_video_path())
        video.prediction_callback(self.predictor)
        video.update_state('Predicting')
        video.set_progress(0)
        self.prediction_details.log(f"Started prediction for {video.get_video_path()}")
        
    def update_predictions(self):
        if self._active_video != None:
            metadata = self._active_video.get_item_metadata()
            current_timestamp = self.video_player.get_current_timestamp()//2*2 
            if 'softmax_preds' in metadata:
                try:
                    self.prediction_details.set_flask_swirl_probabilities(*metadata['softmax_preds'][current_timestamp])
                except:
                    self.prediction_details.set_flask_swirl_probabilities(0,0,0)
                
if __name__ == '__main__':
    def on_closing():
        root.predictor.kill_workers()
        root.destroy()
        root.quit()
    root = mainWindow()
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()