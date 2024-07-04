from flask import Flask, render_template, request, send_file, redirect, url_for, flash
from pytube import YouTube
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for flash messages

# Define the path to the downloads folder
DOWNLOADS_FOLDER = os.path.join(os.path.dirname(__file__), 'downloads')

# Function to get list of downloaded videos
def get_downloaded_videos():
    videos = []
    for filename in os.listdir(DOWNLOADS_FOLDER):
        if filename.endswith(".mp4"):
            title = os.path.splitext(filename)[0]
            videos.append({'title': title, 'path': os.path.join(DOWNLOADS_FOLDER, filename)})
    return videos

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form['url']
    try:
        yt = YouTube(url)
        stream = yt.streams.filter(progressive=True, file_extension='mp4').first()
        if stream:
            download_path = f"downloads/{yt.title}.mp4"
            stream.download(output_path='downloads/', filename=f"{yt.title}.mp4")
            return send_file(download_path, as_attachment=True)
        else:
            flash('The provided YouTube link is not compatible for download.', 'error')
            return redirect(url_for('home'))
    except Exception as e:
        print(e)
        flash('Error processing the YouTube link.', 'error')
        return redirect(url_for('home'))

@app.route('/overview')
def overview():
    videos = get_downloaded_videos()
    return render_template('overview.html', videos=videos)

@app.route('/remove/<title>')
def remove_video(title):
    try:
        os.remove(f"downloads/{title}.mp4")
        flash(f'Video "{title}" has been removed.', 'success')
    except Exception as e:
        print(e)
        flash(f'Error removing video "{title}".', 'error')
    return redirect(url_for('overview'))

@app.route('/download_again/<title>')
def download_again(title):
    return send_file(f"downloads/{title}.mp4", as_attachment=True, download_name=f"{title}.mp4")

if __name__ == '__main__':
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
    app.run(debug=True,host='0.0.0.0', port=5000)
