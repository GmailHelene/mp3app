from flask import Flask, request, render_template, send_from_directory
import yt_dlp
import os
import zipfile

app = Flask(__name__)
ZIP_NAME = "alle_sanger.zip"
DOWNLOAD_FOLDER = os.path.join(os.getcwd(), "downloads")
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    status = ""
    files = []
    if request.method == "POST":
        input_text = request.form["songs"]
        song_titles = [line.strip() for line in input_text.strip().split("\n") if line.strip()]
        for title in song_titles:
            try:
                safe_title = title.replace(" ", "_").replace("/", "_")
                output_path = os.path.join(DOWNLOAD_FOLDER, f"{safe_title}.%(ext)s")
                ydl_opts = {
                    "format": "bestaudio/best",
                    "outtmpl": output_path,
                    "postprocessors": [{
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192",
                    }],
                    "postprocessor_args": ["-ar", "44100"],
                    "prefer_ffmpeg": True,
                    "ffmpeg_location": "ffmpeg"
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([f"ytsearch1:{title}"])
                status += f"✅ {title}<br>"
            except Exception as e:
                status += f"❌ {title} – Feil: {str(e)}<br>"

        files = [f for f in os.listdir(DOWNLOAD_FOLDER) if f.endswith(".mp3")]
        if files:
            zip_path = os.path.join(DOWNLOAD_FOLDER, ZIP_NAME)
            with zipfile.ZipFile(zip_path, "w") as zipf:
                for f in files:
                    zipf.write(os.path.join(DOWNLOAD_FOLDER, f), arcname=f)

    files = [f for f in os.listdir(DOWNLOAD_FOLDER) if f.endswith(".mp3")]
    return render_template("index.html", status=status, files=files)

@app.route("/downloads/<filename>")
def download_file(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)

@app.route("/download_zip")
def download_zip():
    return send_from_directory(DOWNLOAD_FOLDER, ZIP_NAME, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
