#!/usr/bin/env python3
"""gemini_service.py - Google Gemini AI Integration for Script & Visual Enhancement

Uses Gemini 2.5 Flash to generate contextual visual prompts, caption lower-thirds,
motion camera directions, and enhance scripts into broadcast video compositions.
"""
import os
import json
from typing import List, Dict, Any, Optional
import google.generativeai as genai

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyByYUgDesP2NMnlHyGj4i8zKdL-ykUJclo")
genai.configure(api_key=GEMINI_API_KEY)

MODEL_NAME = "gemini-2.5-flash"

def get_gemini_model():
    return genai.GenerativeModel(
        MODEL_NAME,
        generation_config={"response_mime_type": "application/json"}
    )

def enhance_script_with_gemini(topic: str, beats: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Use Gemini AI to generate rich photorealistic visual image prompts and clean subtitles for each beat."""
    prompt = f"""
You are an expert AI Video Producer.
Given the topic: "{topic}" and the following spoken script beats, create a stunning visual scene for each beat:
1. "image_prompt": A clean, photorealistic/cinematic image description describing the background picture (e.g. "Futuristic AI server room with glowing blue cables and floating data particles, 8k photorealistic", "Close up of person looking shocked at a glowing laptop screen at night, cinematic lighting", "Split screen showing manual calendar vs automated digital workflow diagram"). Do NOT include words like "title card" or "slide". Make it a real scene/photo/digital artwork prompt.
2. "caption_overlay": The primary 3-7 word punchy subtitle phrase to show on screen (e.g. "STOP WASTING 3 HOURS EVERY WEEK").

Input beats:
{json.dumps(beats, indent=2)}

Return a JSON array of objects with the original fields plus "image_prompt" and "caption_overlay".
"""
    try:
        model = get_gemini_model()
        response = model.generate_content(prompt)
        enhanced = json.loads(response.text.strip())
        if isinstance(enhanced, list):
            return enhanced
        elif isinstance(enhanced, dict) and "beats" in enhanced:
            return enhanced["beats"]
        return beats
    except Exception as e:
        print(f"Gemini enhancement fallback: {e}")
        # Fallback enhancement
        enhanced = []
        effects = ["zoom_in", "pan_left", "zoom_out", "pan_right", "dynamic_pulse"]
        themes = ["cyber_red", "neon_blue", "emerald_tech", "royal_purple", "amber_gold"]
        for i, b in enumerate(beats):
            b_copy = dict(b)
            b_copy["image_prompt"] = f"Cinematic 3D render illustrating {topic}, high contrast lighting, modern creator studio style."
            b_copy["caption_overlay"] = b.get("spoken", "")[:40] + "..."
            b_copy["motion_effect"] = effects[i % len(effects)]
            b_copy["visual_theme"] = themes[i % len(themes)]
            b_copy["b_roll_description"] = f"Smooth camera motion across {topic} infographic with particle effects."
            enhanced.append(b_copy)
        return enhanced
