#!/usr/bin/env python3
"""YouTube Agent Automation Studio - Backend Server

FastAPI server exposing all 11 YouTube agent skills and 6 core analysis engines.
"""
import os
import re
import json
import csv
import io
import statistics
from typing import Optional, List, Dict, Any
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from pydantic import BaseModel

# Base directory
BASE_DIR = Path(__file__).resolve().parent
SKILLS_DIR = BASE_DIR / "skills"
TEMPLATES_DIR = BASE_DIR / "templates"
PUBLIC_DIR = BASE_DIR / "public"

# Ensure directories
PUBLIC_DIR.mkdir(exist_ok=True)

# Import local skill tools
import sys
sys.path.insert(0, str(SKILLS_DIR / "yt-script"))
sys.path.insert(0, str(SKILLS_DIR / "yt-package"))
sys.path.insert(0, str(SKILLS_DIR / "yt-edit"))
sys.path.insert(0, str(SKILLS_DIR / "yt-chapters"))
sys.path.insert(0, str(SKILLS_DIR / "yt-retention"))
sys.path.insert(0, str(SKILLS_DIR / "yt-viral"))

import hookscore
import title as title_linter
import deadair
import chapters as chapter_mod
import retention as retention_mod
import swipe as swipe_mod
import video_maker
import youtube_uploader
import gemini_service

