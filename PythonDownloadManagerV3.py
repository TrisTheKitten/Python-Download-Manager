import customtkinter as ctk
import os
from tkinter import filedialog, messagebox
import threading
import re
import time
import webbrowser
import yt_dlp
import subprocess

class DownloaderApp(ctk.CTk):
    def __init__(self):
            super().__init__()
            self.title("YouTube Downloader")
            self.geometry("500x450")
            self.resizable(False, False)

            self.download_type_var = ctk.StringVar(value="single")
            self.playlist_link = ctk.StringVar()
            self.quality = ctk.StringVar(value="720p")
            self.format = ctk.StringVar(value="mp4")
            self.output_directory = ctk.StringVar(value="./downloads")

            self.quality_options = ["144p", "240p", "360p", "480p", "720p", "1080p", "1440p", "2160p"]

            self.dark_mode = ctk.BooleanVar(value=True)
            self.download_progress = ctk.DoubleVar()
            self.download_status = ctk.StringVar()
            self.download_paused = False
            self.progress_label_text = ctk.StringVar()
            self.current_downloading_number = ctk.StringVar()
            self.downloading_percentage = ctk.StringVar()
            self.remaining_number = ctk.StringVar()
            

            self.create_widgets()
            self.toggle_appearance_mode()

    def create_widgets(self):
        title_label = ctk.CTkLabel(self, text="YouTube Downloader", font=("San-Serif", 24, "bold"))
        title_label.grid(row=0, column=0, padx=20, pady=20, sticky="w")

        theme_switch = ctk.CTkSwitch(self, text="Dark Mode", variable=self.dark_mode, command=self.toggle_appearance_mode, fg_color="gray", font=ctk.CTkFont(family="San-Serif", size=14, weight="bold"))
        theme_switch.grid(row=0, column=1, padx=20, pady=20, sticky="e")
        
        link_frame = ctk.CTkFrame(self)
        link_frame.grid(row=1, columnspan=2, pady=10, padx=20, sticky="ew")

        download_type_var = ctk.StringVar(value="playlist")
        playlist_radio = ctk.CTkRadioButton(link_frame, text="Playlist", variable=self.download_type_var, value="playlist", fg_color="#16A4FA")
        playlist_radio.pack(side="left", padx=5)
        single_video_radio = ctk.CTkRadioButton(link_frame, text="Single Video", variable=self.download_type_var, value="single", fg_color="#16A4FA")
        single_video_radio.pack(side="left", padx=5)

        link_label = ctk.CTkLabel(link_frame, text="Link:")
        link_label.pack(side="left", padx=10)
        link_entry = ctk.CTkEntry(link_frame, textvariable=self.playlist_link)
        link_entry.pack(side="right", padx=10, expand=True, fill="x")

        directory_frame = ctk.CTkFrame(self)
        directory_frame.grid(row=2, columnspan=2, pady=10, padx=20, sticky="ew")
        directory_label = ctk.CTkLabel(directory_frame, text="Output Directory:")
        directory_label.pack(side="left", padx=10)
        directory_entry = ctk.CTkEntry(directory_frame, textvariable=self.output_directory)
        directory_entry.pack(side="left", padx=10, expand=True, fill="x")
        browse_button = ctk.CTkButton(directory_frame, text="Browse", command=self.browse_directory, font=ctk.CTkFont(family="San-Serif", size=14, weight="bold"), fg_color="#16A4FA")
        browse_button.pack(side="right", padx=10)

        options_frame = ctk.CTkFrame(self)
        options_frame.grid(row=3, columnspan=2, pady=10, padx=20, sticky="ew")

        quality_label = ctk.CTkLabel(options_frame, text="Video Quality:")
        quality_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.quality_optionmenu = ctk.CTkOptionMenu(options_frame, values=self.quality_options, variable=self.quality, font=ctk.CTkFont(family="San-Serif", size=14, weight="bold"), fg_color="#16A4FA")
        self.quality_optionmenu.grid(row=0, column=1, padx=10, pady=5)

        format_label = ctk.CTkLabel(options_frame, text="Format:")
        format_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        format_optionmenu = ctk.CTkOptionMenu(options_frame, values=["mp3", "mp4"], variable=self.format, font=ctk.CTkFont(family="San-Serif", size=14, weight="bold"), fg_color="#16A4FA")
        format_optionmenu.grid(row=1, column=1, padx=10, pady=5)
        
        self.updates_button = ctk.CTkButton(self, text="Updates", command=self.open_github_releases, font=ctk.CTkFont(family="San-Serif", size=14, weight="bold"), fg_color="#16A4FA")
        self.updates_button.grid(row=3, column=1, padx=10, pady=(0, 10), sticky="w")
        
        progress_frame = ctk.CTkFrame(self)
        progress_frame.grid(row=4, columnspan=2, pady=10, padx=20, sticky="ew")

        progress_info_frame = ctk.CTkFrame(progress_frame)
        progress_info_frame.pack(fill="x", pady=(0, 10))

        current_downloading_label = ctk.CTkLabel(progress_info_frame, textvariable=self.current_downloading_number)
        current_downloading_label.pack(side="left", padx=(0, 10))

        downloading_percentage_label = ctk.CTkLabel(progress_info_frame, textvariable=self.downloading_percentage)
        downloading_percentage_label.pack(side="left", padx=(0, 10))

        remaining_number_label = ctk.CTkLabel(progress_info_frame, textvariable=self.remaining_number)
        remaining_number_label.pack(side="right")

        self.progress_bar = ctk.CTkProgressBar(progress_frame, variable=self.download_progress)
        self.progress_bar.set(0)  # Set initial progress to 0
        self.progress_bar.pack(fill="x", pady=(0, 10))
        
        self.status_label = ctk.CTkLabel(progress_frame, textvariable=self.download_status)
        self.status_label.pack()
        
        self.download_button = ctk.CTkButton(self, text="Download", font=ctk.CTkFont(family="San-Serif", size=16, weight="bold"), command=self.download_videos, fg_color="#ac5434", hover_color="#16A4FA")
        self.download_button.grid(row=5, column=1, padx=10, pady=10, sticky="w", columnspan=3)

        self.stop_button = ctk.CTkButton(self, text="Stop", font=ctk.CTkFont(family="San-Serif", size=16, weight="bold"), command=self.toggle_download, fg_color="#edeff0", hover_color="#ac5434", state="disabled")
        self.stop_button.grid(row=5, column=1, padx=10, pady=10, sticky="e")

        self.download_button.grid(row=5, column=0, padx=10, pady=10, sticky="w")

        self.version_label = ctk.CTkLabel(self, text="Python Youtube Downloader V3", font=ctk.CTkFont(family="San-Serif", size=12, weight="bold"))
        self.version_label.grid(row=6, column=0, padx=10, pady=(0, 10), sticky="w")
        self.developer_label = ctk.CTkLabel(self, text="Developed By Tris", font=ctk.CTkFont(family="San-Serif", size=12, weight="bold"))
        self.developer_label.grid(row=6, column=1, padx=10, pady=(0, 10), sticky="e")

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        
        ctk.set_appearance_mode("dark")

    def toggle_appearance_mode(self):
        ctk.set_appearance_mode("dark" if self.dark_mode.get() else "light")

    def browse_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.output_directory.set(directory)

    def open_github_releases(self):
        webbrowser.open("https://github.com/TrisTheKitten/Python-Download-Manager/releases")

    def is_valid_url(self, url):
        patterns = {
            "video": [
                r"^https?://(?:www\.)?youtube\.com/watch\?v=.+",
                r"^https?://(?:www\.)?youtube\.com/shorts/.+",
                r"^https?://youtu\.be/.+"  
            ],
            "playlist": [r"^https?://(?:www\.)?youtube\.com/playlist\?list=.+"]
        }
        download_type = self.download_type_var.get()
        if download_type == "single":
            return any(re.match(pattern, url) for pattern in patterns["video"])
        elif download_type == "playlist":
            return any(re.match(pattern, url) for pattern in patterns["playlist"])
        else:
            return False

    def download_videos(self):
        url = self.playlist_link.get()
        output_path = self.output_directory.get()

        if not url:
            messagebox.showerror("Empty Link", "Please provide a YouTube link.")
            return

        if not self.is_valid_url(url):
            messagebox.showerror("Invalid Link", f"Please provide a valid YouTube {'playlist' if self.download_type_var.get() == 'playlist' else 'video'} link.")
            return

        if not os.path.isdir(output_path):
            messagebox.showerror("Invalid Directory", "The provided output directory is invalid.")
            return

        self.stop_button.configure(state="normal")
        threading.Thread(target=self.download_videos_thread, daemon=True).start()

    def toggle_download(self):
        self.download_paused = not self.download_paused
        self.stop_button.configure(text="Resume" if self.download_paused else "Stop")

    @staticmethod
    def sanitize_filename(filename):
        return re.sub(r'[<>:"/\\|?*]', '', filename).replace(' ', '_')

    def download_videos_thread(self):
        try:
            print("Download thread started")  
            url = self.playlist_link.get()
            format = self.format.get()
            quality = self.quality.get()
            output_path = self.output_directory.get()

            ydl_opts = {
                'format': f'bestvideo[height<={quality[:-1]}]+bestaudio/best[height<={quality[:-1]}]',
                'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
                'progress_hooks': [self.ydl_progress_hook],
                'concurrent_fragment_downloads': 10,
                'throttledratelimit': 100000,
            }

            if format == 'mp3':
                ydl_opts.update({
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                })

            self.download_status.set("Download started.")
            self.download_progress.set(0)  

            print("Starting yt-dlp download")  
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            self.download_status.set("Download completed.")
            self.download_progress.set(1)
            messagebox.showinfo("Download Complete", "All videos have been downloaded successfully.")
        except Exception as e:
            print(f"Error in download thread: {str(e)}")  
            print(traceback.format_exc())  
            self.download_status.set("Download failed.")
            messagebox.showerror("Download Error", f"An error occurred: {str(e)}")
        finally:
            self.stop_button.configure(state="disabled", text="Stop")

    def ydl_progress_hook(self, d):
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', '0%').strip()
            speed = d.get('_speed_str', 'N/A')
            eta = d.get('_eta_str', 'N/A')
            filename = d.get('filename', '').split('/')[-1]

            max_filename_length = 20
            if len(filename) > max_filename_length:
                filename = filename[:max_filename_length-3] + '...'

            progress_text = f"{percent} | {filename} | {eta}"
            
            self.downloading_percentage.set(percent)
            self.progress_label_text.set(progress_text)
            
            try:
                progress = float(percent.rstrip('%'))
                self.download_progress.set(progress / 100)
            except ValueError:
                print(f"Could not convert percentage: {percent}")
            
            self.current_downloading_number.set(f"Speed: {speed}")
            self.remaining_number.set(f"ETA: {eta}")

        elif d['status'] == 'finished':
            self.download_status.set("Download finished, now processing...")
            self.download_progress.set(1)
            self.progress_label_text.set("100% | Processing | Completed")

if __name__ == "__main__":
    app = DownloaderApp()
    app.mainloop()