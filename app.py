import asyncio, json, os, re, subprocess, time, uuid, math
from pathlib import Path
import requests
import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import edge_tts

ROOT = Path(__file__).parent
OUT = ROOT / "outputs"
OUT.mkdir(exist_ok=True)
W, H = 720, 1280

st.set_page_config(page_title="AI Shorts Studio", page_icon="🎬", layout="wide")
st.title("🎬 AI Shorts Studio — Story Cut")
st.caption("More scenes • male narration • punchy captions • cinematic pacing")

def ffmpeg(args):
    try:
        return subprocess.run(args, capture_output=True, text=True, check=True)
    except FileNotFoundError:
        raise RuntimeError("FFmpeg not found. Add its bin folder to PATH and restart Streamlit.")
    except subprocess.CalledProcessError as e:
        raise RuntimeError((e.stderr or e.stdout or "FFmpeg failed")[-2500:])

def font(size, bold=True):
    paths = ([r"C:\Windows\Fonts\arialbd.ttf", r"C:\Windows\Fonts\Arial.ttf"] if bold else [r"C:\Windows\Fonts\arial.ttf"])
    for p in paths:
        if os.path.exists(p):
            try: return ImageFont.truetype(p, size)
            except Exception: pass
    return ImageFont.load_default()

def wrap(draw, text, fnt, max_width):
    words = text.split()
    lines, line = [], ""
    for word in words:
        trial = (line + " " + word).strip()
        if draw.textbbox((0,0), trial, font=fnt)[2] <= max_width or not line:
            line = trial
        else:
            lines.append(line); line = word
    if line: lines.append(line)
    return lines

def fit_vertical(im):
    im = im.convert("RGB")
    ratio = W/H
    if im.width/im.height > ratio:
        nw = int(im.height*ratio); x=(im.width-nw)//2; im=im.crop((x,0,x+nw,im.height))
    else:
        nh = int(im.width/ratio); y=(im.height-nh)//2; im=im.crop((0,y,im.width,y+nh))
    return im.resize((W,H), Image.Resampling.LANCZOS)

def draw_caption(src, dst, text, idx, total):
    im = fit_vertical(Image.open(src))
    overlay = Image.new("RGBA", im.size, (0,0,0,0))
    d = ImageDraw.Draw(overlay)
    # dark gradient-ish lower panel
    for j in range(410):
        alpha = int(155 * (j/410))
        d.line((0, H-410+j, W, H-410+j), fill=(0,0,0,alpha))
    # scene counter   
    f = font(43)
    lines = wrap(d, text.upper(), f, W-76)[:4]
    lh = 54
    y = H - 220 - lh*len(lines)
    for line in lines:
        bb = d.textbbox((0,0), line, font=f)
        x = (W-(bb[2]-bb[0]))//2
        d.text((x+3,y+4), line, font=f, fill=(0,0,0,220), stroke_width=3, stroke_fill=(0,0,0,200))
        d.text((x,y), line, font=f, fill=(255,255,255,255), stroke_width=1, stroke_fill=(10,10,10,255))
        y += lh
    out = Image.alpha_composite(im.convert("RGBA"), overlay).convert("RGB")
    out.save(dst, quality=94)

