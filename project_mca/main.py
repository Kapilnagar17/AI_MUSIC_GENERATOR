import os
from datetime import datetime
from flask import Flask, render_template, request, send_file, url_for
from moviepy.video.io.VideoFileClip import VideoFileClip
from audiocraft.models import MusicGen
from audiocraft.data.audio import audio_write
import subprocess
import torch

app = Flask(__name__)

VIDEO_DIR = "static/videos"
OUTPUT_DIR = "static/output"
os.makedirs(VIDEO_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(os.path.join(OUTPUT_DIR, "Audio"), exist_ok=True)
os.makedirs(os.path.join(OUTPUT_DIR, "Video"), exist_ok=True)

# Check for GPU availability
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# Load model globally (only once)
print("Loading model...")
model = MusicGen.get_pretrained("facebook/musicgen-small")
print("Model loaded successfully!")

def run_ffmpeg_command(command):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            return False, f"FFmpeg Error: {result.stderr.strip()}"
        return True, "FFmpeg operation completed successfully!"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/music", methods=["GET", "POST"])
def music():
    message = None
    audio_url = None
    download_url = None
    if request.method == 'POST':
        prompt = request.form.get('prompt', '').strip()
        if not prompt:
            message = 'No prompt Provided!'
            return render_template('music.html', message=message)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')   
        duration_str = request.form.get('duration', '').strip()
        if not duration_str:
            message = 'No duration provided!'
            return render_template('music.html', message=message)
        try:
            duration = float(duration_str)
        except ValueError:
            message = 'Invalid duration provided!'
            return render_template('music.html', message=message)

        try:
            model.set_generation_params(duration=duration)
            wav = model.generate([prompt])[0].detach().cpu()

            # Save Audio File for future use
            audio_filename = f'Audio_{timestamp}.wav'
            audio_output_path = os.path.join(OUTPUT_DIR, "Audio", audio_filename)
            audio_write(audio_output_path[:-4], wav, model.sample_rate, strategy="loudness")

            if not os.path.exists(audio_output_path):
                message = "Error: Audio file was not created"
                return render_template('music.html', message=message)

            audio_url = url_for('static', filename=f"output/Audio/{audio_filename}")  
        except Exception as e:
            message = f"Error during generation: {str(e)}" 

    return render_template('music.html', message=message, audio_url=audio_url, download_url=download_url)           

@app.route("/video", methods=["GET", "POST"])
def video():
    message = None
    audio_url = None
    video_url = None
    download_url = None
    if request.method == 'POST':
        # Ensure a video file is uploaded
        if 'video' not in request.files or request.files['video'].filename == '':
            message = "No video file uploaded!"
            return render_template('video.html', message=message)

        uploaded_video = request.files['video']

        # Ensure a prompt is provided
        prompt = request.form.get('prompt', '').strip()
        if not prompt:
            message = "No prompt provided!"
            return render_template('video.html', message=message)
        
        # Save uploaded video with a timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        video_filename = f"uploaded_{timestamp}.mp4"
        video_path = os.path.join(VIDEO_DIR, video_filename)
        uploaded_video.save(video_path)

        # Extract the video duration 
        try:
            clip = VideoFileClip(video_path)
            video_duration = int(clip.duration)
            clip.close()
        except Exception as e:
            message = f"Error processing video: {str(e)}"
            return render_template('video.html', message=message)

        # Generate music
        try:
            model.set_generation_params(duration=video_duration)
            wav = model.generate([prompt])[0].detach().cpu()

            # Save audio
            audio_filename = f"generated_audio_{timestamp}.wav"
            audio_output_path = os.path.join(OUTPUT_DIR, "Audio", audio_filename)
            audio_write(audio_output_path[:-4], wav, model.sample_rate, strategy="loudness")

            if not os.path.exists(audio_output_path):
                message = "Error: Audio file was not created!"
                return render_template('video.html', message=message)

            audio_url = url_for('static', filename=f"output/Audio/{audio_filename}")

            # Convert to AAC
            aac_filename = f"generated_audio_{timestamp}.aac"
            aac_output_path = os.path.join(OUTPUT_DIR, aac_filename)
            aac_command = f'ffmpeg -i "{audio_output_path}" -c:a aac -b:a 192k -strict experimental "{aac_output_path}" -y'
            success, ffmpeg_message = run_ffmpeg_command(aac_command)
            if not success:
                message = ffmpeg_message
                return render_template('video.html', message=message, audio_url=audio_url)

            # Merge video and audio with proper audio mapping
            final_filename = f"final_video_{timestamp}.mp4"
            final_output_path = os.path.join(OUTPUT_DIR, "Video", final_filename)
            merge_command = f'ffmpeg -i "{video_path}" -i "{aac_output_path}" -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -b:a 192k -strict experimental -shortest "{final_output_path}" -y'
            success, ffmpeg_message = run_ffmpeg_command(merge_command)
            if not success:
                message = ffmpeg_message
                return render_template('video.html', message=message, audio_url=audio_url)

            if os.path.exists(final_output_path):
                video_url = url_for('static', filename=f"output/Video/{final_filename}")
                download_url = url_for('download_file', filename=final_filename)
            else:
                message = "Error: Final video was not created!"

        except Exception as e:
            message = f"Error during generation: {str(e)}"  

    return render_template('video.html', message=message, audio_url=audio_url, video_url=video_url, download_url=download_url)    

@app.route('/download/<filename>')
def download_file(filename):
    file_path = os.path.join('{OUTPUT_DIR}/video', filename)
    return send_file(file_path, as_attachment=True)      

if __name__ == "__main__":
    app.run(debug=False)
