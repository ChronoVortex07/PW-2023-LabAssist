import tkinter as tk
import customtkinter as ctk
import os

class SelectorItem(ctk.CTkFrame):
    def __init__(self, *args, video_path = 'video_path', color = '#808080', set_active_callback = None, update_selection_callback = None, **kwargs):
        super().__init__(*args, **kwargs)
        
        self._video_prediction = {
            'overall_pred': 'Unlabelled',
            'prediction_timeline': None
        }
        
        self._color_legend = {
            'Unlabelled': '#808080',
            'Predicting': '#808080',
            'Correct': '#06D671',
            'Incorrect': '#EF476F',
            'Unsure': '#FFD166',
        }
        
        self._video_path = tk.StringVar(self, value=video_path)
        self._is_active = False
        self.set_active_callback = set_active_callback if set_active_callback != None else lambda x: x
        self.update_selection_callback = update_selection_callback if update_selection_callback != None else lambda: None
        
        self.configure(
            fg_color=color,
            height=120,
        )
        self.bind('<Button-1>', self.on_click)
        
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        
        self._select_box = ctk.CTkCheckBox(self, text=None, width=0, bg_color=color, command=self.on_select)
        self._select_box.grid(row=0, column=0, sticky="nsew", padx=10, pady=10, rowspan=2)
        
        self._text_frame = ctk.CTkFrame(self)
        self._text_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=10)
        self._text_frame.bind('<Button-1>', self.on_click)
        
        self._text_frame.grid_columnconfigure(0, weight=0)
        self._text_frame.grid_columnconfigure(1, weight=1)
        
        self._video_path_text = ctk.CTkLabel(self._text_frame, text='Video Path:', text_color=('black','white'), anchor='w', font=('Arial', 15))
        self._video_path_text.grid(row=0, column=0, sticky="ne", padx=5)
        self._video_path_text.bind('<Button-1>', self.on_click)
        
        self._video_path_label = ctk.CTkLabel(self._text_frame, textvariable=self._video_path, text_color=('black','white'), anchor='e', font=('Arial', 15))
        self._video_path_label.grid(row=0, column=1, sticky="nw", padx=5)
        self._video_path_label.bind('<Button-1>', self.on_click)
        
        self._state_display_text = ctk.CTkLabel(self._text_frame, text='State:', text_color=('black','white'), anchor='w', font=('Arial', 15))
        self._state_display_text.grid(row=1, column=0, sticky="ne", padx=5)
        self._state_display_text.bind('<Button-1>', self.on_click)
        
        self._state_display = ctk.CTkLabel(self._text_frame, text=self._video_prediction['overall_pred'], text_color=('black','white'), anchor='e', font=('Arial', 15))
        self._state_display.grid(row=1, column=1, sticky="nw", padx=5)
        self._state_display.bind('<Button-1>', self.on_click)
        
        self._progress_bar = ctk.CTkProgressBar(self, height=14, fg_color='#262626')
        self._progress_bar.set(0)
        self._progress_bar.grid(row=1, column=1, sticky="ew", padx=5, pady=10)
        self._progress_bar.bind('<Button-1>', self.on_click)
        
        self.update_state()
        
    def on_select(self):
        self.update_selection_callback()
    
    def on_click(self, event):
        self.set_active_callback(self)
        
    def update_state(self, state = None):
        if state is not None and state in ['Unlabelled', 'Correct', 'Incorrect', 'Unsure', 'Predicting']:
            self._video_prediction['overall_pred'] = state
        new_color = self._color_legend[self._video_prediction['overall_pred']]
        self.configure(fg_color=new_color)
        self._select_box.configure(bg_color=new_color)
        self._progress_bar.configure(bg_color=new_color)
        self._state_display.configure(text=self._video_prediction['overall_pred'])
        
    def set_video_path(self, path):
        self._video_path.set(path)
        
    def get_video_path(self):
        return self._video_path.get()
    
    def set_checkbox_state(self, state):
        if state == 1:
            self._select_box.select()
        elif state == 0:
            self._select_box.deselect()
    
    def get_checkbox_state(self):
        return self._select_box.get()
    
    def set_visibility(self, state):
        if state:
            self.pack(expand=True, fill="both", padx=10, pady=5)
        else:
            self.pack_forget()
            
    def set_active(self, state):
        self._is_active = state
        
    def get_active(self):
        return self._is_active
            
    def delete(self):
        self.destroy()
        del self
        
    def set_progress(self, progress):
        self._progress_bar.set(progress)
        
    def prediction_callback(self, callback):
        progress = callback.get_progress(self._video_path.get())
        self._progress_bar.set(progress/100)
        if progress == 100:
            self._video_prediction = callback.get_result(self._video_path.get())
            self.update_state()
        else:
            self.after(100, lambda: self.prediction_callback(callback))
            
    def get_item_metadata(self):
        return self._video_prediction
    
    def parse_timeline_colors(self):
        if 'final_preds' not in self._video_prediction:
            return None
        timeline = self._video_prediction['final_preds']
        timeline_colors = []
        for timestamp in timeline:
            if timestamp == 'Unmoving':
                timeline_colors.append('#808080')
            elif timestamp == 'Correct':
                timeline_colors.append('#06D671')
            elif timestamp == 'Incorrect':
                timeline_colors.append('#EF476F')
            elif timestamp == 'Unsure':
                timeline_colors.append('#FFD166')
        return timeline_colors
        
if __name__ == '__main__':
    root = tk.Tk()
    root.title('Prediction Details')
    root.geometry('400x120')
    item = SelectorItem(root, set_active_callback=lambda x: print(x), update_selection_callback=lambda: print('update'))
    item.set_video_path('C:\\Users\\User\\Desktop\\test.mp4')
    item.update_state('Incorrect')
    item.set_progress(0.5)
    item.pack(expand=True, fill='both')
    root.mainloop()
    
        
    