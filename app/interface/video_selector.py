import sys

from PIL import Image
import tkinter as tk
import customtkinter as ctk
import multiprocessing

sys.path.append('./')
from selector_item import SelectorItem


class VideoSelector(ctk.CTkFrame):
    def __init__(self, *args, active_video_change_callback = None, start_prediction_callback = None, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.configure(fg_color=('#778DA9','#415A77'), corner_radius=0)
        
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        
        self._search_icon = ctk.CTkImage(Image.open('app/src/light/search.png'), Image.open('app/src/dark/search.png'), (20, 20))
        self._search_icon_label = ctk.CTkLabel(self, image=self._search_icon, text=None, corner_radius=0, width=28)
        self._search_icon_label.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        self._search_bar = ctk.CTkEntry(self, height=50, placeholder_text='Search...',placeholder_text_color=('#1B263B', '#FFFFFF'), fg_color=('#ACBFD7','#778DA9'), text_color=('#1B263B', '#FFFFFF'), border_width=0)
        self._search_bar.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        self._menu_frame = ctk.CTkFrame(self, fg_color=('#637A97','#1B263B'))
        self._menu_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10, columnspan=2)
        self._menu_frame.grid_columnconfigure(0, weight=0)
        self._menu_frame.grid_columnconfigure(1, weight=1)
        self._menu_frame.grid_rowconfigure(0, weight=0)
        self._menu_frame.grid_rowconfigure(1, weight=1)
        
        self._select_all_checkbox = ctk.CTkCheckBox(self._menu_frame, text=None, command=self.select_all, width=28, border_color=('#0D1B2A','#E0E1DD'), fg_color=('#778DA9','#1B263B'), hover=False)
        self._select_all_checkbox.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        self._option_menu = ctk.CTkOptionMenu(self._menu_frame, values=[
            "Predict unlabelled tasks",
        ], command=self.execute_option_menu, width=200, fg_color='#415A77', text_color='#FFFFFF', button_color='#778DA9', dropdown_fg_color='#415A77', dropdown_hover_color='#778DA9',dynamic_resizing=True)
        self._option_menu.set("Predict unlabelled tasks")
        self._option_menu.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        self._video_list_frame = ctk.CTkScrollableFrame(self._menu_frame, fg_color=('#415A77','#0D1B2A'), scrollbar_button_color=('#778DA9','#415A77'))
        self._video_list_frame.grid(row=1, column=0, sticky="nsew", columnspan=2, padx=10, pady=10)
        
        self._video_list = []
        self._active_video = None
        self._video_prediction_queue = multiprocessing.Queue()
        self.active_video_change_callback = active_video_change_callback if active_video_change_callback != None else lambda x: None
        self.start_prediction_callback = start_prediction_callback if start_prediction_callback != None else lambda x: None
        
        self._search_bar.bind('<KeyRelease>', lambda event: self.filter_videos(self._search_bar.get()))
        
    def add_video(self, video_path):
        video = SelectorItem(
            self._video_list_frame, 
            video_path=video_path, 
            set_active_callback=self.set_active_video,
            update_selection_callback=self.update_option_menu,
        )
        video.set_visibility(True)
        self._video_list.append(video)
        
    def select_all(self):    
        state = self._select_all_checkbox.get()
        for video in self._video_list:
            video.set_checkbox_state(state)
        self.update_option_menu()
    
    def execute_option_menu(self, choice):
        if choice == "Predict unlabelled tasks":
            for video in self._video_list:
                if video._video_prediction['overall_pred'] == 'Unlabelled':
                    self._video_prediction_queue.put(video.get_video_path())
            self.predict_videos()
        elif choice.startswith("Predict"):
            for video in self._video_list:
                if video.get_checkbox_state() == 1:
                    self._video_prediction_queue.put(video.get_video_path())
            self.predict_videos()
        elif choice.startswith("Delete"):
            for video in self._video_list.copy():
                if video.get_checkbox_state() == 1:
                    video.delete()
                    self._video_list.remove(video)
        elif choice.startswith("Set state"):
            for video in self._video_list:
                if video.get_checkbox_state() == 1:
                    video.update_state(state=choice.split()[-1])
    
    def predict_videos(self):
        if not self._video_prediction_queue.empty():
            while not self._video_prediction_queue.empty():
                predicting_path = self._video_prediction_queue.get()
                for video in self._video_list:
                    if video.get_video_path() == predicting_path:
                        video.update_state(state='Predicting')
                        self.start_prediction_callback(video)
                        break
                    
    def update_option_menu(self):
        selected_task_count = [video.get_checkbox_state() for video in self._video_list].count(1)
        if selected_task_count == len(self._video_list):
            self._option_menu.configure(values=[
                "Predict all tasks",
                "Delete all tasks",
                "Set state of all tasks to Correct",
                "Set state of all tasks to Incorrect",
                "Set state of all tasks to Unsure",
                "Set state of all tasks to Unlabelled"
            ])
            self._option_menu.set("Predict all tasks")
        elif selected_task_count > 0:
            self._option_menu.configure(values=[
                f'Predict {selected_task_count} tasks',
                f'Delete {selected_task_count} tasks',
                f'Set state of {selected_task_count} tasks to Correct',
                f'Set state of {selected_task_count} tasks to Incorrect',
                f'Set state of {selected_task_count} tasks to Unsure',
                f'Set state of {selected_task_count} tasks to Unlabelled',
            ])
            self._option_menu.set(f'Predict {selected_task_count} tasks')
        elif selected_task_count == 0:
            self._option_menu.configure(values=[
                "Predict unlabelled tasks",
            ])
            self._option_menu.set("Predict unlabelled tasks")
            
    def set_active_video(self, video):
        if video.get_active():
            print(f"Active video changed to None")
            self._active_video = None
        else:
            print(f"Active video changed to {video.get_video_path()}")
            self._active_video = video
        for video in self._video_list:
            if video == self._active_video:
                video.set_active(True)
            else:
                video.set_active(False)
        self.active_video_change_callback(self._active_video)
        
    def filter_videos(self, filter_string):
        for video in self._video_list:
            video.set_visibility(False)
            if filter_string.lower() in video.get_video_path().lower():
                video.set_visibility(True)
                
            
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Video Selector")
    root.geometry("500x720")
    
    # ctk.set_appearance_mode('light')
    
    selector = VideoSelector(root)
    selector.pack(expand=True, fill="both")
    
    selector.add_video('Video_1.mp4')
    selector.add_video('Video_2.mp4')
    selector.add_video('Video_3.mp4')
    selector.add_video('Video_4.mp4')
    selector.add_video('Video_5.mp4')
    selector.add_video('Video_6.mp4')
    
    root.mainloop()