def script_pack(topic, style):
    topic_l = topic.lower().strip()
    if "moon" in topic_l:
        return [
            ("HOOK", "What if the Moon vanished tonight?", "The full Moon hangs over Earth, enormous and luminous, clouds drifting across its surface, cinematic astronomy, vertical 9:16."),
            ("SILENCE", "In one instant… it is gone.", "A bright full Moon suddenly disappears from a starry night sky above a quiet city, dramatic contrast, cinematic wide-to-close composition, vertical 9:16."),
            ("LOOK UP", "The sky would look strangely empty.", "Person standing on a rooftop looking up at a moonless sky filled with stars, silhouette, emotional cinematic lighting, vertical 9:16."),
            ("THE OCEAN", "And the oceans would feel the difference.", "Powerful ocean waves rolling along a rugged coastline at night, dark blue water, aerial cinematic view, vertical 9:16."),
            ("TIDES", "The Moon helps drive Earth's tides.", "Dramatic aerial view of tidal flats and ocean currents around a coastline, moonless night transitioning toward dawn, realistic science documentary, vertical 9:16."),
            ("WILDLIFE", "Some animals use moonlight as a signal.", "Nocturnal seabirds moving above dark ocean waves under a starry sky, natural-history documentary, dramatic but realistic, vertical 9:16."),
            ("DARKNESS", "Night journeys would become harder for many creatures.", "Small nocturnal animals navigating a dim forest floor, tiny points of starlight through trees, cinematic macro details, vertical 9:16."),
            ("THE BIG PICTURE", "But Earth would not fly off into space.", "Planet Earth rotating in space with the Sun glowing in the distance, realistic NASA-style visual, deep black starfield, vertical 9:16."),
            ("GRAVITY", "Our planet would still orbit the Sun.", "Earth orbiting the Sun represented by a beautiful cinematic space view, no labels or text, realistic astronomy imagery, vertical 9:16."),
            ("A DIFFERENT SKY", "The night sky would lose its familiar companion.", "Wide star field above mountains with no Moon, lonely atmospheric landscape, deep blue night, cinematic composition, vertical 9:16."),
            ("THE TWIST", "And Earth's long-term wobble would change too.", "Earth spinning in space with a subtle tilted axis, elegant scientific visualization, no text, cinematic lighting, vertical 9:16."),
            ("ENDING", "Would you spend one night on a Moonless Earth?", "Beautiful Earth horizon under a dense star field, slow dramatic reveal, hopeful cinematic ending, vertical 9:16.")
        ]
    # General reusable scene structure for other topics
    return [
        ("HOOK", f"What if {topic} changed everything?", f"Striking cinematic opening visual about {topic}, dramatic lighting, high contrast, vertical 9:16, no text."),
        ("SETUP", f"At first, the change might seem small.", f"Close-up establishing shot illustrating {topic}, realistic cinematic detail, vertical 9:16, no text."),
        ("ZOOM IN", "But look closer.", f"Extreme close-up of a key detail related to {topic}, shallow depth of field, vertical 9:16, no text."),
        ("THE CHANGE", "Then one unexpected thing happens.", f"Dramatic turning point showing {topic}, dynamic composition, vertical 9:16, no text."),
        ("CONSEQUENCE", "And the consequences spread much further.", f"Wide cinematic scene showing consequences of {topic}, realistic lighting, vertical 9:16, no text."),
        ("SURPRISE", "Here is the part most people miss.", f"Surprising visual detail related to {topic}, cinematic reveal, vertical 9:16, no text."),
        ("BIG PICTURE", "The bigger picture is even stranger.", f"Epic wide shot about {topic}, cinematic atmosphere, vertical 9:16, no text."),
        ("ENDING", f"What would you do if {topic} happened?", f"Memorable cinematic final shot related to {topic}, vertical 9:16, no text.")
    ]

st.sidebar.header("Video settings")
topic = st.sidebar.text_area("Topic / idea", "What if the Moon disappeared for one night?", height=90)
style = st.sidebar.selectbox("Visual style", ["Cinematic science", "Realistic documentary", "Mystery", "Fantasy"])
duration = st.sidebar.select_slider("Target length (seconds)", options=[15,20,30,45,60], value=30)
voice = st.sidebar.selectbox("Narrator voice", [
    "en-US-GuyNeural — Male US",
    "en-US-ChristopherNeural — Male US",
    "en-GB-RyanNeural — Male UK",
    "en-IN-PrabhatNeural — Male Indian English",
    "en-US-AriaNeural — Female US"
])
voice_id = voice.split(" — ")[0]
st.sidebar.caption("AI narration uses edge-tts and requires internet access.")

st.info("This version makes a faster, more dramatic image-based Short. It still uses scene images rather than continuous AI-generated video footage.")
tabs = st.tabs(["1 · Storyboard", "2 · Add visuals", "3 · Render Short"])
with tabs[0]:
    if st.button("Build cinematic storyboard"):
        st.session_state.storyboard = script_pack(topic, style)
    if "storyboard" not in st.session_state:
        st.session_state.storyboard = script_pack(topic, style)
    rows = st.session_state.storyboard
    st.write(f"**{len(rows)} planned scenes** — edit the on-screen captions and visual prompts before rendering.")
    edited=[]
    for i, (label, caption, prompt) in enumerate(rows):
        with st.expander(f"Scene {i+1}: {label}", expanded=(i<2)):
            new_caption=st.text_input("On-screen caption", caption, key=f"cap_{i}")
            new_prompt=st.text_area("Visual prompt (for image generation)", prompt, key=f"vis_{i}", height=80)
            edited.append((label,new_caption,new_prompt))
    st.session_state.storyboard=edited
    script = " ".join([x[1] for x in edited])
    st.text_area("Narration script (edit this to control what is spoken)", script, key="narration_script", height=150)
    st.caption("Tip: make the narration punchy. The scene captions are designed to change frequently.")
