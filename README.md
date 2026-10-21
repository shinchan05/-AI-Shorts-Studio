# -AI-Shorts-Studio
A local, Python-based application for creating vertical YouTube Shorts from storyboards, scene images, narration, and captions.  The project is a prototype exploring a free, locally controlled AI-assisted video creation workflow using Python, Streamlit, ComfyUI, and FFmpeg.
✨ Current Features

Storyboard generation: Creates a structured sequence of scenes from a topic using predefined Python templates.

Editable scenes: Customize scene captions and visual prompts.

Custom visuals: Upload PNG or JPG images generated with ComfyUI or other image-generation tools.

Vertical formatting: Crops and resizes images to a 9:16 video format at 720 × 1280.

Caption overlays: Adds large, high-contrast text captions to scene images.

Text-to-speech narration: Generates narration using Microsoft Edge TTS through the edge-tts Python package.

Video rendering: Uses FFmpeg to assemble images, narration, and optional background music into an MP4.

Configurable duration: Supports target durations of 15, 20, 30, 45, and 60 seconds.

Local project output: Saves generated video files under the project's outputs/ directory.

🛠️ Technology Stack

Python

Streamlit

Pillow

Edge TTS

FFmpeg

ComfyUI with Stable Diffusion 1.5 for manually generated scene images

🖥️ System Requirements

Windows 10 or Windows 11

Python environment compatible with the project's dependencies

FFmpeg installed and accessible through PATH

Internet access for Edge TTS narration

ComfyUI is optional and can be used to generate images locally

An NVIDIA GPU is useful for local image generation but is not required by the basic image-based video renderer.

🚀 Setup

1. Clone the repository

git clone https://github.com/YOUR_USERNAME/ai-shorts-studio.git
cd ai-shorts-studio

2. Create a virtual environment

python -m venv .venv

Activate it in Windows PowerShell:

.\.venv\Scripts\Activate.ps1

3. Install dependencies

python -m pip install -r requirements.txt

4. Install FFmpeg

Install an FFmpeg Windows build and add its bin directory to PATH.

Verify the installation:

ffmpeg -version

5. Run the application

python -m streamlit run app.py

Open the local URL printed in the terminal, usually:

http://localhost:8501

🎞️ How to Create a Short

Enter a topic and choose a visual style and target duration.

Generate the storyboard.

Edit the scene captions and visual prompts.

Generate or collect scene images using ComfyUI or another image tool.

Upload the images in storyboard order and save them.

Choose a narration voice.

Optionally upload licensed background music.

Render the Short and review the resulting MP4.

📂 Project Structure

ai-shorts-studio/
├── app.py
├── requirements.txt
├── README.md
├── assets/
├── outputs/
│   ├── scenes/
│   └── short_*/
└── .gitignore

Generated files and the virtual environment should not normally be committed to GitHub.

⚠️ Current Limitations

The current renderer uses still images with caption overlays; it does not generate continuous AI video footage.

Scene images must currently be supplied manually.

Storyboards use predefined Python templates rather than a connected language model.

Edge TTS requires internet access and may sound less expressive than a dedicated storytelling voice model.

Narration pacing and scene timing may require manual review.

Generated content must be checked for factual accuracy, copyright, and suitability before publication.

🗺️ Roadmap

Version 1 — Image-Based Shorts

Streamlit interface

Storyboard templates

Manual scene image upload

Vertical image formatting

Caption overlays

Edge TTS narration

FFmpeg MP4 rendering

Version 2 — Automated Production

Automatic generation of scene images

Improved storytelling scripts and narration

Automatic scene timing and synchronization

Quality checks for audio, captions, and video

One-click video creation

Version 3 — AI Video Generation

Evaluate open-source text-to-video and image-to-video models

Generate moving footage locally where hardware permits

Integrate generated clips into the rendering pipeline

Add transitions and improved sound design

Version 4 — Publishing Workflow

Generate titles and descriptions

Prepare upload metadata

Explore YouTube Data API integration

Add publishing status and analytics tracking

📌 Project Status

Status: Working prototype — image-based video rendering verified.

The current version can render an MP4 using uploaded images, caption overlays, and generated narration. Full scene-generation automation, expressive narration, AI-generated moving footage, and automated YouTube publishing remain future development goals.

📄 License

Choose a license before publicly distributing or accepting contributions. Check the licenses of all third-party models, packages, and assets used in the project.
