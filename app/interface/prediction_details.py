import tkinter as tk
from PIL import Image
import customtkinter as ctk
from typing import Literal

class PredictionDetails(ctk.CTkScrollableFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.configure(fg_color=('#637A97','#1B263B'), corner_radius=0, width=300, scrollbar_button_color=('#778DA9','#415A77'))
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        
        self._prediction_icon = ctk.CTkImage(Image.open('app/src/prediction_icon.png'), size=(24, 24))
        self._caption_label = ctk.CTkLabel(self, image=self._prediction_icon, text='  Prediction Details', corner_radius=0, height=24, compound='left', font=('Arial', 20, 'bold'), anchor='center', text_color='#FFFFFF')
        self._caption_label.grid(row=0, column=0, sticky='nsew', padx=10, pady=30)
        
        self._prediction_frame = ctk.CTkFrame(self, corner_radius=15, fg_color=('#415A77','#0D1B2A'))
        self._prediction_frame.grid(row=1, column=0, sticky='nsew', padx=24, pady=24)
        self._prediction_frame.grid_columnconfigure(0, weight=1)
        
        self._flask_swirl_prediction_caption = ctk.CTkLabel(self._prediction_frame, text='Flask Swirl Prediction (confidence %)', font=('Arial', 16, 'bold'), anchor='center', text_color='#FFFFFF', wraplength=200)
        self._flask_swirl_prediction_caption.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
        
        self._flask_swirl_prediction_frame = ctk.CTkFrame(self._prediction_frame, corner_radius=10, fg_color=('#778DA9','#1B263B'))
        self._flask_swirl_prediction_frame.grid(row=1, column=0, sticky='nsew', padx=10, pady=10)
        self._flask_swirl_prediction_frame.grid_columnconfigure(0, weight=1)
        self._flask_swirl_prediction_frame.grid_columnconfigure(1, weight=100)
        self._flask_swirl_prediction_frame.grid_rowconfigure((0,1,2), weight=1)
        
        self._correct_label = ctk.CTkLabel(self._flask_swirl_prediction_frame, text='Correct', font=('Arial', 15, 'bold'), anchor='e', text_color=('#1B263B','#FFFFFF'))
        self._correct_label.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
        
        self._correct_bar = ctk.CTkProgressBar(self._flask_swirl_prediction_frame, height=25, fg_color='#415A77', progress_color='#06D6A0', corner_radius=0)
        self._correct_bar.grid(row=0, column=1, sticky='nsew', padx=10, pady=10)
        
        self._incorrect_label = ctk.CTkLabel(self._flask_swirl_prediction_frame, text='Incorrect', font=('Arial', 15, 'bold'), anchor='e', text_color=('#1B263B','#FFFFFF'))
        self._incorrect_label.grid(row=1, column=0, sticky='nsew', padx=10, pady=10)
        
        self._incorrect_bar = ctk.CTkProgressBar(self._flask_swirl_prediction_frame, height=25, fg_color='#415A77', progress_color='#EF476F', corner_radius=0)
        self._incorrect_bar.grid(row=1, column=1, sticky='nsew', padx=10, pady=10)
        
        self._stationary_label = ctk.CTkLabel(self._flask_swirl_prediction_frame, text='Stationary', font=('Arial', 15, 'bold'), anchor='e', text_color=('#1B263B','#FFFFFF'))
        self._stationary_label.grid(row=2, column=0, sticky='nsew', padx=10, pady=10)
        
        self._stationary_bar = ctk.CTkProgressBar(self._flask_swirl_prediction_frame, height=25, fg_color='#415A77', progress_color='#FFFFFF', corner_radius=0)
        self._stationary_bar.grid(row=2, column=1, sticky='nsew', padx=10, pady=10)
        
        self._object_detection_prediction_caption = ctk.CTkLabel(self._prediction_frame, text='Object Detection Prediction', font=('Arial', 16, 'bold'), anchor='center', text_color='#FFFFFF')
        self._object_detection_prediction_caption.grid(row=2, column=0, sticky='nsew', padx=10, pady=10)
        
        self._object_detection_prediction_frame = ctk.CTkFrame(self._prediction_frame, corner_radius=10, fg_color=('#778DA9','#1B263B'))
        self._object_detection_prediction_frame.grid(row=3, column=0, sticky='nsew', padx=10, pady=10)
        self._object_detection_prediction_frame.grid_columnconfigure((0,1), weight=1)
        
        self._tile_present_label = ctk.CTkLabel(self._object_detection_prediction_frame, text='Tile Present', font=('Arial', 15, 'bold'), anchor='w', text_color=('#1B263B','#FFFFFF'))
        self._tile_present_label.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
        
        self._tile_present_indicator = ctk.CTkLabel(self._object_detection_prediction_frame, text='-', font=('Arial', 15, 'bold'), anchor='center', text_color='#FFFFFF', fg_color='#415A77', corner_radius=6, height=36)
        self._tile_present_indicator.grid(row=0, column=1, sticky='nsew', padx=10, pady=10)
        
        self._funnel_present_label = ctk.CTkLabel(self._object_detection_prediction_frame, text='Funnel Present', font=('Arial', 15, 'bold'), anchor='w', text_color=('#1B263B','#FFFFFF'))
        self._funnel_present_label.grid(row=1, column=0, sticky='nsew', padx=10, pady=10)
        
        self._funnel_present_indicator = ctk.CTkLabel(self._object_detection_prediction_frame, text='-', font=('Arial', 15, 'bold'), anchor='center', text_color='#FFFFFF', fg_color='#415A77', corner_radius=6, height=36)
        self._funnel_present_indicator.grid(row=1, column=1, sticky='nsew', padx=10, pady=10)
        
        self._burette_position_label = ctk.CTkLabel(self._object_detection_prediction_frame, text='Burette Position', font=('Arial', 15, 'bold'), anchor='w', text_color=('#1B263B','#FFFFFF'))
        self._burette_position_label.grid(row=2, column=0, sticky='nsew', padx=10, pady=10)
        
        self._burette_position_indicator = ctk.CTkLabel(self._object_detection_prediction_frame, text='-', font=('Arial', 15, 'bold'), anchor='center', text_color='#FFFFFF', fg_color='#415A77', corner_radius=6, height=36)
        self._burette_position_indicator.grid(row=2, column=1, sticky='nsew', padx=10, pady=10)
        
        self._session_log_caption = ctk.CTkLabel(self._prediction_frame, text='Session Log', font=('Arial', 16, 'bold'), anchor='center', text_color='#FFFFFF')
        self._session_log_caption.grid(row=4, column=0, sticky='nsew', padx=10, pady=10)
        
        self._session_log_font = ctk.CTkFont(family='Cascadia Mono', size=12, weight='normal', slant='roman', underline=0, overstrike=0)
        
        self._session_log = ctk.CTkTextbox(self._prediction_frame, fg_color='black', text_color='white', corner_radius=10, height=500, width=0, font=self._session_log_font)
        self._session_log.grid(row=5, column=0, sticky='nsew', padx=10, pady=10)
        
        self.toggle_session_log(False)
        self.reset_predictions()
        
    def reset_predictions(self):
        self._correct_bar.set(0)
        self._incorrect_bar.set(0)
        self._stationary_bar.set(0)
        self._tile_present_indicator.configure(text='-', text_color='#FFFFFF')
        self._funnel_present_indicator.configure(text='-', text_color='#FFFFFF')
        self._burette_position_indicator.configure(text='-', text_color='#FFFFFF')
        
    def set_flask_swirl_probabilities(self, correct, stationary, incorrect):
        self._correct_bar.set(correct)
        self._stationary_bar.set(stationary)
        self._incorrect_bar.set(incorrect)
        
    def set_tile_prediction(self, prediction):
        if prediction == False:
            self._tile_present_indicator.configure(text='Absent', text_color='#EF476F')
        elif prediction == True:
            self._tile_present_indicator.configure(text='Present', text_color='#06D6A0')
        else:
            self._tile_present_indicator.configure(text='-', text_color='#FFFFFF')   
        
    def set_funnel_prediction(self, prediction):
        if prediction == False:
            self._funnel_present_indicator.configure(text='Absent', text_color='#06D6A0')
        elif prediction == True:
            self._funnel_present_indicator.configure(text='Present', text_color='#EF476F')
        else:
            self._funnel_present_indicator.configure(text='-', text_color='#FFFFFF')
        
    def set_burette_prediction(self, prediction):
        if prediction == False:
            self._burette_position_indicator.configure(text='Normal', text_color='#06D6A0')
        elif prediction == True:
            self._burette_position_indicator.configure(text='Too high', text_color='#EF476F')
        else:
            self._burette_position_indicator.configure(text='-', text_color='#FFFFFF')
            
    def toggle_session_log(self, active = True):
        if active:
            self._session_log.grid(row=5, column=0, sticky='nsew', padx=10, pady=10)
            self._session_log_caption.grid(row=4, column=0, sticky='nsew', padx=10, pady=10)
        else:
            self._session_log.grid_forget()
            self._session_log_caption.grid_forget()
        
    def log(self, text):
        self._session_log.insert('end', '>>> '+text+'\n')
        self._session_log.see('end')


if __name__ == '__main__':
    root = ctk.CTk()
    root.title('Prediction Details')
    root.geometry('800x600')
    
    # ctk.set_appearance_mode('light')
    
    prediction_details = PredictionDetails(root)
    prediction_details.pack(fill='y', side='right')
    prediction_details.set_flask_swirl_probabilities(0.5, 0.3, 0.2)
    prediction_details.set_tile_prediction('Present')
    prediction_details.set_funnel_prediction('Absent')
    prediction_details.set_burette_prediction('Normal')
    prediction_details.log('This is a test log')
    prediction_details.log('Prediction Completed')
    root.mainloop()