with tabs[1]:
    st.write("Upload one image per scene, in order. Images are cropped to 9:16. You can use images you create with any tool; ComfyUI is optional.")
    uploads = st.file_uploader("Upload scene images (PNG/JPG), in storyboard order", type=["png","jpg","jpeg"], accept_multiple_files=True)
    if uploads:
        st.caption(f"{len(uploads)} images uploaded for {len(st.session_state.storyboard)} storyboard scenes.")
        if st.button("Save scene images"):
            scene_dir=OUT/"scenes"; scene_dir.mkdir(exist_ok=True)
            saved=[]
            for i, up in enumerate(uploads):
                p=scene_dir/f"scene_{i+1:02d}.png"
                fit_vertical(Image.open(up)).save(p)
                saved.append(str(p))
            st.session_state.scene_paths=saved
            st.success(f"Saved {len(saved)} images.")
    if st.session_state.get("scene_paths"):
        cols=st.columns(4)
        for i,p in enumerate(st.session_state.scene_paths):
            cols[i%4].image(p, caption=f"Scene {i+1}", use_container_width=True)
with tabs[2]:
    st.write("The renderer distributes time across scenes, adds camera-like zoom/pan, caption overlays, male narration and optional background music.")
    music=st.file_uploader("Optional background music (MP3/WAV; use audio you have rights to)", type=["mp3","wav"])
    if st.button("🎬 Render my Short", type="primary"):
        scene_paths=st.session_state.get("scene_paths", [])
        board=st.session_state.storyboard
        if not scene_paths:
            st.error("First upload and save scene images in tab 2.")
        elif len(scene_paths) < len(board):
            st.error(f"You have {len(scene_paths)} images but {len(board)} scenes. Upload one image per scene.")
        else:
            job=OUT/f"short_{time.strftime('%Y%m%d_%H%M%S')}"
            job.mkdir(parents=True,exist_ok=True)
            try:
                audio=job/"narration.mp3"
                narration=st.session_state.get("narration_script", " ".join([r[1] for r in board]))
                async def speak():
                    await edge_tts.Communicate(narration, voice_id, rate="+5%", volume="+0%").save(str(audio))
                asyncio.run(speak())
                captioned=[]
                for i, (_,cap,_) in enumerate(board):
                    cp=job/f"caption_{i+1:02d}.jpg"
                    draw_caption(scene_paths[i],cp,cap,i,len(board))
                    captioned.append(cp)
                # Allocate duration proportional to caption count; make quick, energetic cuts.
                per_scene=max(1.25, duration/len(captioned))
                clips=[]
                progress=st.progress(0)
                for i,cp in enumerate(captioned):
                    clip=job/f"scene_{i+1:02d}.mp4"
                    frames=max(30,int(per_scene*24))
                    # slow zoom for visual energy; output 24fps
                    vf=f"scale=720:1280,zoompan=z='min(zoom+0.0012,1.10)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s=720x1280:fps=24,format=yuv420p"
                    ffmpeg(["ffmpeg","-y","-loop","1","-i",str(cp),"-t",str(per_scene),"-vf",vf,"-r","24","-an","-c:v","libx264","-preset","veryfast","-pix_fmt","yuv420p",str(clip)])
                    clips.append(clip); progress.progress((i+1)/len(captioned))
                concat=job/"concat.txt"
                concat.write_text("".join("file '"+str(p).replace("'","'\\''")+"'\n" for p in clips),encoding="utf-8")
                silent=job/"video_only.mp4"
                ffmpeg(["ffmpeg","-y","-f","concat","-safe","0","-i",str(concat),"-c","copy",str(silent)])
                final=job/"final_short.mp4"
                if music:
                    music_path=job/("music"+Path(music.name).suffix)
                    music_path.write_bytes(music.getvalue())
                    ffmpeg(["ffmpeg","-y","-i",str(silent),"-i",str(audio),"-i",str(music_path),"-filter_complex","[1:a]volume=1.0[voice];[2:a]volume=0.10[music];[voice][music]amix=inputs=2:duration=shortest:dropout_transition=2[a]","-map","0:v:0","-map","[a]","-c:v","copy","-c:a","aac","-b:a","192k","-shortest","-movflags","+faststart",str(final)])
                else:
                    ffmpeg(["ffmpeg","-y","-i",str(silent),"-i",str(audio),"-map","0:v:0","-map","1:a:0","-c:v","copy","-c:a","aac","-b:a","192k","-shortest","-movflags","+faststart",str(final)])
                st.success("Your Short is ready!")
                st.video(str(final))
                st.download_button("Download final MP4", final.read_bytes(), file_name="ai_short.mp4", mime="video/mp4")
                st.caption(f"Saved at: {final}")
            except Exception as e:
                st.error(f"Render failed: {e}")
                st.info("Check FFmpeg is on PATH and edge-tts can access the internet.")

st.divider()
st.caption("For fully generated moving footage, the next step is choosing a ComfyUI video model based on your GPU VRAM.")
