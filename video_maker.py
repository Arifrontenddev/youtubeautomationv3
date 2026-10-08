#!/usr/bin/env python3
"""video_maker.py - AI Cinematic Video Generator with Real Image Synthesis & Subtitles

Generates real visual scene imagery for each script beat, applies clean broadcast
subtitles/captions over the image, and renders an animated moving .mp4 with voiceover.
"""
import os
import sys
import json
import asyncio
import subprocess
import urllib.request
import urllib.parse
from pathlib import Path
from typing import List, Dict, Any, Optional
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import imageio_ffmpeg
import edge_tts

BASE_DIR = Path(__file__).resolve().parent
RENDERS_DIR = BASE_DIR / "public" / "renders"
IMAGES_DIR = BASE_DIR / "public" / "renders" / "images"
RENDERS_DIR.mkdir(parents=True, exist_ok=True)
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()

VOICES = {
    "guy": "en-US-GuyNeural",
    "christopher": "en-US-ChristopherNeural",
    "aria": "en-US-AriaNeural",
    "jenny": "en-US-JennyNeural",
    "brian": "en-GB-BrianNeural"
}

def get_font(size: int, bold: bool = True):
    """Fallback font loader for high-impact subtitles."""
    font_paths = [
        r"C:\Windows\Fonts\impact.ttf",
        r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\calibrib.ttf" if bold else r"C:\Windows\Fonts\calibri.ttf"
    ]
    for p in font_paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()

def fetch_ai_scene_image(prompt: str, output_path: str, width: int = 1920, height: int = 1080) -> str:
    """Fetch/generate a real AI background image matching the scene prompt with robust fallbacks."""
    import random
    clean_prompt = prompt.strip() or "cinematic digital art high quality 4k"
    enhanced_prompt = f"{clean_prompt}, 8k resolution, cinematic lighting, photorealistic masterpiece"
    encoded = urllib.parse.quote(enhanced_prompt[:200])
    seed = random.randint(1000, 999999)
    
    # 1. Primary: Pollinations AI Generation
    pollinations_urls = [
        f"https://image.pollinations.ai/prompt/{encoded}?width={width}&height={height}&nologo=true&seed={seed}",
        f"https://image.pollinations.ai/prompt/{encoded}?width={width}&height={height}&nologo=true&model=turbo&seed={seed}"
    ]
    
    for api_url in pollinations_urls:
        try:
            req = urllib.request.Request(api_url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
            with urllib.request.urlopen(req, timeout=12) as res:
                img_data = res.read()
                if len(img_data) > 5000:
                    with open(output_path, "wb") as f:
                        f.write(img_data)
                    with Image.open(output_path) as img:
                        img_resized = img.convert("RGB").resize((width, height), Image.Resampling.LANCZOS)
                        img_resized.save(output_path, "JPEG", quality=95)
                    return output_path
        except Exception as e:
            print(f"Pollinations AI try error ({e}), trying next source...")

    # 2. Secondary fallback: High-Resolution curated cinematic photo libraries
    curated_photos = [
        "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=1920&q=85", # Abstract Cyber Neon
        "https://images.unsplash.com/photo-1518770660439-4636190af475?w=1920&q=85", # Tech Circuit Board
        "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=1920&q=85", # Matrix Code Screen
        "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=1920&q=85", # Cyberpunk Futuristic
        "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=1920&q=85", # Earth & Global Tech
        "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=1920&q=85"  # Modern Studio Setup
    ]
    curated_url = curated_photos[abs(hash(clean_prompt)) % len(curated_photos)]
    try:
        req = urllib.request.Request(curated_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=8) as res:
            img_data = res.read()
            with open(output_path, "wb") as f:
                f.write(img_data)
            with Image.open(output_path) as img:
                img_resized = img.convert("RGB").resize((width, height), Image.Resampling.LANCZOS)
                img_resized.save(output_path, "JPEG", quality=95)
            return output_path
    except Exception as e:
        print(f"Curated library fallback notice ({e}), creating canvas...")

    # 3. Fallback gradient canvas
    return create_fallback_canvas(clean_prompt, output_path, width, height)

def create_fallback_canvas(prompt: str, output_path: str, width: int = 1920, height: int = 1080) -> str:
    """Generate a rich cinematic dark gradient backdrop when offline."""
    img = Image.new("RGB", (width, height), color=(14, 18, 26))
    draw = ImageDraw.Draw(img)

    for y in range(height):
        factor = y / height
        r = int(20 * (1 - factor) + 8 * factor)
        g = int(32 * (1 - factor) + 12 * factor)
        b = int(54 * (1 - factor) + 20 * factor)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # Add abstract grid pattern
    for x in range(0, width, 80):
        draw.line([(x, 0), (x, height)], fill=(25, 35, 55))
    for y in range(0, height, 80):
        draw.line([(0, y), (width, y)], fill=(25, 35, 55))

    img.save(output_path, "JPEG", quality=90)
    return output_path

async def generate_voiceover_async(text: str, output_path: str, voice_key: str = "guy") -> float:
    """Generate neural TTS audio file and return audio duration in seconds."""
    voice = VOICES.get(voice_key.lower(), "en-US-GuyNeural")
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)
    
    cmd = [
        FFMPEG_EXE, "-i", output_path,
        "-hide_banner"
    ]
    res = subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    duration = 5.0
    import re
    match = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", res.stderr)
    if match:
        h, m, s = match.groups()
        duration = int(h) * 3600 + int(m) * 60 + float(s)
    return duration

