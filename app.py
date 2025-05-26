from flask import Flask, render_template, request, send_file
import yt_dlp
import os
import uuid

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/youtube', methods=['GET', 'POST'])
def youtube_downloader():
    if request.method == 'POST':
        url = request.form.get('url')
        if not url:
            return render_template('youtube.html', error='Please provide a YouTube URL')

        # Extract video info and formats
        ydl_opts = {'quiet': True, 'skip_download': True}
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)

            selected_format = request.form.get('format')
            selected_quality = request.form.get('quality')

            if selected_format and selected_quality:
                # Prepare download path
                unique_filename = str(uuid.uuid4())
                downloads_dir = 'downloads'
                os.makedirs(downloads_dir, exist_ok=True)

                if selected_format == 'mp3':
                    outtmpl = os.path.join(downloads_dir, unique_filename + '.mp3')
                    ydl_opts = {
                        'format': 'bestaudio/best',
                        'outtmpl': outtmpl,
                        'postprocessors': [{
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': 'mp3',
                            'preferredquality': '192',
                        }],
                        'quiet': True,
                    }
                else:
                    # Video download with best video <= selected quality + best audio
                    outtmpl = os.path.join(downloads_dir, unique_filename + '.mp4')
                    ydl_opts = {
                        'format': f'bestvideo[height<={selected_quality}]+bestaudio/best',
                        'merge_output_format': 'mp4',
                        'outtmpl': outtmpl,
                        'quiet': True,
                    }

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])

                return send_file(outtmpl, as_attachment=True)

            # Show preview + quality options if no download request
            formats = info.get('formats', [])
            video_qualities = set()
            for f in formats:
                if f.get('vcodec') != 'none' and f.get('acodec') != 'none' and f.get('height') and f.get('ext') in ['mp4', 'webm']:
                    video_qualities.add(f['height'])
            video_qualities = sorted(list(video_qualities))

            return render_template('youtube.html',
                                   info=info,
                                   video_qualities=video_qualities,
                                   error=None)

        except Exception as e:
            return render_template('youtube.html', error=f"Error: {str(e)}")

    # GET request: show URL input form
    return render_template('youtube.html')


@app.route('/instagram', methods=['GET', 'POST'])
def instagram_downloader():
    return render_template('instagram.html')


if __name__ == '__main__':
    app.run(debug=True)
