import customtkinter as ctk
import json

class SettingsMenu(ctk.CTkToplevel):
    def __init__(self, *args, close_callback=lambda:None, mode_switch_callback=lambda:None, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("Settings")
        self.geometry("800x600")
        self.configure(fg_color=('#778DA9','#0D1B2A'))
        
        self._close_callback = close_callback
        self._mode_switch_callback = mode_switch_callback
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self._inner_frame = ctk.CTkFrame(self, fg_color=('#556E8D','#1B263B'))
        self._inner_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self._inner_frame.grid_columnconfigure(0, weight=1)
        self._inner_frame.grid_rowconfigure(3, weight=1)
        self._inner_frame.grid_rowconfigure((0,1,2,4), weight=0)
        
        self._setting_caption = ctk.CTkLabel(self._inner_frame, text="Settings", font=('Arial', 30, 'bold'), text_color='#FFFFFF', anchor='w')
        self._setting_caption.grid(row=0, column=0, sticky="nsew", padx=54, pady=35)
        
        self._prediction_threads_frame = ctk.CTkFrame(self._inner_frame, fg_color='#415A77')
        self._prediction_threads_frame.grid(row=1, column=0, sticky="nsew", padx=54, pady=10)
        self._prediction_threads_frame.grid_columnconfigure(0, weight=1)
        self._prediction_threads_frame.grid_columnconfigure(1, weight=0)
        self._prediction_threads_frame.grid_rowconfigure((0,1), weight=0)
        
        self._prediction_threads_label = ctk.CTkLabel(self._prediction_threads_frame, text="Number of prediction threads", font=('Arial', 14, 'bold'), text_color='#FFFFFF', anchor='w')
        self._prediction_threads_label.grid(row=0, column=0, sticky="nsew", padx=16, pady=10)
        
        self._prediction_threads_number = ctk.CTkLabel(self._prediction_threads_frame, text="2", font=('Arial', 14, 'bold'), text_color='#FFFFFF', anchor='e')
        self._prediction_threads_number.grid(row=0, column=1, sticky="nsew", padx=16, pady=10)
        
        self._prediction_threads_slider = ctk.CTkSlider(self._prediction_threads_frame, from_=1, to=4, number_of_steps=3, fg_color='#778DA9', progress_color='#1B263B', button_color='#1B263B', corner_radius=0, height=20, command=self.update_threads_number)
        self._prediction_threads_slider.grid(row=1, column=0, sticky="nsew", padx=10, pady=10, columnspan=2)
        
        self._appearance_mode_frame = ctk.CTkFrame(self._inner_frame, fg_color='#415A77')
        self._appearance_mode_frame.grid(row=2, column=0, sticky="nsew", padx=54, pady=10)
        self._appearance_mode_frame.grid_columnconfigure(0, weight=1)
        self._appearance_mode_frame.grid_columnconfigure(1, weight=9)
        
        self._appearance_mode_label = ctk.CTkLabel(self._appearance_mode_frame, text="Appearance mode", font=('Arial', 14, 'bold'), text_color='#FFFFFF', anchor='w')
        self._appearance_mode_label.grid(row=0, column=0, sticky="nsew", padx=16, pady=10)
        
        self._appearance_mode_switch = ctk.CTkSegmentedButton(self._appearance_mode_frame, fg_color='#778DA9', selected_color='#556E8D', unselected_color='#778DA9', selected_hover_color='#1B263B', unselected_hover_color='#1B263B',font=('Arial', 14, 'bold'), values=['Light', 'System', 'Dark'], command=self.update_appearance_mode)
        self._appearance_mode_switch.grid(row=0, column=1, sticky="nsew", padx=16, pady=10)
        
        self._button_frame = ctk.CTkFrame(self._inner_frame, fg_color=('#556E8D','#1B263B'))
        self._button_frame.grid(row=4, column=0, sticky="nsew", padx=44, pady=35)
        self._button_frame.grid_columnconfigure(0, weight=1)
        
        self._cancel_button = ctk.CTkButton(self._button_frame, text="Cancel", font=('Arial', 14, 'bold'), fg_color=('#778DA9','#415A77'), hover_color=('#537A97','#364B63'), width=70, height=30, command=self.close)
        self._cancel_button.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        self._save_button = ctk.CTkButton(self._button_frame, text="Save", font=('Arial', 14, 'bold'), fg_color=('#778DA9','#415A77'), hover_color=('#537A97','#364B63'), width=70, height=30, command=self.save_values)
        self._save_button.grid(row=0, column=2, sticky="nsew", padx=10, pady=10)
        
        self.load_values()
        self.attributes("-topmost", True)
        
    def update_threads_number(self, event=None):
        self._prediction_threads_number.configure(text=int(self._prediction_threads_slider.get()))
        
    def update_appearance_mode(self, event=None):
        ctk.set_appearance_mode(self._appearance_mode_switch.get().lower())
        self._mode_switch_callback()
        
    def load_values(self):
        with open('settings.json', 'r') as f:
            self._settings = json.load(f)
        self._prediction_threads_slider.set(self._settings['num_workers'])
        self._appearance_mode_switch.set(self._settings['appearance_mode'])
        self.update_appearance_mode()
        self.update_threads_number()
        
    def save_values(self, event=None):
        with open('settings.json', 'w') as f:
            json.dump({
                'num_workers': int(self._prediction_threads_slider.get()),
                'appearance_mode': self._appearance_mode_switch.get()
            }, f, indent=4)
        self.close()
            
    def close(self, event=None):
        self._close_callback()
        self.destroy()
        
if __name__ == "__main__":
    root = SettingsMenu()
    root.mainloop()