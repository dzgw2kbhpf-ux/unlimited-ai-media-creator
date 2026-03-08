# Unlimited AI Media Creator

This is a web-based tool for generating, editing images, and creating videos using AI. It's completely free, unlimited, and supports NSFW content. Built with Flask, Diffusers (Stable Diffusion), and other libraries.

## Features
- Image Generation: Generate images from text prompts.
- Image Editing: Edit existing images with prompts.
- Video Generation: Generate videos from prompts or images.
- Audio Addition: Add custom audio to videos using text-to-speech.
- Supports up to 100 image uploads.
- NSFW enabled (safety checker disabled).

## Setup
1. Clone the repo: `git clone https://github.com/dzgw2kbhpf-ux/unlimited-ai-media-creator.git`
2. Install dependencies: `pip install -r requirements.txt`
3. Run the app: `python app.py`
4. Open in browser: http://localhost:5000

## Requirements
- Python 3.8+
- GPU recommended for faster generation (use CUDA if available).
- For deployment: Use Heroku, Vercel, or Google Colab with GPU.

## Usage
- Enter prompts for generation.
- Upload up to 100 images for editing or video input.
- Specify audio text for video sound.

## Notes
- This tool uses heavy AI models; expect longer generation times without GPU.
- NSFW content is allowed; use responsibly.
- For video audio, it uses gTTS for text-to-speech.

## License
MIT License
