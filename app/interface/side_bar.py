import os
from PIL import Image
import customtkinter as ctk

class SideBar(ctk.CTkFrame):
    def __init__(self, *args, upload_callback=lambda x:None, export_callback=lambda x:None, settings_callback=lambda x:None, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.configure(fg_color=('#ACBFD7','#778DA9'), width=96, corner_radius=0)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((0,1,2), weight=0)
        self.grid_rowconfigure(3, weight=1)
        
        self._flask_icon = ctk.CTkImage(Image.open('app/src/light/flask.png'), Image.open('app/src/dark/flask.png'), (48, 48))
        self._export_icon = ctk.CTkImage(Image.open('app/src/light/export.png'), Image.open('app/src/dark/export.png'), (32, 32))
        self._import_icon = ctk.CTkImage(Image.open('app/src/light/import.png'), Image.open('app/src/dark/import.png'), (32, 32))
        self._settings_icon = ctk.CTkImage(Image.open('app/src/light/settings.png'), Image.open('app/src/dark/settings.png'), (32, 32))
        
        self._flask_icon_frame = ctk.CTkFrame(self, width=96, height=96, fg_color=('#415A77','#1B263B'), corner_radius=0)
        self._flask_icon_frame.grid(row=0, column=0, sticky="nsew")
        self._flask_icon_frame.grid_columnconfigure(0, weight=1)
        
        self._flask_icon_label = ctk.CTkLabel(self._flask_icon_frame, width=96, height=96, image=self._flask_icon, anchor='center', text=None)
        self._flask_icon_label.grid(row=0, column=0, sticky="nsew")
        
        self._upload_button = ctk.CTkButton(self, text=None, width=32, height=48, fg_color=('#778DA9','#415A77'), corner_radius=8, image=self._import_icon, border_spacing=0, hover_color=('#415A77','#ACBFD7'), command=upload_callback)
        self._upload_button.grid(row=1, column=0, sticky="ns", pady=24)
        
        self._export_button = ctk.CTkButton(self, text=None, width=32, height=48, fg_color=('#778DA9','#415A77'), corner_radius=8, image=self._export_icon, border_spacing=0, hover_color=('#415A77','#ACBFD7'), command=export_callback)
        self._export_button.grid(row=2, column=0, sticky="ns", pady=0)
        
        self._settings_button = ctk.CTkButton(self, text=None, width=32, height=48, fg_color=('#778DA9','#415A77'), corner_radius=8, image=self._settings_icon, border_spacing=0, hover_color=('#415A77','#ACBFD7'), command=settings_callback)
        self._settings_button.grid(row=3, column=0, sticky="s", pady=24)
        
if __name__ == '__main__':
    root = ctk.CTk()
    root.geometry('800x600')
    root.configure(bg='#1B263B')
    
    ctk.set_appearance_mode('light')
    
    side_bar = SideBar(root)
    side_bar.pack(side='left', fill='y')
    
    root.mainloop()