app = FastAPI(
    title="YouTube Agent Automation Studio",
    description="Interactive Studio and Automation Suite for 11 YouTube Agent Skills",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------- Data Models -----------------

class VideoRenderRequest(BaseModel):
    title: str
    beats: List[Dict[str, Any]]
    voice_key: Optional[str] = "guy"

class YouTubeUploadRequest(BaseModel):
    video_path: Optional[str] = None
    title: str
    description: str
    tags: Optional[List[str]] = None
    privacy_status: Optional[str] = "private"
    category_id: Optional[str] = "28"

class HookScoreRequest(BaseModel):
    hook: str

class HookBatchScoreRequest(BaseModel):
    hooks: List[str]

class ScriptGenerateRequest(BaseModel):
    topic: str
    target_duration_minutes: Optional[int] = 8
    target_audience: Optional[str] = "General Audience / Creators"
    call_to_action: Optional[str] = "Comment your biggest takeaway below"
    selected_hook: Optional[str] = None
    voice_profile: Optional[str] = None

class PackageLintRequest(BaseModel):
    title: str
    thumbnail_text: Optional[str] = ""

class PackageGenerateRequest(BaseModel):
    topic: str
    target_audience: Optional[str] = "Tech & Creator Enthusiasts"

class DeadAirRequest(BaseModel):
    transcript_text: str
    floor: Optional[float] = 0.45

class ChaptersRequest(BaseModel):
    transcript_text: str
    target_chapters: Optional[int] = 7

class RetentionAnalyzeRequest(BaseModel):
    csv_data: str
    duration_seconds: Optional[float] = None
    transcript_text: Optional[str] = None

class ShortsExtractRequest(BaseModel):
    transcript_text: str
    max_shorts: Optional[int] = 3

class SeoGenerateRequest(BaseModel):
    title: str
    topic: str
    chapters: Optional[str] = ""
    links: Optional[str] = ""

class CommentTriageRequest(BaseModel):
    comments: List[Dict[str, str]]  # [{"author": "...", "text": "..."}]

class ViralSwipeRequest(BaseModel):
    videos: List[Dict[str, Any]]
    min_multiplier: Optional[float] = 1.5

class WeeklyPlanRequest(BaseModel):
    hours_available: int
    niche: str

class ChannelAuditRequest(BaseModel):
    channel_name: str
    subscribers: int
    avg_views_last_10: int
    top_video_views: int
    upload_frequency_per_week: float
    retention_30s_pct: Optional[float] = None

class VoiceProfileUpdate(BaseModel):
    content: str


# ----------------- Voice Profile Helper -----------------

def get_voice_profile_path() -> Path:
    local_voice = BASE_DIR / "voice.md"
    if local_voice.exists():
        return local_voice
    tmpl_voice = TEMPLATES_DIR / "voice.md"
    if tmpl_voice.exists():
        return tmpl_voice
    return local_voice

def load_voice_profile() -> str:
    path = get_voice_profile_path()
    if path.exists():
        return path.read_text(encoding="utf-8")
    return (
        "# Voice Profile\n\n"
        "## Who I Talk To\nSmart, pragmatic creators and builders.\n\n"
        "## Tone\nDirect, clear, punchy, zero fluff, evidence-backed.\n\n"
        "## Words I Never Say\n'Game changer', 'Mind blowing', 'Subscribe now', 'Before we get started'.\n"
    )

def save_voice_profile(content: str):
    path = BASE_DIR / "voice.md"
    path.write_text(content, encoding="utf-8")


# ----------------- Core API Endpoints -----------------

@app.get("/api/health")
def health_check():
    return {"status": "ok", "app": "YouTube Agent Studio", "version": "1.0.0"}

@app.get("/api/voice")
def get_voice():
    return {"content": load_voice_profile()}

@app.post("/api/voice")
def update_voice(req: VoiceProfileUpdate):
    save_voice_profile(req.content)
    return {"status": "updated", "length": len(req.content)}

@app.get("/api/formulas")
def get_formulas():
    formulas_path = SKILLS_DIR / "yt-script" / "hooks.json"
    if formulas_path.exists():
        with open(formulas_path, encoding="utf-8") as f:
            data = json.load(f)
        return data
    return {"hooks": []}

@app.post("/api/hook/score")
def score_single_hook(req: HookScoreRequest):
    hook = req.hook.strip()
    if not hook:
        raise HTTPException(status_code=400, detail="Hook cannot be empty")
    parts, verdict, name, hits = hookscore.score(hook)
    lowest_prop = min(parts, key=parts.get)
    fix_tip = hookscore.FIX.get(lowest_prop, "Refine the wording for clarity and punch")
    
    return {
        "hook": hook,
        "score": verdict,
        "band": hookscore.band(verdict),
        "formula": name,
        "formula_hits": hits,
        "properties": parts,
        "weakest_property": lowest_prop,
        "fix_tip": fix_tip,
        "words_count": len(hookscore.words(hook))
    }

@app.post("/api/hook/batch-score")
def score_batch_hooks(req: HookBatchScoreRequest):
    results = []
    for h in req.hooks:
        h = h.strip()
        if not h:
            continue
        parts, verdict, name, hits = hookscore.score(h)
        lowest_prop = min(parts, key=parts.get)
        results.append({
            "hook": h,
            "score": verdict,
            "band": hookscore.band(verdict),
            "formula": name,
            "formula_hits": hits,
            "properties": parts,
            "weakest_property": lowest_prop,
            "fix_tip": hookscore.FIX.get(lowest_prop, ""),
            "words_count": len(hookscore.words(h))
        })
    results.sort(key=lambda x: -x["score"])
    return {"results": results}

@app.post("/api/hook/generate")
def generate_hooks(topic: str = Body(..., embed=True)):
    topic_clean = topic.strip()
    formulas_data = get_formulas().get("hooks", [])
    
    # Generate 5 diverse hooks mapped to formulas
    generated_hooks = [
        f"If you're still doing {topic_clean} in 2026, you are wasting at least 3 hours every single week.",
        f"I tested every method for {topic_clean} so you don't lose $5,000 making the exact same mistakes I did.",
        f"Why does nobody talk about the 1 rule that actually makes {topic_clean} work?",
        f"Stop doing {topic_clean} until you change this one setting.",
        f"90% of people fail at {topic_clean} because they start with step 3 instead of step 1."
    ]
    
    scored_hooks = []
    for h in generated_hooks:
        parts, verdict, name, hits = hookscore.score(h)
        lowest_prop = min(parts, key=parts.get)
        scored_hooks.append({
            "hook": h,
            "score": verdict,
            "band": hookscore.band(verdict),
            "formula": name,
            "formula_hits": hits,
            "properties": parts,
            "weakest_property": lowest_prop,
            "fix_tip": hookscore.FIX.get(lowest_prop, "")
        })
    
    scored_hooks.sort(key=lambda x: -x["score"])
    return {
        "topic": topic_clean,
        "hooks": scored_hooks,
        "best_hook": scored_hooks[0] if scored_hooks else None
    }

@app.post("/api/script/generate")
def generate_script(req: ScriptGenerateRequest):
    topic = req.topic.strip()
    voice = req.voice_profile or load_voice_profile()
    dur = req.target_duration_minutes or 8
    target_words = dur * 150
    
    # Pick or score hook
    hook_text = req.selected_hook
    if not hook_text:
        hooks_res = generate_hooks(topic=topic)
        hook_text = hooks_res["best_hook"]["hook"]
    
    parts, verdict, name, hits = hookscore.score(hook_text)
    
    script_beats = [
        {
            "timestamp": "0:00 - 0:15",
            "section": "1. THE HOOK",
            "visual": f"[ON SCREEN: High-contrast title card with bold text & fast B-roll highlighting '{topic}']",
            "spoken": hook_text,
            "retention_note": "Confirm the promise in under 15 seconds. No channel intro."
        },
        {
            "timestamp": "0:15 - 0:45",
            "section": "2. THE TURN",
            "visual": f"[ON SCREEN: Direct to camera talking head + side graphic showing 3 main milestones of {topic}]",
            "spoken": f"In this video, I'm going to walk you through the exact step-by-step breakdown of {topic}, so you can implement this immediately without the usual trial and error. Let's get straight into step one.",
            "retention_note": "State what the video will do in one clear sentence and start immediately."
        },
        {
            "timestamp": "0:45 - 2:30",
            "section": "3. THE FOUNDATION & CORE MISTAKE",
            "visual": "[ON SCREEN: Screen recording demonstration + highlight boxes showing the common error vs correct setup]",
            "spoken": f"The biggest mistake people make with {topic} is treating it like a one-off task. When you look under the hood, the entire workflow hinges on getting the initial parameters configured properly. Here is what that looks like in practice...",
            "retention_note": "Keep visual motion every 4-6 seconds with zooms, sound cues, or UI highlights."
        },
        {
            "timestamp": "2:30 - 5:00",
            "section": "4. THE ACTIONABLE STEP-BY-STEP PLAYBOOK",
            "visual": "[ON SCREEN: Animated numbered checklist (1, 2, 3) + practical live walkthrough on screen]",
            "spoken": f"Here is the 3-step playbook that makes this repeatable. Step 1: establish the baseline metrics. Step 2: automate the repetitive scoring and linting. Step 3: review the output before shipping.",
            "retention_note": "Deliver high-density practical value without filler words."
        },
        {
            "timestamp": "5:00 - 7:00",
            "section": "5. THE PAYOFF & PROOF",
            "visual": "[ON SCREEN: Split-screen Before & After data / real comparison dashboard with clear proof metrics]",
            "spoken": f"And here is the payoff: once this is active, your output quality doubles while cutting your production time in half. That is the exact workflow, and the full template is linked in the description below.",
            "retention_note": "Deliver the explicit payoff promised in the hook."
        },
        {
            "timestamp": "7:00 - 7:30",
            "section": "6. THE CLOSE",
            "visual": "[ON SCREEN: End screen card pointing to next recommended video + subscribe prompt]",
            "spoken": f"{req.call_to_action}. If you found this useful, watch this next video on your screen where we take this to the next level.",
            "retention_note": "One clear ask. Never give three competing calls to action."
        }
    ]
    
    total_words = sum(len(b["spoken"].split()) for b in script_beats)
    est_runtime_mins = round(total_words / 150, 1)
    
    # Enhance script beats with Gemini AI (image prompts, visual captions, motion direction)
    enhanced_beats = gemini_service.enhance_script_with_gemini(topic, script_beats)
    
    # Generate real AI image for each beat
    for idx, b in enumerate(enhanced_beats):
        img_prompt = b.get("image_prompt") or f"Cinematic scene for {topic}"
        img_filename = f"scene_{idx}_{abs(hash(img_prompt)) % 100000}.jpg"
        img_full_path = str(video_maker.IMAGES_DIR / img_filename)
        if not os.path.exists(img_full_path):
            video_maker.fetch_ai_scene_image(img_prompt, img_full_path)
        b["image_url"] = f"/renders/images/{img_filename}"
        b["image_filename"] = img_filename
    
    return {
        "topic": topic,
        "winning_hook": {
            "text": hook_text,
            "score": verdict,
            "band": hookscore.band(verdict),
            "formula": name,
            "properties": parts
        },
        "target_duration_minutes": dur,
        "estimated_duration_minutes": est_runtime_mins,
        "total_words": total_words,
        "words_per_minute": 150,
        "beats": enhanced_beats
    }

class ImageRegenerateRequest(BaseModel):
    prompt: str
    beat_index: Optional[int] = 0

@app.post("/api/script/regenerate-image")
def regenerate_beat_image(req: ImageRegenerateRequest):
    import time
    prompt = req.prompt.strip() or "Cinematic futuristic 8k"
    filename = f"scene_regen_{req.beat_index}_{int(time.time())}.jpg"
    full_path = str(video_maker.IMAGES_DIR / filename)
    video_maker.fetch_ai_scene_image(prompt, full_path)
    return {
        "status": "success",
        "image_url": f"/renders/images/{filename}",
        "prompt": prompt
    }

@app.post("/api/package/lint")
def lint_package(req: PackageLintRequest):
    title_str = req.title.strip()
    thumb_str = (req.thumbnail_text or "").strip()
    if not title_str:
        raise HTTPException(status_code=400, detail="Title cannot be empty")
    
    result = title_linter.check(title_str, thumb_str if thumb_str else None)
    
    # Truncation previews
    desktop_cut = title_str[:title_linter.DESKTOP] + ("..." if len(title_str) > title_linter.DESKTOP else "")
    mobile_head = title_str[:title_linter.MOBILE].rsplit(" ", 1)[0] + ("..." if len(title_str) > title_linter.MOBILE else "")
    
    return {
        "title": title_str,
        "thumbnail_text": thumb_str,
        "score": result["score"],
        "chars": result["chars"],
        "issues": [{"category": k, "message": m} for k, m in result["issues"]],
        "good": result["good"],
        "previews": {
            "desktop_preview": desktop_cut,
            "mobile_preview": mobile_head,
            "thumbnail_words_count": len(title_linter.words(thumb_str)) if thumb_str else 0
        }
    }

@app.post("/api/package/generate")
def generate_packages(req: PackageGenerateRequest):
    topic = req.topic.strip()
    
    # Curate high-performing title + thumbnail pairings
    candidates = [
        {"title": f"Why 90% of {topic} Fails (And How to Fix It)", "thumb": "THE 1 FIX"},
        {"title": f"The $0 Setup for {topic} in 2026", "thumb": "FREE SETUP"},
        {"title": f"Stop Doing {topic} Like This (3 Big Mistakes)", "thumb": "DON'T DO THIS"},
        {"title": f"How I Automated {topic} in Under 20 Minutes", "thumb": "20 MIN WORKFLOW"},
        {"title": f"{topic}: 5 Rules Nobody Tells You", "thumb": "THE 5 RULES"}
    ]
    
    linted = []
    for c in candidates:
        res = title_linter.check(c["title"], c["thumb"])
        linted.append({
            "title": c["title"],
            "thumb": c["thumb"],
            "score": res["score"],
            "chars": res["chars"],
            "issues": [{"category": k, "message": m} for k, m in res["issues"]],
            "good": res["good"]
        })
    
    linted.sort(key=lambda x: -x["score"])
    return {"packages": linted, "topic": topic}

@app.post("/api/edit/deadair")
def process_deadair(req: DeadAirRequest):
    raw_text = req.transcript_text.strip()
    if not raw_text:
        raise HTTPException(status_code=400, detail="Transcript text cannot be empty")
    
    # Write temp file to parse with deadair
    temp_path = BASE_DIR / "temp_transcript.srt"
    try:
        temp_path.write_text(raw_text, encoding="utf-8")
        cues = deadair.load(str(temp_path))
        if not cues:
            # Check if it was plain text or needs auto-cues
            raise HTTPException(status_code=400, detail="No cues found. Please provide valid SRT, VTT, or Whisper JSON timestamped transcripts.")
        
        dur = cues[-1][1]
        floor = req.floor or 0.45
        cuts = []
        
        for i, (s, e, t) in enumerate(cues):
            if deadair.FILLER_ONLY.match(t):
                cuts.append({"kind": "FILLER", "start": round(s, 2), "end": round(e, 2), "why": t.strip()[:48]})
            if i:
                gap = s - cues[i - 1][1]
                if gap > floor:
                    keep = floor / 2
                    cuts.append({"kind": "DEAD", "start": round(cues[i - 1][1] + keep, 3),
                                 "end": round(s - keep, 3), "why": f"{gap:.2f}s gap"})
            if t.strip() and not deadair.FILLER_ONLY.match(t):
                j = i - 1
                while j >= 0 and (deadair.FILLER_ONLY.match(cues[j][2]) or not cues[j][2].strip()):
                    j -= 1
                if j >= 0:
                    a1, b1 = deadair.norm(cues[j][2])[:5], deadair.norm(t)[:5]
                    if len(a1) >= 3 and a1 == b1:
                        cuts.append({"kind": "REPEAT", "start": round(cues[j][0], 2), "end": round(cues[j][1], 2),
                                     "why": f'restart of "{" ".join(a1)}"'})
        
        cuts = [c for c in cuts if c["end"] > c["start"]]
        cuts.sort(key=lambda c: c["start"])
        removed = sum(c["end"] - c["start"] for c in cuts)
        final_dur = max(0, dur - removed)
        
        return {
            "duration": round(dur, 2),
            "cues_count": len(cues),
            "floor": floor,
            "cuts_count": len(cuts),
            "removed_seconds": round(removed, 2),
            "final_duration": round(final_dur, 2),
            "time_saved_percent": round((removed / dur * 100) if dur else 0, 1),
            "cuts": cuts
        }
    finally:
        if temp_path.exists():
            temp_path.unlink()

@app.post("/api/chapters/generate")
def generate_chapters(req: ChaptersRequest):
    raw_text = req.transcript_text.strip()
    if not raw_text:
        raise HTTPException(status_code=400, detail="Transcript text cannot be empty")
    
    temp_path = BASE_DIR / "temp_chapters.srt"
    try:
        temp_path.write_text(raw_text, encoding="utf-8")
        cues = deadair.load(str(temp_path))
        if len(cues) < 6:
            raise HTTPException(status_code=400, detail="Too few transcript cues to generate chapters (minimum 6 required).")
        
        dur = cues[-1][1]
        target = req.target_chapters or 7
        cand = []
        for i in range(1, len(cues)):
            gap = cues[i][0] - cues[i - 1][1]
            before = " ".join(c[2] for c in cues[max(0, i - 12):i])
            after = " ".join(c[2] for c in cues[i:i + 12])
            kb, ka = chapter_mod.keywords(before), chapter_mod.keywords(after)
            shift = 1 - (len(kb & ka) / len(kb | ka)) if (kb | ka) else 0
            cand.append((gap * 1.6 + shift * 3.2, cues[i][0], i))
        cand.sort(reverse=True)
        picked, MIN = [0.0], 10.0
        for _, t, i in cand:
            if len(picked) >= target:
                break
            if all(abs(t - p) >= MIN for p in picked) and dur - t >= MIN:
                picked.append(t)
        picked.sort()
        chapters_list = []
        for n, t in enumerate(picked):
            end = picked[n + 1] if n + 1 < len(picked) else dur
            text = " ".join(c[2] for c in cues if c[0] >= t and c[1] <= end)
            kw = [w for w in chapter_mod.keywords(text)]
            kw.sort(key=lambda w: -text.lower().count(w))
            title_text = " ".join(w.capitalize() for w in kw[:3]) or "Introduction"
            if n == 0 and t == 0:
                title_text = "Introduction & Overview"
            chapters_list.append({
                "start": round(t, 2),
                "label": chapter_mod.mmss(t),
                "title": title_text,
                "seconds": round(end - t, 2)
            })
        
        is_valid = len(chapters_list) >= 3 and chapters_list[0]["start"] == 0 and all(c["seconds"] >= MIN for c in chapters_list)
        formatted_block = "\n".join(f"{c['label']} {c['title']}" for c in chapters_list)
        
        return {
            "valid": is_valid,
            "total_chapters": len(chapters_list),
            "formatted_text": formatted_block,
            "chapters": chapters_list,
            "rules_checked": {
                "starts_at_zero": chapters_list[0]["start"] == 0,
                "min_three_chapters": len(chapters_list) >= 3,
                "min_ten_seconds_each": all(c["seconds"] >= 10 for c in chapters_list)
            }
        }
    finally:
        if temp_path.exists():
            temp_path.unlink()

@app.post("/api/retention/analyze")
def analyze_retention(req: RetentionAnalyzeRequest):
    csv_raw = req.csv_data.strip()
    if not csv_raw:
        raise HTTPException(status_code=400, detail="Retention CSV data cannot be empty")
    
    rows = []
    for r in csv.reader(io.StringIO(csv_raw)):
        nums = []
        for c in r:
            c = c.strip().replace("%", "").replace(",", "")
            try:
                nums.append(float(c))
            except ValueError:
                pass
        vals = [n for n in nums if n is not None]
        if len(vals) >= 2:
            rows.append((vals[0], vals[1]))
    
    if len(rows) < 8:
        raise HTTPException(status_code=400, detail="Could not parse at least 8 valid retention data points from CSV.")
    
    xs = [r[0] for r in rows]
    ys = [r[1] for r in rows]
    pct_axis = max(xs) <= 100.5
    dur = req.duration_seconds
    
    def at(x):
        return (x / 100.0 * dur) if (pct_axis and dur) else x
    
    start = ys[0] or 100.0
    cutoff = 30.0 if not pct_axis else (30.0 / dur * 100 if dur else 10.0)
    hook_end = min((y for x, y in rows if x <= cutoff), default=start)
    hook_leak = start - hook_end
    
    drops = []
    for i in range(1, len(rows)):
        d = ys[i - 1] - ys[i]
        span = xs[i] - xs[i - 1] or 1
        drops.append((d / span, xs[i - 1], xs[i], d))
    drops.sort(reverse=True)
    
    cliffs = [
        {
            "from": round(a1, 2),
            "to": round(b1, 2),
            "lost": round(d, 2),
            "at_seconds": round(at(a1), 1) if (not pct_axis or dur) else None
        }
        for _, a1, b1, d in drops[:5] if d > 0.8
    ]
    
    mid = [d for d, x0, _, _ in [(r[0], r[1], r[2], r[3]) for r in drops] if x0 > cutoff]
    slide = sum(mid) / len(mid) if mid else 0
    
    verdict = "healthy" if hook_leak < 25 else "leaking" if hook_leak < 40 else "severe"
    
    return {
        "points_count": len(rows),
        "start_pct": start,
        "end_pct": ys[-1],
        "hook_leak_pct": round(hook_leak, 2),
        "hook_verdict": verdict,
        "hook_advice": "Under 25% is healthy. Above 35% means the opening 15s made viewers click away before the promise was confirmed.",
        "cliffs": cliffs,
        "slide_rate": round(slide, 3),
        "slide_advice": "A steady slide is pacing/fluff. Cut the middle beats rather than rewriting the core concept.",
        "curve_data": [{"x": round(r[0], 2), "y": round(r[1], 2)} for r in rows]
    }

@app.post("/api/shorts/extract")
def extract_shorts(req: ShortsExtractRequest):
    raw_text = req.transcript_text.strip()
    if not raw_text:
        raise HTTPException(status_code=400, detail="Transcript text cannot be empty")
    
    temp_path = BASE_DIR / "temp_shorts.srt"
    try:
        temp_path.write_text(raw_text, encoding="utf-8")
        cues = deadair.load(str(temp_path))
        if len(cues) < 5:
            raise HTTPException(status_code=400, detail="Transcript too short to extract Shorts.")
        
        total_dur = cues[-1][1]
        shorts_list = []
        
        # Segment long video into 30-55s high-energy clips
        step = max(30.0, total_dur / (req.max_shorts or 3))
        for i in range(min(req.max_shorts or 3, int(total_dur // 30) or 1)):
            start_t = i * step
            end_t = min(total_dur, start_t + 45.0)
            clip_cues = [c for c in cues if c[0] >= start_t and c[1] <= end_t]
            clip_text = " ".join(c[2] for c in clip_cues)
            if not clip_text:
                continue
            
            # Generate sharp Short hook
            first_words = clip_text.split()[:8]
            short_hook = f"Here's why most people get this wrong: {' '.join(first_words)}..."
            
            shorts_list.append({
                "short_id": i + 1,
                "timecode": f"{chapter_mod.mmss(start_t)} - {chapter_mod.mmss(end_t)}",
                "duration_seconds": round(end_t - start_t, 1),
                "generated_hook": short_hook,
                "core_quote": clip_text[:280] + ("..." if len(clip_text) > 280 else ""),
                "edit_direction": "Vertical 9:16 crop, bold animated captions, zoom on key punchline, SFX swoosh on hook."
            })
            
        return {"shorts": shorts_list, "total_extracted": len(shorts_list)}
    finally:
        if temp_path.exists():
            temp_path.unlink()

@app.post("/api/seo/generate")
def generate_seo(req: SeoGenerateRequest):
    title = req.title.strip()
    topic = req.topic.strip()
    
    # 3 High-intent search queries
    queries = [
        f"how to {topic} step by step",
        f"best workflow for {topic} 2026",
        f"{topic} tutorial for beginners"
    ]
    
    description = (
        f"In this video, we break down {topic} with a complete step-by-step practical guide. "
        f"Whether you're starting from scratch or looking to optimize your existing workflow, "
        f"these strategies will save you hours.\n\n"
        f"📌 Target Topics Covered:\n"
        f"• The core mechanics of {topic}\n"
        f"• The 3 biggest pitfalls to avoid\n"
        f"• Full actionable walkthrough & implementation\n\n"
        + (f"⏱️ Timestamps & Chapters:\n{req.chapters}\n\n" if req.chapters else "")
        + (f"🔗 Resources & Links Mentioned:\n{req.links}\n\n" if req.links else "🔗 Resources & Links:\n• Get the templates & guides: https://example.com/resources\n\n")
        + f"💬 Let me know your thoughts or questions in the comments below!\n\n"
        f"#YouTubeAutomation #CreatorWorkflow #{''.join(w.capitalize() for w in topic.split()[:2])}"
    )
    
    tags = [
        topic.lower(),
        f"{topic.lower()} tutorial",
        f"how to do {topic.lower()}",
        f"{topic.lower()} guide",
        "youtube workflow",
        "creator tools",
        "productivity"
    ]
    
    return {
        "title": title,
        "description": description,
        "target_queries": queries,
        "tags": tags,
        "tags_string": ", ".join(tags)
    }

@app.post("/api/comments/triage")
def triage_comments(req: CommentTriageRequest):
    voice = load_voice_profile()
    
    piles = {
        "superfans": [],
        "questions": [],
        "critiques": [],
        "noise": []
    }
    
    for item in req.comments:
        author = item.get("author", "Viewer")
        text = item.get("text", "").strip()
        t_low = text.lower()
        
        reply = ""
        category = "noise"
        
        if "?" in text or any(w in t_low for w in ["how", "what", "where", "why", "when", "can you"]):
            category = "questions"
            reply = f"Great question, {author}! In short, the key is to test step 1 first before scaling. Appreciate you asking!"
        elif any(w in t_low for w in ["love", "fire", "goat", "helpful", "gem", "awesome", "best video", "thank"]):
            category = "superfans"
            reply = f"Thank you so much {author}! Glad this breakdown hit the mark. More deep-dives coming next week!"
        elif any(w in t_low for w in ["disagree", "wrong", "fake", "bad", "waste", "clickbait", "terrible", "cap"]):
            category = "critiques"
            reply = f"Appreciate the pushback, {author}. The data shows this works for 80%+ of cases, but edge cases do exist. Thanks for keeping it sharp!"
        else:
            category = "noise"
            reply = f"Thanks for watching and commenting, {author}!"
            
        piles[category].append({
            "author": author,
            "comment": text,
            "category": category,
            "suggested_reply": reply
        })
        
    # Pick pinned comment candidate
    pin_candidate = None
    if piles["questions"]:
        pin_candidate = {
            "author": piles["questions"][0]["author"],
            "comment": piles["questions"][0]["comment"],
            "reason": "Answers a high-value community question that clarifies the main video takeaway."
        }
    elif piles["superfans"]:
        pin_candidate = {
            "author": piles["superfans"][0]["author"],
            "comment": piles["superfans"][0]["comment"],
            "reason": "High-energy positive review to set the tone of the comment section."
        }
        
    return {
        "summary": {
            "total": len(req.comments),
            "superfans": len(piles["superfans"]),
            "questions": len(piles["questions"]),
            "critiques": len(piles["critiques"]),
            "noise": len(piles["noise"])
        },
        "piles": piles,
        "recommended_pinned_comment": pin_candidate
    }

@app.post("/api/viral/swipe")
def analyze_viral_swipe(req: ViralSwipeRequest):
    lo = req.min_multiplier or 1.5
    by = {}
    for v in req.videos:
        by.setdefault(v.get("channel", "?"), []).append(v)
    
    out, thin = [], []
    for ch, vids in by.items():
        views = [float(v.get("views", 0) or 0) for v in vids]
        med = statistics.median(views) if views else 0
        if len(vids) < 4:
            thin.append({"channel": ch, "count": len(vids)})
            continue
        for v in vids:
            m = (float(v.get("views", 0) or 0) / med) if med else 0
            out.append({
                "channel": ch,
                "title": v.get("title", ""),
                "views": int(v.get("views", 0) or 0),
                "median": int(med),
                "multiple": round(m, 2),
                "formula": swipe_mod.classify(v.get("title", "")),
                "url": v.get("url", "")
            })
            
    out = [r for r in out if r["multiple"] >= lo]
    out.sort(key=lambda r: -r["multiple"])
    
    counts = {}
    for r in out:
        counts[r["formula"]] = counts.get(r["formula"], 0) + 1
        
    return {
        "total_analyzed": len(req.videos),
        "total_channels": len(by),
        "min_multiplier": lo,
        "outliers": out,
        "skipped_thin_channels": thin,
        "formula_distribution": counts
    }

@app.post("/api/plan/weekly")
def generate_weekly_plan(req: WeeklyPlanRequest):
    hrs = req.hours_available
    niche = req.niche
    
    if hrs < 5:
        tier = "Micro Schedule (< 5h)"
        anchor_hrs = 2.5
        cheap_hrs = 1.0
        shorts_hrs = 1.5
    elif hrs <= 12:
        tier = "Standard Creator Schedule (5-12h)"
        anchor_hrs = 5.0
        cheap_hrs = 2.5
        shorts_hrs = 3.0
    else:
        tier = "Full-Throttle Schedule (15h+)"
        anchor_hrs = 9.0
        cheap_hrs = 4.0
        shorts_hrs = 4.0
        
    schedule = {
        "tier": tier,
        "total_hours": hrs,
        "niche": niche,
        "deliverables": [
            {
                "type": "1. Anchor Video (Deep-Dive)",
                "hours_allocated": anchor_hrs,
                "format": "Long-form (8-14 mins)",
                "strategy": f"Flagship research-backed guide on {niche}. Invest in the first 15s hook and packaging.",
                "days": "Mon - Wed"
            },
            {
                "type": "2. Cheap / Fast Reaction Video",
                "hours_allocated": cheap_hrs,
                "format": "Medium-form (5-7 mins)",
                "strategy": f"Quick breakdown of a recent trend or case study in {niche}. Minimal edit, raw take.",
                "days": "Thursday"
            },
            {
                "type": "3. Three Shorts (Repurposed)",
                "hours_allocated": shorts_hrs,
                "format": "Shorts (30-50s each)",
                "strategy": "Extract 3 punchy highlights directly from Anchor video with newly recorded opening hooks.",
                "days": "Tue / Thu / Sat"
            }
        ]
    }
    return schedule

@app.post("/api/audit/channel")
def audit_channel(req: ChannelAuditRequest):
    ratio = (req.avg_views_last_10 / req.subscribers) if req.subscribers else 0
    spike_multiple = (req.top_video_views / req.avg_views_last_10) if req.avg_views_last_10 else 1
    
    # Identify the SINGLE highest-leverage bottleneck
    if req.retention_30s_pct and req.retention_30s_pct < 60:
        bottleneck = "0:30 Hook Leak"
        prescription = "Your first 15 seconds are leaking viewers before the payoff. Eliminate channel intros and open with a specific high-stakes promise."
    elif ratio < 0.05:
        bottleneck = "Packaging & Click-Through Failure"
        prescription = "Your subscriber base is not clicking. Title and thumbnail are repeating each other or vague. Fix packaging pairings before recording more videos."
    elif spike_multiple > 8.0:
        bottleneck = "Unreplicated Outlier Concept"
        prescription = f"Your top video scored {spike_multiple:.1f}x your median views. Build a 3-part series iterating on that exact topic and hook formula immediately."
    elif req.upload_frequency_per_week < 1:
        bottleneck = "Cadence & Momentum"
        prescription = "Consistency is too low to compound algorithm memory. Shift to 1 Anchor + 1 Fast Video + 3 Shorts per week using the Weekly Plan."
    else:
        bottleneck = "Pacing & Mid-Video Retention"
        prescription = "Your audience is steady but bleeding in the middle. Cut dead air to <0.35s and insert on-screen visual shifts every 6 seconds."
        
    return {
        "channel_name": req.channel_name,
        "views_to_sub_ratio": f"{ratio * 100:.1f}%",
        "outlier_multiple": f"{spike_multiple:.1f}x",
        "single_critical_fix": {
            "bottleneck": bottleneck,
            "prescription": prescription
        }
    }

@app.post("/api/video/render")
def render_ai_video(req: VideoRenderRequest):
    import time
    filename = f"video_{int(time.time())}.mp4"
    result = video_maker.create_video_from_beats(
        title=req.title,
        beats=req.beats,
        output_filename=filename,
        voice_key=req.voice_key or "guy"
    )
    return result

class CodeExchangeRequest(BaseModel):
    code: str

@app.get("/api/youtube/status")
def get_youtube_status():
    return youtube_uploader.check_youtube_connection()

@app.get("/api/youtube/auth-url")
def get_youtube_auth_url():
    try:
        url = youtube_uploader.get_auth_url()
        return {"auth_url": url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/youtube/exchange-code")
def exchange_youtube_code(req: CodeExchangeRequest):
    try:
        res = youtube_uploader.exchange_auth_code(req.code)
        return res
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Code exchange failed: {str(e)}")

@app.post("/api/youtube/upload")
def upload_to_youtube(req: YouTubeUploadRequest):
    # If no specific path given, find the most recent render
    video_path = req.video_path
    if not video_path or not os.path.exists(video_path):
        renders = list((PUBLIC_DIR / "renders").glob("*.mp4"))
        if renders:
            renders.sort(key=lambda p: p.stat().st_mtime, reverse=True)
            video_path = str(renders[0])
        else:
            raise HTTPException(status_code=400, detail="No rendered video found to upload. Please generate an AI video first.")

    res = youtube_uploader.upload_video_to_youtube(
        video_file_path=video_path,
        title=req.title,
        description=req.description,
        tags=req.tags,
        privacy_status=req.privacy_status or "private",
        category_id=req.category_id or "28"
    )
    return res

# Serve static rendered video files
app.mount("/renders", StaticFiles(directory=str(PUBLIC_DIR / "renders")), name="renders")

# Serve static frontend files
app.mount("/", StaticFiles(directory=str(PUBLIC_DIR), html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

