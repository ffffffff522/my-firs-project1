from flask import Flask, render_template, request, send_file
import yt_dlp
import os
import imageio_ffmpeg as ffmpeg

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    video_url = request.form['videoUrl']
    quality = request.form['quality']
    storage_location = request.form['storageLocation']
    custom_path = request.form.get('customPath')
    download_type = request.form['downloadType']

    if not video_url or not quality or not storage_location or not download_type:
        return "Please enter a video URL, select a quality, choose a storage location, and select a download type.", 400

    if storage_location == 'custom' and custom_path:
        download_path = custom_path
    else:
        download_path = storage_location

    if not os.path.exists(download_path):
        os.makedirs(download_path)

    file_path, error_message = download_media(video_url, quality, download_path, download_type)
    if file_path:
        return send_file(file_path, as_attachment=True)
    else:
        return f"Failed to download media. Error: {error_message}", 500

def download_media(url, quality, download_path, download_type):
    ffmpeg_path = ffmpeg.get_ffmpeg_exe()

    if download_type == 'audio':
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'{download_path}/%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': quality,
            }],
            'ffmpeg_location': ffmpeg_path,
        }
    else:
        ydl_opts = {
            'format': f'bestvideo[height<={quality}]+bestaudio/best',
            'outtmpl': f'{download_path}/%(title)s.%(ext)s',
            'ffmpeg_location': ffmpeg_path,
        }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info_dict)
            if download_type == 'audio':
                file_path = os.path.splitext(file_path)[0] + '.mp3'
            return file_path, None
    except yt_dlp.utils.DownloadError as e:
        error_message = f'Error downloading media: {e}'
        print(error_message)
        return None, error_message
    except Exception as e:
        error_message = f'An unexpected error occurred: {e}'
        print(error_message)
        return None, error_message

if __name__ == '__main__':
    app.run(debug=True)