def generate_voiceover(text: str, output_path: str, voice_key: str = "guy") -> float:
    return asyncio.run(generate_voiceover_async(text, output_path, voice_key))

def render_scene_with_captions(
    base_image_path: str,
    spoken_text: str,
    output_image_path: str,
    caption_keyword: str = "",
    width: int = 1920,
    height: int = 1080
):
    """Overlay real YouTube video captions (bold yellow/white text with dark vignette) on the image."""
    with Image.open(base_image_path) as img:
        img = img.convert("RGB").resize((width, height), Image.Resampling.LANCZOS)
        
        # Create a subtle bottom vignette overlay so subtitles pop with maximum contrast
        overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        
        vignette_height = int(height * 0.45)
        for y in range(vignette_height):
            alpha = int((y / vignette_height) ** 1.5 * 190)
            overlay_draw.line(
                [(0, height - vignette_height + y), (width, height - vignette_height + y)],
                fill=(0, 0, 0, alpha)
            )
        
        # Merge vignette overlay
        img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
        draw = ImageDraw.Draw(img)

        # Word wrap spoken sentence into clean 2-3 line caption blocks
        f_sub = get_font(56, bold=True)
        words = spoken_text.split()
        lines = []
        curr = []
        for w in words:
            curr.append(w)
            if len(" ".join(curr)) > 36:
                lines.append(" ".join(curr[:-1]))
                curr = [w]
        if curr:
            lines.append(" ".join(curr))

        # Render only the most impactful 2-3 lines for this segment
        display_lines = lines[:3]
        total_text_height = len(display_lines) * 72
        start_y = height - 120 - total_text_height

        for i, line in enumerate(display_lines):
            line_text = line.upper()
            
            # Calculate text width for centered alignment
            bbox = draw.textbbox((0, 0), line_text, font=f_sub)
            text_w = bbox[2] - bbox[0]
            x_pos = (width - text_w) // 2
            y_pos = start_y + i * 72

            # Black outline / shadow for crisp readability
            outline_width = 4
            for ox in range(-outline_width, outline_width + 1):
                for oy in range(-outline_width, outline_width + 1):
                    if ox != 0 or oy != 0:
                        draw.text((x_pos + ox, y_pos + oy), line_text, font=f_sub, fill=(0, 0, 0))

            # Highlight first line in energetic Yellow, others in White
            text_color = (255, 230, 0) if (i == 0 or len(display_lines) == 1) else (255, 255, 255)
            draw.text((x_pos, y_pos), line_text, font=f_sub, fill=text_color)

        img.save(output_image_path, "JPEG", quality=95)

