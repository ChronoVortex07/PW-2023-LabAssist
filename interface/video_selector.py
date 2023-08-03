import os
import sys
import numpy as np

import tkinter as tk
import customtkinter as ctk
import multiprocessing

sys.path.append('./')
from scripts import deploy
from selector_item import SelectorItem


class VideoSelector(ctk.CTkFrame):
    def __init__(self, *args, active_video_change_callback = None, start_prediction_callback = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        self.search_bar = ctk.CTkEntry(self, height=20, placeholder_text='search...')
        self.search_bar.grid(row=0, column=0, sticky="nsew", padx=10, pady=10, columnspan=2)
        
        self.select_all_checkbox = ctk.CTkCheckBox(self, text='', command=self.select_all)
        self.select_all_checkbox.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
        self.option_menu = ctk.CTkOptionMenu(self, values=[
            "Predict unlabelled tasks",
        ], command=self.execute_option_menu, width=200)
        self.option_menu.set("Predict unlabelled tasks")
        self.option_menu.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
        
        self.video_list_frame = ctk.CTkScrollableFrame(self)
        self.video_list_frame.grid(row=2, column=0, sticky="nsew", columnspan=2)
        
        self.video_list = []
        self.active_video = None
        self.video_prediction_queue = multiprocessing.Queue()
        self.predicting_video = None
        self.active_video_change_callback = active_video_change_callback if active_video_change_callback != None else lambda x: None
        self.start_prediction_callback = start_prediction_callback if start_prediction_callback != None else lambda x: None
        
        self.search_bar.bind('<KeyRelease>', lambda event: self.filter_videos(self.search_bar.get()))
        
    def add_video(self, video_path):
        video = SelectorItem(
            self.video_list_frame, 
            video_path=video_path, 
            set_active_callback=self.set_active_video,
            update_selection_callback=self.update_option_menu,
        )
        video.set_visibility(True)
        self.video_list.append(video)
        
    def select_all(self):    
        state = self.select_all_checkbox.get()
        for video in self.video_list:
            video.set_checkbox_state(state)
        self.update_option_menu()
    
    def execute_option_menu(self, choice):
        if choice == "Predict unlabelled tasks":
            for video in self.video_list:
                if video._video_prediction['overall_pred'] == 'Unlabelled':
                    self.video_prediction_queue.put(video.get_video_path())
            self.predict_videos()
        elif choice.startswith("Predict"):
            for video in self.video_list:
                if video.get_checkbox_state() == 1:
                    self.video_prediction_queue.put(video.get_video_path())
            self.predict_videos()
        elif choice.startswith("Delete"):
            for video in self.video_list.copy():
                if video.get_checkbox_state() == 1:
                    video.delete()
                    self.video_list.remove(video)
        elif choice.startswith("Set state"):
            for video in self.video_list:
                if video.get_checkbox_state() == 1:
                    video.update_state(state=choice.split()[-1])
    
    def predict_videos(self):
        print('Current queue size:', self.video_prediction_queue.qsize(), 'Predicting video:', self.predicting_video)
        if not self.video_prediction_queue.empty():
            while not self.video_prediction_queue.empty():
                predicting_path = self.video_prediction_queue.get()
                for video in self.video_list:
                    if video.get_video_path() == predicting_path:
                        self.start_prediction_callback(video)
                        break
                    
    def update_option_menu(self):
        selected_task_count = [video.get_checkbox_state() for video in self.video_list].count(1)
        if selected_task_count == len(self.video_list):
            self.option_menu.configure(values=[
                "Predict all tasks",
                "Delete all tasks",
                "Set state of all tasks to Correct",
                "Set state of all tasks to Incorrect",
                "Set state of all tasks to Unsure",
            ])
            self.option_menu.set("Predict all tasks")
        elif selected_task_count > 0:
            self.option_menu.configure(values=[
                f'Predict {selected_task_count} tasks',
                f'Delete {selected_task_count} tasks',
                f'Set state of {selected_task_count} tasks to Correct',
                f'Set state of {selected_task_count} tasks to Incorrect',
                f'Set state of {selected_task_count} tasks to Unsure',
                f'Set state of {selected_task_count} tasks to Unlabelled',
            ])
            self.option_menu.set(f'Predict {selected_task_count} tasks')
        elif selected_task_count == 0:
            self.option_menu.configure(values=[
                "Predict unlabelled tasks",
            ])
            self.option_menu.set("Predict unlabelled tasks")
            
    def set_active_video(self, video):
        if video.get_active():
            print(f"Active video changed to None")
            self.active_video = None
        else:
            print(f"Active video changed to {video.get_video_path()}")
            self.active_video = video
        for video in self.video_list:
            if video == self.active_video:
                video.configure(border_width=3, border_color='black')
            else:
                video.configure(border_width=0, border_color='black')
        self.active_video_change_callback(self.active_video)
        
    def filter_videos(self, filter_string):
        for video in self.video_list:
            video.set_visibility(False)
            if filter_string.lower() in video.get_video_path().lower():
                video.set_visibility(True)
                
            
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Video Selector")
    root.geometry("500x720")
    
    selector = VideoSelector(root)
    selector.pack(expand=True, fill="both")
    
    selector.add_video("video1.mp4")
    selector.add_video(r"C:\Users\zedon\Pictures\Saved Pictures\yae wallpaper.jpg")
    selector.add_video("video3.mp4")
    
    root.mainloop()