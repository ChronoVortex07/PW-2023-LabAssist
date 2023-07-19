import os
import sys
import numpy as np

import tkinter as tk
import customtkinter as ctk
import multiprocessing

sys.path.append('./')
from scripts import deploy


class video_selector(ctk.CTkFrame):
    def __init__(self, *args, **kwargs):
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
        ], command=self.execute_option_menu)
        self.option_menu.set("Predict unlabelled tasks")
        self.option_menu.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
        
        self.video_list_frame = ctk.CTkScrollableFrame(self)
        self.video_list_frame.grid(row=2, column=0, sticky="nsew", columnspan=2)
        
        self.video_list = []
        self.active_video = None
        self.video_prediction_queue = multiprocessing.Queue()
        self.predicting_video = None
        
    def add_video(self, video_path):
        video = self.video_object(
            self,
            self.video_list_frame, 
            video_path=video_path
        )
        video.pack(expand=True, fill="both", padx=10, pady=5)
        self.video_list.append(video)
        
    def select_all(self):    
        if self.select_all_checkbox.get() == 1:
            for video in self.video_list:
                video.select_box.select()
        else:
            for video in self.video_list:
                video.select_box.deselect()
        self.update_option_menu()
    
    def execute_option_menu(self, choice):
        if choice == "Predict unlabelled tasks":
            for video in self.video_list:
                if video.video_prediction['Label'] == 'Unlabelled':
                    self.video_prediction_queue.put(video.video_path)
                    print(f"Adding {video.video_path} to prediction queue")
            self.predict_videos()
        elif choice.startswith("Predict"):
            for video in self.video_list:
                if video.selected() == 1:
                    self.video_prediction_queue.put(video.video_path)
                    print(f"Adding {video.video_path} to prediction queue")
            self.predict_videos()
        elif choice.startswith("Delete"):
            for video in self.video_list.copy():
                if video.selected() == 1:
                    print(f"Deleting {video.video_path}")
                    video.delete()
                    self.video_list.remove(video)
        elif choice.startswith("Set state"):
            for video in self.video_list:
                if video.selected() == 1:
                    print(f"Setting state of {video.video_path} to {choice.split()[-1]}")
                    video.update_body_color(state=choice.split()[-1])
    
    def predict_videos(self):
        print('Current queue size:', self.video_prediction_queue.qsize(), 'Predicting video:', self.predicting_video)
        if self.predicting_video == None and not self.video_prediction_queue.empty():
            print('Predicting video')
            predicting_path = self.video_prediction_queue.get()
            for video in self.video_list:
                if video.video_path == predicting_path:
                    self.predicting_video = video
                    break
            print(f"Predicting {self.predicting_video.video_path}")
            self.predicting_video.predict()
        if self.predicting_video != None:
            if self.predicting_video.is_predicting == False:
                self.predicting_video = None
        if not self.video_prediction_queue.empty():
            self.after(1000, self.predict_videos)
                    
    def update_option_menu(self):
        selected_task_count = [video.selected() for video in self.video_list].count(1)
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
                f'Set state of {selected_task_count} tasks to Unsure'
                f'Set state of {selected_task_count} tasks to Unlabelled'
            ])
            self.option_menu.set(f'Predict {selected_task_count} tasks')
        elif selected_task_count == 0:
            self.option_menu.configure(values=[
                "Predict unlabelled tasks",
            ])
            self.option_menu.set("Predict unlabelled tasks")
            
    def set_active_video(self, video):
        print(f"Active video changed to {video.video_path}")
        self.active_video = video
        for video in self.video_list:
            if video == self.active_video:
                video.configure(border_width=3, border_color='black')
            else:
                video.configure(border_width=0, border_color='black')
        self.active_video_change_callback()
        
    class video_object(ctk.CTkButton):
        def __init__(self, video_selector, *args, video_path = None, color = '#808080', **kwargs):
            super().__init__(*args, **kwargs)
            
            self.video_selector_object = video_selector
            
            self.video_prediction = {
                'Label': 'Unlabelled',
                'prediction_timeline': None
            }
            self.is_predicting = False
            
            self.configure(
                text='',
                fg_color=color,
                hover_color=color,
            )
            self.grid_columnconfigure(0, weight=0)
            self.grid_columnconfigure(1, weight=1)
            self.grid_columnconfigure(2, weight=0)
            self.grid_rowconfigure(0, weight=1)
            self.grid_rowconfigure(1, weight=0)
            
            self.select_box = ctk.CTkCheckBox(self, text=None, width=0, bg_color=color, command=self.on_select)
            self.select_box.grid(row=0, column=0, sticky="nsew", padx=10, pady=10, rowspan=2)
            
            self.video_path_label = ctk.CTkLabel(self, text=os.path.basename(video_path), text_color='black', bg_color=color, anchor='w')
            self.video_path_label.grid(row=0, column=1, sticky="ew", padx=5, pady=10)
            
            self.progress_bar = ctk.CTkProgressBar(self, height=14)
            self.progress_bar.set(0)
            self.progress_bar.grid(row=1, column=1, sticky="ew", padx=5, pady=10)
            
            self.selected = self.select_box.get
            self.video_path = video_path
            
            self.state_display = ctk.CTkLabel(self, text=self.video_prediction['Label'], text_color='black', anchor='e')
            self.state_display.grid(row=1, column=2, sticky="nsew", padx=5, pady=10, rowspan=2)
            
            self.update_body_color()
            
            self.bind("<Button-1>", self.on_click)
            self.video_path_label.bind("<Button-1>", self.on_click)
            self.progress_bar.bind("<Button-1>", self.on_click)
            self.state_display.bind("<Button-1>", self.on_click)
            
        def update_body_color(self, state = None):
            if state is not None and state in ['Unlabelled', 'Correct', 'Incorrect', 'Unsure']:
                self.video_prediction['Label'] = state
            color_legend = {
                'Unlabelled': '#808080',
                'Correct': '#3f9c05',
                'Incorrect': '#b01207',
                'Unsure': '#dbac04',
            }
            self.color = color_legend[self.video_prediction['Label']]
            self.configure(
                fg_color=self.color,
                hover_color=self.color,
            )
            self.select_box.configure(bg_color=self.color)
            self.video_path_label.configure(bg_color=self.color)
            self.progress_bar.configure(bg_color=self.color)
            self.state_display.configure(bg_color=self.color, text=self.video_prediction['Label'])
            
        def on_select(self):
            self.video_selector_object.update_option_menu()
        
        def delete(self):
            self.destroy()
            del self
            
        def on_click(self, event):
            self.video_selector_object.set_active_video(self)
            
        def predict(self):
            pred_legend = {
                0: 'Correct',
                1: 'Unsure',
                2: 'Incorrect',
            }
            def callback(predictor):
                if not predictor.queue.empty():
                    self.progress_bar.configure(mode='determinate')
                    self.progress_bar.set(predictor.get_progress()/100)
                    self.after(1000, lambda: callback(predictor))
                else:
                    self.progress_bar.set(1)
                    self.is_predicting = False
                    results = predictor.get_result()
                    preds = np.array([x['pred'] for x in results])
                    self.update_body_color(pred_legend[np.argmax(np.mean(preds, axis=0))])
                    self.video_prediction['prediction_timeline'] = results
            self.is_predicting = True
            self.progress_bar.configure(mode='indeterminate')
            predictor = deploy.predict_video(self.video_path)
            callback(predictor)
            
        def parse_timeline(self):
            output = []
            color_legend = {
                0: '#3f9c05',
                1: '#dbac04',
                2: '#b01207',
            }
            if self.video_prediction['prediction_timeline'] is not None:
                for prediction in self.video_prediction['prediction_timeline']:
                    output.append(color_legend[np.argmax(prediction['pred'])])
                
                return output
            else:
                return None
            
        def get_overall_prediction(self):
            if self.video_prediction['prediction_timeline'] is not None:
                preds = np.array([x['pred'] for x in self.video_prediction['prediction_timeline']])
                mean_softmax = np.mean(preds, axis=0)
                return mean_softmax
            else:
                return (0, 0, 0)
            
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Video Selector")
    root.geometry("500x720")
    
    selector = video_selector(root)
    selector.pack(expand=True, fill="both")
    
    selector.add_video("video1.mp4")
    selector.add_video(r"C:\Users\zedon\Pictures\Saved Pictures\yae wallpaper.jpg")
    selector.add_video("video3.mp4")
    
    root.mainloop()