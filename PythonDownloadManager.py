import customtkinter as ctk
from pytube import Playlist, YouTube
import os

class DownloaderApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("YouTube Playlist Downloader")
        self.geometry("500x450")
        self.resizable(False, False)

        self.playlist_link = ctk.StringVar()
        self.quality = ctk.StringVar(value="720p")
        self.format = ctk.StringVar(value="mp4")

        self.quality_options = ["144p", "240p", "360p", "480p", "720p", "1080p", "1440p", "2160p", "4320p"]
        self.available_qualities = []

        self.dark_mode = ctk.BooleanVar(value=True)

        self.create_widgets()
        self.set_theme()

    def create_widgets(self):
        ctk.CTkLabel(self, text="YouTube Playlist Downloader", font=("Helvetica", 24, "bold")).pack(pady=20)

        link_frame = ctk.CTkFrame(self)
        link_frame.pack(pady=10, padx=20, fill="x")
        link_label = ctk.CTkLabel(link_frame, text="Playlist Link:")
        link_label.pack(side="left", padx=10)
        link_entry = ctk.CTkEntry(link_frame, textvariable=self.playlist_link)
        link_entry.pack(side="right", padx=10, expand=True, fill="x")

        options_frame = ctk.CTkFrame(self)
        options_frame.pack(pady=10, padx=20, fill="x")

        quality_label = ctk.CTkLabel(options_frame, text="Video Quality:")
        quality_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.quality_optionmenu = ctk.CTkOptionMenu(options_frame, values=self.quality_options, variable=self.quality, state="disabled")
        self.quality_optionmenu.grid(row=0, column=1, padx=10, pady=5)

        format_label = ctk.CTkLabel(options_frame, text="Format:")
        format_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        format_optionmenu = ctk.CTkOptionMenu(options_frame, values=["mp3", "mp4"], variable=self.format)
        format_optionmenu.grid(row=1, column=1, padx=10, pady=5)

        button_frame = ctk.CTkFrame(self)
        button_frame.pack(pady=20)
        check_button = ctk.CTkButton(button_frame, text="Check Playlist", command=self.check_playlist)
        check_button.pack(side="left", padx=10)
        self.download_button = ctk.CTkButton(button_frame, text="Download", command=self.download_videos, state="disabled")
        self.download_button.pack(side="right", padx=10)

        theme_switch = ctk.CTkSwitch(self, text="Dark Mode", variable=self.dark_mode, command=self.set_theme)
        theme_switch.pack(pady=10)

    def set_theme(self):
        if self.dark_mode.get():
            ctk.set_appearance_mode("dark")
        else:
            ctk.set_appearance_mode("light")

    def check_playlist(self):
        playlist_url = self.playlist_link.get()
        if playlist_url:
            playlist = Playlist(playlist_url)
            self.available_qualities = self.get_available_qualities(playlist)
            self.quality_optionmenu.configure(values=self.available_qualities, state="normal")
            self.quality.set(self.available_qualities[0])
            self.download_button.configure(state="normal")

    def get_available_qualities(self, playlist):
        available_qualities = set(self.quality_options)
        for url in playlist.video_urls:
            video = YouTube(url)
            video_qualities = set([stream.resolution for stream in video.streams.filter(progressive=True, file_extension='mp4')])
            available_qualities &= video_qualities
        return sorted(list(available_qualities), key=self.quality_options.index)

    def download_videos(self):
        playlist_url = self.playlist_link.get()
        quality = self.quality.get()
        format = self.format.get()

        playlist = Playlist(playlist_url)

        for url in playlist.video_urls:
            video = YouTube(url)

            if format == 'mp3':
                stream = video.streams.filter(only_audio=True).first()
                output_file = stream.download(output_path='./downloads', filename_prefix='audio_')
                base, ext = os.path.splitext(output_file)
                new_file = base + '.mp3'
                os.rename(output_file, new_file)
            else:
                stream = video.streams.filter(progressive=True, file_extension='mp4', resolution=quality).first()
                if stream is None:
                    print(f"Skipping video: {video.title} (Requested quality not available)")
                    continue
                stream.download(output_path='./downloads', filename_prefix='video_')

            print(f"Downloaded: {video.title}")

        print("Download completed.")

if __name__ == "__main__":
    app = DownloaderApp()
    app.mainloop()