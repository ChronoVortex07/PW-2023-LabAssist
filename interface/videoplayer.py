import tkinter as tk
import customtkinter as ctk

                
import ffmpeg
import av
import time
import threading
import logging
import tkinter as tk
from PIL import ImageTk, Image, ImageOps
from typing import Tuple, Dict

logging.getLogger('libav').setLevel(logging.ERROR)  # removes warning: deprecated pixel format used

class video_player(ctk.CTkFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.video_path = None
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        
        self.video_display = self.TkinterVideo(self, keep_aspect=True, bg="black")
        self.video_display.grid(row=0, column=0, sticky="nsew")
        
        self.progress_bar_frame = ctk.CTkFrame(self, height=30, corner_radius=0)
        self.progress_bar_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=7)
        self.progress_bar = self.CustomProgressBar(self.progress_bar_frame, height=15)
        self.progress_bar.pack(fill="both", expand=True)
        self.progress_bar.update_section_colors(['gray'])
        
        self.video_display.bind("<<Duration>>", self._update_duration)
        self.video_display.bind("<<SecondChanged>>", self._seek_progress_bar)
        
        self.progress_bar.bind('<<seek_video>>', self._seek_video)
        
    def load(self, path):
        self.video_path = path
        self.video_display.load(path)
        self.progress_bar.seek(0)
        self.video_display.play()
        
    def stop(self):
        self.video_display.stop()
        
    def _update_duration(self, event):
        self.duration = self.video_display.video_info()["duration"]
        
    def _seek_video(self, event):
        # update the current frame of the video based on value of progress bar
        self.video_display.seek(int(self.duration * self.progress_bar.slider_value / 100)+1)
        if self.video_display._stop:
            self.video_display.play()
        
    def _seek_progress_bar(self, event):
        self.progress_bar.seek(self.video_display.current_duration() / self.duration * 100)

        
    class CustomProgressBar(ctk.CTkCanvas):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.slider_width = 5
            self.bind("<B1-Motion>", self._update_slider_position)
            self.bind("<Button-1>", self._update_slider_position)
            self.bind("<Configure>", self.repaint_canvas)
            
            self.configure(relief="flat", highlightthickness=0, bd=0, bg="black")
            
            self.slider_value = 0
            self.section_colors = []
            
        def repaint_canvas(self, event):
            self.delete("all")
            if self.section_colors:
                section_width = self.winfo_width() / len(self.section_colors)
                for i, color in enumerate(self.section_colors):
                    section_start = i * section_width
                    section_end = (i + 1) * section_width
                    self.create_rectangle(section_start, 0, section_end, self.winfo_height(), fill=color)
            self.slider_handle = self.create_rectangle(0, 0, self.slider_width, self.winfo_height(), fill="black")
            self.coords(self.slider_handle, self.slider_value / 100 * (self.winfo_width() - self.slider_width), 0, self.slider_value / 100 * (self.winfo_width() - self.slider_width) + self.slider_width, self.winfo_height())
            
        def _update_slider_position(self, event):
            x = event.x - self.slider_width / 2  # Adjust x position to center the slider handle
            x = max(0, min(x, self.winfo_width() - self.slider_width))  # Restrict the slider within the canvas bounds
            self.coords(self.slider_handle, x, 0, x + self.slider_width, self.winfo_height())  # Move the slider handle
            self._update_slider_value(x)
            self.event_generate('<<seek_video>>')

        def _update_slider_value(self, x):
            normalized_value = x / (self.winfo_width() - self.slider_width)  # Calculate the normalized value between 0 and 1
            self.slider_value = normalized_value * 100  # Map the normalized value to the desired range
            
        def update_section_colors(self, section_colors):
            print(section_colors)
            if section_colors is not None:
                self.section_colors = section_colors
            else:
                self.section_colors = ['gray']
            self.repaint_canvas(None)
            
        def seek(self, value):
            self.slider_value = value
            self.repaint_canvas(None)
            
    class TkinterVideo(tk.Label):
        def __init__(self, master, scaled: bool = True, consistant_frame_rate: bool = True, keep_aspect: bool = False, *args, **kwargs):
            super().__init__(master, *args, **kwargs)

            self.path = ""
            self._load_thread = None

            self._paused = True
            self._stop = True
            self.rotation = None

            self.consistant_frame_rate = consistant_frame_rate # tries to keep the frame rate consistant by skipping over a few frames

            self._container = None

            self._current_img = None
            self._current_frame_Tk = None
            self._frame_number = 0
            self._time_stamp = 0

            self._current_frame_size = (0, 0)

            self._seek = False
            self._seek_sec = 0

            self._video_info = {
                "duration": 0, # duration of the video
                "framerate": 0, # frame rate of the video
                "framesize": (0, 0) # tuple containing frame height and width of the video

            }   

            self.set_scaled(scaled)
            self._keep_aspect_ratio = keep_aspect
            self._resampling_method: int = Image.Resampling.NEAREST


            self.bind("<<Destroy>>", self.stop)
            self.bind("<<FrameGenerated>>", self._display_frame)
            self.bind("<Button-1>", self._play_pause)
        
        def keep_aspect(self, keep_aspect: bool):
            """ keeps the aspect ratio when resizing the image """
            self._keep_aspect_ratio = keep_aspect

        def set_resampling_method(self, method: int):
            """ sets the resampling method when resizing """
            self._resampling_method = method

        def set_size(self, size: Tuple[int, int], keep_aspect: bool=False):
            """ sets the size of the video """
            self.set_scaled(False, self._keep_aspect_ratio)
            self._current_frame_size = size
            self._keep_aspect_ratio = keep_aspect

        def _resize_event(self, event):

            self._current_frame_size = event.width, event.height

            if self._paused and self._current_img and self.scaled:
                if self._keep_aspect_ratio:
                    proxy_img = ImageOps.contain(self._current_img.copy(), self._current_frame_size)

                else:
                    proxy_img = self._current_img.copy().resize(self._current_frame_size)
                
                self._current_imgtk = ImageTk.PhotoImage(proxy_img)
                self.config(image=self._current_imgtk)


        def set_scaled(self, scaled: bool, keep_aspect: bool = False):
            self.scaled = scaled
            self._keep_aspect_ratio = keep_aspect
            
            if scaled:
                self.bind("<Configure>", self._resize_event)

            else:
                self.unbind("<Configure>")
                self._current_frame_size = self.video_info()["framesize"]

        def _play_pause(self, event):
            if self._paused:
                self.play()
            else:
                self.pause()

        def _set_frame_size(self, event=None):
            """ sets frame size to avoid unexpected resizing """

            self._video_info["framesize"] = (self._container.streams.video[0].width, self._container.streams.video[0].height)

            self.current_imgtk = ImageTk.PhotoImage(Image.new("RGBA", self._video_info["framesize"], (255, 0, 0, 0)))
            self.config(width=150, height=100, image=self.current_imgtk)

        def _load(self, path):
            """ load's file from a thread """

            current_thread = threading.current_thread()

            with av.open(path) as self._container:

                self._container.streams.video[0].thread_type = "AUTO"
                
                self._container.fast_seek = True
                self._container.discard_corrupt = True

                try:
                    self.rotation = ffmpeg.probe(path, cmd="ffmpeg/bin/ffprobe.exe")['streams'][0]['side_data_list'][0]['rotation']
                except:
                    self.rotation = None

                stream = self._container.streams.video[0]

                try:
                    self._video_info["framerate"] = int(stream.average_rate)

                except TypeError:
                    raise TypeError("Not a video file")
                
                try:

                    self._video_info["duration"] = float(stream.duration * stream.time_base)
                    self.event_generate("<<Duration>>")  # duration has been found

                except (TypeError, tk.TclError):  # the video duration cannot be found, this can happen for mkv files
                    pass

                self._frame_number = 0

                self._set_frame_size()

                self.stream_base = stream.time_base

                try:
                    self.event_generate("<<Loaded>>") # generated when the video file is opened
                
                except tk.TclError:
                    pass

                now = time.time_ns() // 1_000_000  # time in milliseconds
                then = now

                time_in_frame = (1/self._video_info["framerate"])*1000 # second it should play each frame


                while self._load_thread == current_thread and not self._stop:
                    if self._seek: # seek to specific second
                        self._container.seek(self._seek_sec*1000000 , whence='time', backward=True, any_frame=False) # the seek time is given in av.time_base, the multiplication is to correct the frame
                        self._seek = False
                        self._frame_number = self._video_info["framerate"] * self._seek_sec

                        self._seek_sec = 0

                    if self._paused:
                        time.sleep(0.0001) # to allow other threads to function better when its paused
                        continue

                    now = time.time_ns() // 1_000_000  # time in milliseconds
                    delta = now - then  # time difference between current frame and previous frame
                    then = now
            
                    # print("Frame: ", frame.time, frame.index, self._video_info["framerate"])
                    try:
                        frame = next(self._container.decode(video=0))

                        self._time_stamp = float(frame.pts * stream.time_base)

                        self._current_img = frame.to_image()

                        self._frame_number += 1
                
                        self.event_generate("<<FrameGenerated>>")

                        if self._frame_number % self._video_info["framerate"] == 0:
                            self.event_generate("<<SecondChanged>>")

                        if self.consistant_frame_rate:
                            time.sleep(max((time_in_frame - delta)/1000, 0))

                        # time.sleep(abs((1 / self._video_info["framerate"]) - (delta / 1000)))

                    except (StopIteration, av.error.EOFError, tk.TclError):
                        break

            self._frame_number = 0
            self._paused = True
            self._load_thread = None

            self._container = None
            
            try:
                self.event_generate("<<Ended>>")  # this is generated when the video ends

            except tk.TclError:
                pass

        def load(self, path: str):
            """ loads the file from the given path """
            self.stop()
            self.path = path

        def stop(self):
            """ stops reading the file """
            self._paused = True
            self._stop = True

        def pause(self):
            """ pauses the video file """
            self._paused = True

        def play(self):
            """ plays the video file """
            self._paused = False
            self._stop = False

            if not self._load_thread:
                # print("loading new thread...")
                self._load_thread = threading.Thread(target=self._load,  args=(self.path, ), daemon=True)
                self._load_thread.start()

        def is_paused(self):
            """ returns if the video is paused """
            return self._paused

        def video_info(self) -> Dict:
            """ returns dict containing duration, frame_rate, file"""
            return self._video_info

        def metadata(self) -> Dict:
            """ returns metadata if available """
            if self._container:
                return self._container.metadata

            return {}

        def current_frame_number(self) -> int:
            """ return current frame number """
            return self._frame_number

        def current_duration(self) -> float:
            """ returns current playing duration in sec """
            return self._time_stamp
        
        def current_img(self) -> Image:
            """ returns current frame image """
            return self._current_img
        
        def _display_frame(self, event):
            """ displays the frame on the label """
            
                                
            if self.rotation is not None:
                self._current_img = self._current_img.rotate(self.rotation, expand=True)

            if self.scaled or (len(self._current_frame_size) == 2 and all(self._current_frame_size)):

                if self._keep_aspect_ratio:
                    self._current_img = ImageOps.contain(self._current_img, self._current_frame_size, self._resampling_method)

                else:
                    self._current_img =  self._current_img.resize(self._current_frame_size, self._resampling_method)

            else: 
                self._current_frame_size = self.video_info()["framesize"] if all(self.video_info()["framesize"]) else (1, 1)
                
                if self._keep_aspect_ratio:
                    self._current_img = ImageOps.contain(self._current_img, self._current_frame_size, self._resampling_method)

                else:
                    self._current_img =  self._current_img.resize(self._current_frame_size, self._resampling_method)
                    
            self._current_imgtk = ImageTk.PhotoImage(self._current_img)
            
            self.config(image=self._current_imgtk)

        def seek(self, sec: int):
            """ seeks to specific time""" 

            self._seek = True
            self._seek_sec = sec            
            
if __name__ == "__main__":
    window = ctk.CTk()
    window.title("Video Playback Slider")
    window.geometry("800x600")

    video_display = video_player(window, fg_color="black")
    video_display.pack(fill="both", expand=True)
    video_display.load('C:/Users/zedon/Documents/GitHub/PW-2023-LabAssist/Zedong_fullTitration_1.mp4')

    window.mainloop()