def create_video_from_beats(
    title: str,
    beats: List[Dict[str, Any]],
    output_filename: str = "output_video.mp4",
    voice_key: str = "guy"
) -> Dict[str, Any]:
    """Assemble complete moving MP4 video with real AI scene images, audio sync, and captions."""
    temp_dir = BASE_DIR / "temp_render"
    temp_dir.mkdir(exist_ok=True)
    
    video_segments = []
    total_duration = 0.0

    try:
        for idx, beat in enumerate(beats):
            spoken_text = beat.get("spoken", "").strip()
            if not spoken_text:
                continue

            image_prompt = beat.get("image_prompt") or beat.get("visual") or f"Cinematic scene for {title}"
            caption_highlight = beat.get("caption_overlay", "")

            audio_path = str(temp_dir / f"audio_{idx}.mp3")
            
            # Use specific image if already generated / assigned in beat
            img_filename = beat.get("image_filename")
            if not img_filename and beat.get("image_url"):
                img_filename = os.path.basename(beat["image_url"].split("?")[0])
            if not img_filename:
                img_filename = f"scene_{idx}_{abs(hash(image_prompt)) % 100000}.jpg"

            raw_ai_img_path = str(IMAGES_DIR / img_filename)
            captioned_img_path = str(temp_dir / f"captioned_{idx}.jpg")
            segment_video_path = str(temp_dir / f"segment_{idx}.mp4")

            # 1. Generate Voiceover Audio
            dur = generate_voiceover(spoken_text, audio_path, voice_key=voice_key)
            dur = max(dur, 2.5)
            total_duration += dur

            # 2. Fetch/Generate Real AI Scene Image (if not already cached)
            if not os.path.exists(raw_ai_img_path):
                fetch_ai_scene_image(image_prompt, raw_ai_img_path)

            # 3. Overlay Real Video Subtitles / Captions
            render_scene_with_captions(
                base_image_path=raw_ai_img_path,
                spoken_text=spoken_text,
                output_image_path=captioned_img_path,
                caption_keyword=caption_highlight
            )

            # 4. Render Animated Video Clip (Smooth Ken Burns Zoom across the real AI image)
            frames_count = int(dur * 25)
            # Alternate between zoom in and subtle pan for each beat
            if idx % 2 == 0:
                zoom_filter = f"zoompan=z='min(zoom+0.0015,1.20)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames_count}:s=1920x1080:fps=25"
            else:
                zoom_filter = f"zoompan=z='1.12':x='if(lte(on,1),(iw-iw/zoom)/2,x+0.5)':y='ih/2-(ih/zoom/2)':d={frames_count}:s=1920x1080:fps=25"

            cmd = [
                FFMPEG_EXE, "-y",
                "-loop", "1", "-i", captioned_img_path,
                "-i", audio_path,
                "-vf", zoom_filter,
                "-c:v", "libx264", "-tune", "stillimage",
                "-c:a", "aac", "-b:a", "192k",
                "-pix_fmt", "yuv420p", "-t", str(dur),
                segment_video_path
            ]
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            video_segments.append(segment_video_path)

        # 5. Concatenate into Final MP4 Video
        concat_list_path = str(temp_dir / "concat_list.txt")
        with open(concat_list_path, "w", encoding="utf-8") as f:
            for seg in video_segments:
                f.write(f"file '{Path(seg).as_posix()}'\n")

        final_output_path = str(RENDERS_DIR / output_filename)
        concat_cmd = [
            FFMPEG_EXE, "-y",
            "-f", "concat", "-safe", "0", "-i", concat_list_path,
            "-c", "copy",
            final_output_path
        ]
        subprocess.run(concat_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        return {
            "status": "success",
            "video_filename": output_filename,
            "video_url": f"/renders/{output_filename}",
            "file_path": final_output_path,
            "duration_seconds": round(total_duration, 1),
            "segments_count": len(video_segments)
        }
    finally:
        for f in temp_dir.glob("*.*"):
            try:
                f.unlink()
            except Exception:
                pass
