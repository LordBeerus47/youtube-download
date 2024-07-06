import os
from flask import Flask, request, render_template, redirect, url_for, flash, send_file, send_from_directory
from pytube import YouTube
import moviepy.editor as mp

app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form['url']
    quality = request.form['quality'] 
    file_format = request.form['format']
    download_option = request.form['download_option']

    try:
        yt = YouTube(url)
        if file_format == 'mp4':
            stream = yt.streams.filter(file_extension='mp4').filter(res=quality).filter(progressive=True).first()
        else:
            stream = yt.streams.filter(only_audio=True).first()

        if not stream:
            flash('Requested quality or format not available.', 'danger')
            return redirect(url_for('index'))

        
        if file_format == 'mp4':
            filename = f"{yt.title} [{quality}].mp4"
            stream.download('downloads', filename=filename, max_retries=5)
            flash(f'Video downloaded successfully in {quality}.', 'success')
        else:
            audio_path = stream.download('downloads')
            base, ext = os.path.splitext(audio_path)
            mp4_path = base + '.mp4'
            os.rename(audio_path, mp4_path)

            mp3_path = base + '.mp3'
            clip = mp.AudioFileClip(mp4_path)
            clip.write_audiofile(mp3_path)
            os.remove(mp4_path)

            flash('Audio downloaded successfully as MP3.', 'success')
        if download_option == 'server':
            return redirect(url_for('overview'))
        else:
            if file_format == 'mp4':
                return send_file(f"downloads/{filename}", as_attachment=True)
            return send_file(mp3_path, as_attachment=True)

    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'danger')
        return redirect(url_for('index'))

def get_folder_size(folder):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(folder):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size

@app.route('/overview')
def overview():
    files = os.listdir('downloads')
    mp4_files = [f for f in files if f.endswith('.mp4')]
    mp3_files = [f for f in files if f.endswith('.mp3')]
    used_space = get_folder_size('downloads') / (1024 * 1024 * 1024)  # Convert bytes to gigabytes
    total_space = 3 #in Gb
    used_percentage = (used_space / total_space) * 100
    return render_template('overview.html', mp4_files=mp4_files, mp3_files=mp3_files, used_space=used_space, total_space=total_space, used_percentage=used_percentage)

@app.route('/remove_video/<title>', methods=['GET'])
def remove_video(title):
    try:
        files = os.listdir('downloads')
        files_to_remove = [f for f in files if title in f]
        for file in files_to_remove:
            os.remove(os.path.join('downloads', file))
        flash(f'Files for {title} removed successfully.', 'success')
    except Exception as e:
        flash(f'Error removing files for {title}: {str(e)}', 'danger')
    return redirect(url_for('overview'))

@app.route('/download_again/<title>', methods=['GET'])
def download_again(title):
    files = os.listdir('downloads')
    file_to_download = next((f for f in files if title in f), None)
    if file_to_download:
        return send_file(os.path.join('downloads', file_to_download), as_attachment=True)
    else:
        flash(f'No file found for {title}.', 'danger')
        return redirect(url_for('overview'))

@app.route('/view_video/<title>', methods=['GET'])
def view_video(title):
    files = os.listdir('downloads')
    file_to_view = next((f for f in files if title in f), None)
    if file_to_view:
        return render_template('view_video.html', video_file=file_to_view)
    else:
        flash(f'No file found for {title}.', 'danger')
        return redirect(url_for('overview'))

@app.route('/downloads/<path:filename>')
def download_file(filename):
    return send_from_directory('downloads', filename)


if __name__ == '__main__':
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
    app.run(debug=True)
