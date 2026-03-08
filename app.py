from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import torch
from diffusers import StableDiffusionPipeline, StableDiffusionImg2ImgPipeline, StableDiffusionInpaintPipeline
from diffusers import DiffusionPipeline as VideoPipeline  # Assuming video diffusion model
from PIL import Image
import io
import base64
import os
import uuid
from moviepy.editor import VideoFileClip, AudioFileClip
from gtts import gTTS
import numpy as np
import traceback

app = Flask(__name__)
CORS(app)

# Load models with NSFW disabled
device = "cuda" if torch.cuda.is_available() else "cpu"

# Image Generation Model
img_gen_pipe = StableDiffusionPipeline.from_pretrained("CompVis/stable-diffusion-v1-4", safety_checker=None)
img_gen_pipe = img_gen_pipe.to(device)

# Image Editing Model (Img2Img)
img_edit_pipe = StableDiffusionImg2ImgPipeline.from_pretrained("CompVis/stable-diffusion-v1-4", safety_checker=None)
img_edit_pipe = img_edit_pipe.to(device)

# Video Generation Model (仮定のビデオモデル、実際にはText2Videoや適切なモデルを使う)
# Note: For real video gen, use a model like "damo-vilab/text-to-video-ms-1.7b"
video_gen_pipe = VideoPipeline.from_pretrained("damo-vilab/text-to-video-ms-1.7b")
video_gen_pipe = video_gen_pipe.to(device)

# Temp directory for files
TEMP_DIR = "temp"
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

def generate_unique_id():
    return str(uuid.uuid4())

def save_image(img, filename):
    path = os.path.join(TEMP_DIR, filename)
    img.save(path)
    return path

def generate_audio(text, lang='en'):
    try:
        tts = gTTS(text=text, lang=lang)
        audio_path = os.path.join(TEMP_DIR, f"audio_{generate_unique_id()}.mp3")
        tts.save(audio_path)
        return audio_path
    except Exception as e:
        raise ValueError(f"Audio generation failed: {str(e)}")

def add_audio_to_video(video_path, audio_path):
    try:
        video = VideoFileClip(video_path)
        audio = AudioFileClip(audio_path)
        video_with_audio = video.set_audio(audio)
        output_path = os.path.join(TEMP_DIR, f"video_with_audio_{generate_unique_id()}.mp4")
        video_with_audio.write_videofile(output_path, codec='libx264', audio_codec='aac')
        return output_path
    except Exception as e:
        raise ValueError(f"Adding audio failed: {str(e)}")

@app.route('/generate_image', methods=['POST'])
def generate_image():
    try:
        data = request.json
        prompt = data.get('prompt', '')
        num_images = min(data.get('num_images', 1), 100)  # Max 100
        if not prompt:
            return jsonify({'error': 'Prompt is required'}), 400
        
        images = []
        for _ in range(num_images):
            image = img_gen_pipe(prompt).images[0]
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            images.append(img_str)
        
        return jsonify({'images': images})
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/edit_image', methods=['POST'])
def edit_image():
    try:
        prompt = request.form.get('prompt', '')
        files = request.files.getlist('images')
        if not prompt or not files:
            return jsonify({'error': 'Prompt and at least one image required'}), 400
        
        num_images = min(len(files), 100)  # Max 100
        edited_images = []
        for file in files[:num_images]:
            img = Image.open(file.stream)
            edited = img_edit_pipe(prompt=prompt, image=img, strength=0.75).images[0]
            buffered = io.BytesIO()
            edited.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            edited_images.append(img_str)
        
        return jsonify({'images': edited_images})
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/generate_video', methods=['POST'])
def generate_video():
    try:
        data = request.json
        prompt = data.get('prompt', '')
        audio_text = data.get('audio_text', '')
        if not prompt:
            return jsonify({'error': 'Prompt is required'}), 400
        
        # Generate video (assuming model outputs frames)
        video_frames = video_gen_pipe(prompt).frames  # [num_frames, height, width, 3]
        video_array = np.array(video_frames)  # Convert to numpy
        
        # Save video
        video_path = os.path.join(TEMP_DIR, f"video_{generate_unique_id()}.mp4")
        # Use moviepy to write video
        clip = VideoFileClip.from_images(video_array)  # Custom function if needed
        clip.write_videofile(video_path, fps=24)
        
        if audio_text:
            audio_path = generate_audio(audio_text)
            video_path = add_audio_to_video(video_path, audio_path)
        
        return send_file(video_path, mimetype='video/mp4', as_attachment=True)
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/cleanup', methods=['POST'])
def cleanup():
    try:
        for file in os.listdir(TEMP_DIR):
            os.remove(os.path.join(TEMP_DIR, file))
        return jsonify({'message': 'Temp files cleaned'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/')
def index():
    return send_file('index.html')

if __name__ == '__main__':
    app.run(debug=True)
