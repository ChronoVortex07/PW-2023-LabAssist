import tkinter as tk
import customtkinter as ctk
import os

class SelectorItem(ctk.CTkFrame):
    def __init__(self, *args, video_path = 'video_path', set_active_callback = None, update_selection_callback = None, **kwargs):
        super().__init__(*args, **kwargs)
        
        self._video_prediction = {
            'overall_pred': 'Unlabelled',
            'prediction_timeline': None
        }
        
        self._color_legend = {
            'Unlabelled': ('#1B263B','#778DA9'),
            'Predicting': ('#1B263B','#778DA9'),
            'Correct': '#06D671',
            'Incorrect': '#EF476F',
            'Unsure': '#FFD166',
        }
        
        self._video_path = tk.StringVar(self, value=video_path)
        self._is_active = False
        self.set_active_callback = set_active_callback if set_active_callback != None else lambda x: x
        self.update_selection_callback = update_selection_callback if update_selection_callback != None else lambda: None
        
        self.configure(
            fg_color=('#778DA9','#1B263B'),
            border_color=('#1B263B','#778DA9'),
            border_width=4,
            height=90,
            corner_radius=15,
        )
        self.bind('<Button-1>', self.on_click)
        
        self.grid_columnconfigure((0, 2), weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure((0,1), weight=1)
        
        self._select_box = ctk.CTkCheckBox(self, text=None, width=0, height=0, border_color=('#0D1B2A','#E0E1DD'), fg_color=('#778DA9','#1B263B'), hover=False, command=self.on_select)
        self._select_box.grid(row=0, column=0, sticky="nsew", padx=20, pady=10, rowspan=2)
        
        self._video_path_label = ctk.CTkLabel(self, textvariable=self._video_path, text_color=('#1B263B','#E0E1DD'), anchor='e', font=('Arial', 15))
        self._video_path_label.grid(row=0, column=1, sticky="sew", padx=5)
        self._video_path_label.bind('<Button-1>', self.on_click)
        
        self._state_display = ctk.CTkLabel(self, text=self._video_prediction['overall_pred'], text_color=('#1B263B','#E0E1DD'), anchor='e', font=('Arial', 15, 'bold'))
        self._state_display.grid(row=1, column=1, sticky="new", padx=5)
        self._state_display.bind('<Button-1>', self.on_click)
        
        self._progress_bar = ctk.CTkProgressBar(self, width=24, height=70, progress_color='#E0E1DD', fg_color=('#ACBFD7','#415A77'), orientation='vertical', corner_radius=0)
        self._progress_bar.set(0)
        self._progress_bar.grid(row=0, column=2, sticky="ew", padx=20, pady=20, rowspan=2)
        self._progress_bar.bind('<Button-1>', self.on_click)
        
        self.update_state()
        
    def on_select(self):
        self.update_selection_callback()
    
    def on_click(self, event):
        self.set_active_callback(self)
        
    def update_state(self, state = None):
        if state is not None and state in ['Unlabelled', 'Correct', 'Incorrect', 'Unsure', 'Predicting']:
            self._video_prediction['overall_pred'] = state
        new_color_palette = self.get_color_palette()
        self.configure(
            fg_color=new_color_palette['fg_color'],
            border_color=new_color_palette['border_color'],
        )
        self._select_box.configure(
            border_color=new_color_palette['checkbox_color'],
        )
        self._video_path_label.configure(
            text_color=new_color_palette['video_path_color'],
        )
        self._state_display.configure(
            text_color=new_color_palette['text_color'],
            text=self._video_prediction['overall_pred'],
        )
        self._progress_bar.configure(
            fg_color=new_color_palette['progress_bg_color'],
        )
        
    def set_active(self, state):
        self._is_active = state
        self.update_state()
        
    def get_color_palette(self):
        if self._is_active:
            if self._video_prediction['overall_pred'] in ['Unlabelled', 'Predicting']:
                fg_color = ('#1B263B','#778DA9')
                border_color = ('#1B263B','#778DA9')
                text_color = ('#E0E1DD','#1B263B')
                checkbox_color = ('#E0E1DD','#0D1B2A')
                video_path_color = ('#E0E1DD','#0D1B2A')
            else:
                fg_color = self._color_legend[self._video_prediction['overall_pred']]
                border_color = self._color_legend[self._video_prediction['overall_pred']]
                text_color = '#0D1B2A'
                checkbox_color = '#0D1B2A'
                video_path_color = '#0D1B2A'
            color_palette = {
                'fg_color': fg_color,
                'border_color': border_color,
                'text_color': text_color,
                'progress_bg_color': '#415A77',
                'checkbox_color': checkbox_color,
                'video_path_color': video_path_color,
            }
        else:
            if self._video_prediction['overall_pred'] in ['Unlabelled', 'Predicting']:
                border_color = ('#1B263B','#778DA9')
                text_color = ('#1B263B','#E0E1DD')
                checkbox_color = ('#0D1B2A','#E0E1DD')
            else:
                border_color = self._color_legend[self._video_prediction['overall_pred']]
                text_color = self._color_legend[self._video_prediction['overall_pred']]
                checkbox_color = '#E0E1DD'
            color_palette = {
                'fg_color': ('#778DA9','#1B263B'),
                'border_color': border_color,
                'text_color': text_color,
                'progress_bg_color': ('#ACBFD7','#415A77'),
                'checkbox_color': ('#0D1B2A','#E0E1DD'),
                'video_path_color': ('#1B263B','#E0E1DD')
            }
        return color_palette
        
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
            self.pack(expand=False, fill='x', padx=10, pady=5)
        else:
            self.pack_forget()
            
    def get_active(self):
        return self._is_active
            
    def delete(self):
        self.destroy()
        del self
        
    def set_progress(self, progress):
        self._progress_bar.set(progress)
        
    def prediction_callback(self, callback):
        progress = callback.get_progress(self._video_path.get())
        if progress == 0:
            self._progress_bar.configure(mode='indeterminate')
            self._progress_bar.start()
        else:
            self._progress_bar.stop()
            self._progress_bar.configure(mode='determinate')
            self._progress_bar.set(progress/100)
        if progress == 100:
            self._video_prediction = callback.get_result(self._video_path.get())
            self.update_state()
            self.set_active(self._is_active)
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
    def set_active_callback(item):
        if item.get_active():
            item.set_active(False)
        else:
            item.set_active(True)
    ctk.set_appearance_mode('light')
    root = tk.Tk()
    root.title('Prediction Details')
    root.geometry('300x90')
    item = SelectorItem(root, set_active_callback=set_active_callback, update_selection_callback=lambda: print('update'))
    item.set_video_path('C:\\Users\\User\\Desktop\\test.mp4')
    # item.update_state('Incorrect')
    item.set_active(True)
    item.set_active(False)
    item.set_progress(0.5)
    item.pack(expand=True, fill='both')
    root.mainloop()
    
        
    