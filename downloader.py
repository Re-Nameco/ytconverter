import yt_dlp

class Downloader:
    def __init__(self, progress_callback=None, status_callback=None):
        self.progress_callback = progress_callback
        self.status_callback = status_callback

    def download(self, url, download_path, audio_only=False, playlist=False):
        try:
            self.status_callback("Starting download...")
            
            outtmpl = f'{download_path}/%(title)s.%(ext)s'
            if playlist:
                outtmpl = f'{download_path}/%(playlist_index)s - %(title)s.%(ext)s'

            ydl_opts = {
                'outtmpl': outtmpl,
                'progress_hooks': [self.progress_hook],
                'verbose': True,
                'noplaylist': not playlist,
            }

            if audio_only:
                ydl_opts['format'] = 'bestaudio/best'
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]
            else:
                ydl_opts['format'] = 'bv*+ba[ext=m4a]/b'
                ydl_opts['merge_output_format'] = 'mp4'


            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            self.status_callback("Download finished successfully!")

        except yt_dlp.utils.DownloadError as e:
            self.status_callback(f"Download Error: {e}")
        except Exception as e:
            self.status_callback(f"An unexpected error occurred: {e}")


    def progress_hook(self, d):
        if d['status'] == 'downloading':
            total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate')
            if total_bytes:
                downloaded_bytes = d.get('downloaded_bytes')
                percentage = (downloaded_bytes / total_bytes) * 100
                self.progress_callback(percentage)
        elif d['status'] == 'finished':
            self.progress_callback(100)

