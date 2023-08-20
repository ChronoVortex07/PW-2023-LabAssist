import tkinter as tk
import customtkinter as ctk

import logging
import tkinter as tk
from PIL import Image

logging.getLogger('libav').setLevel(logging.ERROR)  # removes warning: deprecated pixel format used

class VideoControls(ctk.CTkFrame):
    def __init__(self, *args, video_display_callback = None, play_pause_callback = None, fast_forward_callback = None, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.configure(fg_color=('#778DA9','#415A77'), corner_radius=0)
        
        self._is_paused = False
        self._play_pause_callback = play_pause_callback if play_pause_callback != None else lambda x: None
        self._fast_forward_callback = fast_forward_callback if fast_forward_callback != None else lambda x: None
        
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(4, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self._fast_backward_image = ctk.CTkImage(Image.open('app/src/light/fast_backwards.png'), Image.open('app/src/dark/fast_backwards.png'), size=(24, 24))
        self._fast_backward_button = ctk.CTkButton(
            self, text=None, image=self._fast_backward_image, command=self.fast_backward,
            fg_color=('#778DA9','#415A77'),
            hover_color=('#537A97','#364B63'),
            corner_radius=0, width=5, height=5
        )
        self._fast_backward_button.grid(row=0, column=0, sticky="ew", padx=5, pady=7)
        
        self._play_image = ctk.CTkImage(Image.open('app/src/light/play.png'), Image.open('app/src/dark/play.png'), size=(22, 22))
        self._pause_image = ctk.CTkImage(Image.open('app/src/light/pause.png'), Image.open('app/src/dark/pause.png'), size=(22, 22))
        self._play_pause_button = ctk.CTkButton(
            self, text=None, image=self._play_image, command=self.play_pause,
            fg_color=('#778DA9','#415A77'),
            hover_color=('#537A97','#364B63'),
            corner_radius=0, width=5, height=5
        )
        self._play_pause_button.grid(row=0, column=1, sticky="ew", padx=5, pady=7)
        
        self._fast_forward_image = ctk.CTkImage(Image.open('app/src/light/fast_forward.png'), Image.open('app/src/dark/fast_forward.png'), size=(24, 24))
        self._fast_forward_button = ctk.CTkButton(
            self, text=None, image=self._fast_forward_image, command=self.fast_forward,
            fg_color=('#778DA9','#415A77'),
            hover_color=('#537A97','#364B63'),
            corner_radius=0, width=5, height=5
        )
        self._fast_forward_button.grid(row=0, column=2, sticky="ew", padx=5, pady=7)
        
        self._time_display = ctk.CTkLabel(self, text='00:00', font=('Arial', 14, 'bold'), anchor='center', text_color=('#1B263B','#FFFFFF'))
        self._time_display.grid(row=0, column=3, sticky="ew", padx=5, pady=7)
        
        self._progress_bar = CustomProgressBar(self, video_display_callback=video_display_callback, height=15)
        self._progress_bar.grid(row=0, column=4, sticky="ew", padx=10, pady=12)
        
        self._progress_bar.update_section_colors(['gray'])
        
    def play_pause(self, event=None, state=None):
        if state is not None:
            self._is_paused = not state
        else:
            self._play_pause_callback(self._is_paused)
            self._is_paused = not self._is_paused
        if self._is_paused:
            self._play_pause_button.configure(image=self._pause_image)
        else:
            self._play_pause_button.configure(image=self._play_image)
            
    def update_time_display(self, time):
        self._time_display.configure(text='{:02d}:{:02d}'.format(int(time/60), int(time%60)))        
        
    def fast_backward(self):
        self._fast_forward_callback(-5)
    
    def fast_forward(self):
        self._fast_forward_callback(5)
        
    def set_video_display_callback(self, video_display_callback):
        self._progress_bar._video_display_callback = video_display_callback
        
    def update_section_colors(self, section_colors):
        self._progress_bar.update_section_colors(section_colors)
        
    def seek(self, value):
        self._progress_bar.seek(value)

class CustomProgressBar(ctk.CTkCanvas):
    def __init__(self, *args, video_display_callback = None, **kwargs):
        super().__init__(*args,**kwargs)
        self._slider_width = 5
        self.bind("<B1-Motion>", self._update_slider_position)
        self.bind("<Button-1>", self._update_slider_position)
        self.bind("<Configure>", self.repaint_canvas)
        
        self.configure(relief="flat", highlightthickness=0, bd=0, bg="black")
        
        self._slider_value = 0
        self._section_colors = []
        self._video_display_callback = video_display_callback if video_display_callback != None else lambda x: None
        
    def repaint_canvas(self, event):
        self.delete("all")
        if self._section_colors:
            section_width = self.winfo_width() / len(self._section_colors)
            for i, color in enumerate(self._section_colors):
                section_start = i * section_width
                section_end = (i + 1) * section_width
                self.create_rectangle(section_start, 0, section_end, self.winfo_height(), fill=color)
        self._slider_handle = self.create_rectangle(0, 0, self._slider_width, self.winfo_height(), fill="black")
        self.coords(self._slider_handle, self._slider_value / 100 * (self.winfo_width() - self._slider_width), 0, self._slider_value / 100 * (self.winfo_width() - self._slider_width) + self._slider_width, self.winfo_height())
        
    def _update_slider_position(self, event):
        x = event.x - self._slider_width / 2  # Adjust x position to center the slider handle
        x = max(0, min(x, self.winfo_width() - self._slider_width))  # Restrict the slider within the canvas bounds
        self.coords(self._slider_handle, x, 0, x + self._slider_width, self.winfo_height())  # Move the slider handle
        self._update_slider_value(x)
        self._video_display_callback(self._slider_value/100)

    def _update_slider_value(self, x):
        normalized_value = x / (self.winfo_width() - self._slider_width)  # Calculate the normalized value between 0 and 1
        self._slider_value = normalized_value * 100  # Map the normalized value to the desired range
        
    def update_section_colors(self, section_colors):
        if section_colors is not None:
            self._section_colors = section_colors
        else:
            self._section_colors = ['gray']
        self.repaint_canvas(None)
        
    def seek(self, value):
        self._slider_value = value*100
        self.repaint_canvas(None)
            
           
            
if __name__ == "__main__":
    def video_display_callback(val):
        pass
    window = ctk.CTk()
    window.title("Video Playback Slider")
    window.geometry("600x40")

    video_controls = VideoControls(window, height=30)
    video_controls.set_video_display_callback(video_display_callback)
    video_controls.pack(expand=True, fill=tk.BOTH)
    video_controls.update_section_colors(['#EF476F','#FFD166','#06D671', '#808080'])
    video_controls.seek(0.5)
    video_controls.update_time_display(999)
    window.mainloop()
