import tkinter as tk

import customtkinter as ctk

class PredictionDetails(ctk.CTkScrollableFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        
        self.caption = ctk.CTkLabel(self, text='Prediction Details', font=('Arial', 20), fg_color=('#757575', '#a3a3a3'), corner_radius=0, anchor='center')
        self.caption.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
        
        self.flask_swirl_prediction = ctk.CTkFrame(self, corner_radius=0, fg_color=('#919191', '#454545'))
        self.flask_swirl_prediction.grid(row=1, column=0, sticky='nsew', padx=10, pady=10)
        self.flask_swirl_prediction.grid_columnconfigure(0, weight=1)
        
        self.flask_swirl_prediction_caption = ctk.CTkLabel(self.flask_swirl_prediction, text='Flask Swirl Prediction', font=('Arial', 20), anchor='center')
        self.flask_swirl_prediction_caption.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
        
        self.correct_label = ctk.CTkLabel(self.flask_swirl_prediction, text='Correct', font=('Arial', 20), anchor='w')
        self.correct_label.grid(row=1, column=0, sticky='ew', padx=10)
        self.correct_bar = ctk.CTkProgressBar(self.flask_swirl_prediction, width=200, height=30, corner_radius=0, bg_color='#a3a3a3', fg_color='#a3a3a3')
        self.correct_bar.grid(row=2, column=0, sticky='ew', padx=10, pady=10)
        
        self.incorrect_label = ctk.CTkLabel(self.flask_swirl_prediction, text='Incorrect', font=('Arial', 20), anchor='w')
        self.incorrect_label.grid(row=3, column=0, sticky='ew', padx=10)
        self.incorrect_bar = ctk.CTkProgressBar(self.flask_swirl_prediction, width=200, height=30, corner_radius=0, bg_color='#a3a3a3', fg_color='#a3a3a3')
        self.incorrect_bar.grid(row=4, column=0, sticky='ew', padx=10, pady=10)
        
        self.unmoving_label = ctk.CTkLabel(self.flask_swirl_prediction, text='Unmoving', font=('Arial', 20), anchor='w')
        self.unmoving_label.grid(row=5, column=0, sticky='ew', padx=10)
        self.unmoving_bar = ctk.CTkProgressBar(self.flask_swirl_prediction, width=200, height=30, corner_radius=0, bg_color='#a3a3a3', fg_color='#a3a3a3')
        self.unmoving_bar.grid(row=6, column=0, sticky='ew', padx=10, pady=10)
        
        self.tile_prediction = ctk.CTkFrame(self, corner_radius=0, fg_color=('#919191', '#454545'))
        self.tile_prediction.grid(row=2, column=0, sticky='nsew', padx=10, pady=10)
        self.tile_prediction.grid_columnconfigure(0, weight=1)
        
        self.tile_prediction_caption = ctk.CTkLabel(self.tile_prediction, text='Tile Prediction', font=('Arial', 20), anchor='center')
        self.tile_prediction_caption.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
        
        self.tile_prediction_label = ctk.CTkLabel(self.tile_prediction, text='Tile Prediction', font=('Arial', 20), anchor='w')
        self.tile_prediction_label.grid(row=1, column=0, sticky='ew', padx=10)
        self.tile_prediction_bar = ctk.CTkProgressBar(self.tile_prediction, width=200, height=30, corner_radius=0, bg_color='#a3a3a3', fg_color='#a3a3a3')
        self.tile_prediction_bar.grid(row=2, column=0, sticky='ew', padx=10, pady=10)
        
        self.reset_bars()
        
    def reset_bars(self):
        self.correct_bar.set(0)
        self.incorrect_bar.set(0)
        self.unmoving_bar.set(0)
        self.tile_prediction_bar.set(0)
        
    def set_flask_swirl_probabilities(self, correct, unmoving, incorrect):
        self.correct_bar.set(correct)
        self.incorrect_bar.set(incorrect)
        self.unmoving_bar.set(unmoving)
        
    def set_tile_prediction(self, prediction):
        self.tile_prediction_bar.set(prediction)    
        
if __name__ == '__main__':
    root = tk.Tk()
    root.title('Prediction Details')
    root.geometry('800x600')
    prediction_details = PredictionDetails(root)
    prediction_details.pack(expand=True, fill='both')
    prediction_details.set_flask_swirl_probabilities(0.5, 0.3, 0.2)
    root.mainloop()