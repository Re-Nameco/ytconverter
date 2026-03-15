import tkinter as tk
from tkinter import ttk, filedialog
import threading
import json
from pathlib import Path
from downloader import Downloader

class ConfigWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.transient(parent)
        self.parent = parent
        self.title("Configuration")
        self.geometry("500x140")

        self.download_path = tk.StringVar(value=str(parent.download_path))
        self.playlist_var = tk.BooleanVar(value=parent.playlist)

        # Download path
        self.path_label = ttk.Label(self, text="Download Path:")
        self.path_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.path_entry = ttk.Entry(self, textvariable=self.download_path, width=50)
        self.path_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        self.browse_button = ttk.Button(self, text="Browse...", command=self.browse_directory)
        self.browse_button.grid(row=0, column=2, padx=10, pady=10)

        # Playlist option
        self.playlist_label = ttk.Label(self, text="Download:")
        self.playlist_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.single_radio = ttk.Radiobutton(self, text="Single Video", variable=self.playlist_var, value=False)
        self.single_radio.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        self.playlist_radio = ttk.Radiobutton(self, text="Entire Playlist", variable=self.playlist_var, value=True)
        self.playlist_radio.grid(row=1, column=1, padx=10, pady=10, sticky="e")

        # Save button
        self.save_button = ttk.Button(self, text="Save", command=self.save_config)
        self.save_button.grid(row=2, column=2, padx=10, pady=20)

        self.grid_columnconfigure(1, weight=1)


    def browse_directory(self):
        path = filedialog.askdirectory(initialdir=self.download_path.get())
        if path:
            self.download_path.set(path)

    def save_config(self):
        self.parent.download_path = Path(self.download_path.get())
        self.parent.playlist = self.playlist_var.get()
        self.parent.save_config()
        self.destroy()

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("YouTube Downloader")
        self.geometry("500x250")

        self.config_file = Path("config.json")
        self.download_path, self.playlist = self.load_config()

        # URL Entry
        self.url_label = ttk.Label(self, text="YouTube URL:")
        self.url_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.url_entry = ttk.Entry(self, width=50)
        self.url_entry.grid(row=0, column=1, columnspan=2, padx=10, pady=10, sticky="ew")

        # Format Selection
        self.format_label = ttk.Label(self, text="Format:")
        self.format_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.format_var = tk.StringVar(value="mp4")
        self.format_menu = ttk.Combobox(self, textvariable=self.format_var, values=["mp4", "mp3"], state="readonly")
        self.format_menu.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        
        # Config Button
        self.config_button = ttk.Button(self, text="Config", command=self.open_config)
        self.config_button.grid(row=1, column=2, padx=10, pady=10, sticky="e")

        # Download Button
        self.download_button = ttk.Button(self, text="Download", command=self.start_download)
        self.download_button.grid(row=2, column=2, padx=10, pady=20, sticky="e")

        # Progress Bar
        self.progress_label = ttk.Label(self, text="Progress:")
        self.progress_label.grid(row=3, column=0, padx=10, pady=10, sticky="w")
        self.progress_bar = ttk.Progressbar(self, orient="horizontal", length=300, mode="determinate")
        self.progress_bar.grid(row=3, column=1, columnspan=2, padx=10, pady=10, sticky="ew")

        # Status Label
        self.status_label = ttk.Label(self, text="")
        self.status_label.grid(row=4, column=0, columnspan=3, padx=10, pady=10, sticky="w")

        self.grid_columnconfigure(1, weight=1)

        self.downloader = Downloader(progress_callback=self.update_progress, status_callback=self.update_status)

    def load_config(self):
        if self.config_file.exists():
            with open(self.config_file, "r") as f:
                try:
                    config = json.load(f)
                    path = Path(config.get("download_path", str(Path.home() / "Downloads")))
                    playlist = config.get("playlist", False)
                    return path, playlist
                except (json.JSONDecodeError, KeyError):
                    return Path.home() / "Downloads", False
        return Path.home() / "Downloads", False

    def save_config(self):
        config = {
            "download_path": str(self.download_path),
            "playlist": self.playlist
        }
        with open(self.config_file, "w") as f:
            json.dump(config, f)
        self.status_label.config(text=f"Configuration saved.")

    def open_config(self):
        ConfigWindow(self)

    def start_download(self):
        url = self.url_entry.get()
        if not url:
            self.update_status("Please enter a YouTube URL.")
            return

        audio_only = self.format_var.get() == "mp3"
        
        self.download_button.config(state="disabled")
        self.url_entry.config(state="disabled")
        self.format_menu.config(state="disabled")
        self.config_button.config(state="disabled")
        self.progress_bar["value"] = 0

        download_thread = threading.Thread(target=self.downloader.download, args=(url, self.download_path, audio_only, self.playlist))
        download_thread.start()

    def update_progress(self, percentage):
        self.progress_bar["value"] = percentage
        self.update_idletasks()

    def update_status(self, message):
        self.status_label.config(text=message)
        if "finished" in message or "Error" in message:
            self.download_button.config(state="normal")
            self.url_entry.config(state="normal")
            self.format_menu.config(state="normal")
            self.config_button.config(state="normal")

if __name__ == "__main__":
    app = App()
    app.mainloop()
