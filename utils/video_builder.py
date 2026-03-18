"""
Video Builder v3 - MoviePy v2 compatible
- Real Pexels video clips
- gTTS narration audio
- Themed text overlays using PIL (no ImageMagick needed)
- Progress bar, title card, section overlays
"""
import os, requests, tempfile, time, textwrap
from pathlib import Path


def _get_pexels_key():
    try:
        import streamlit as st
        k = st.secrets.get("PEXELS_API_KEY", "")
        if k: return k
    except Exception:
        pass
    return os.environ.get("PEXELS_API_KEY", "")


def _moviepy_ver():
    import moviepy
    return int(getattr(moviepy, "__version__", "1").split(".")[0])


# ─── PIL text image (no ImageMagick needed) ──────────────────────

def _text_image(text, width=1280, height=120, font_size=40,
                text_color=(255,255,255), bg_color=None,
                bold=False, align="center"):
    """Render text to a PIL image, return as numpy array."""
    from PIL import Image, ImageDraw, ImageFont
    import numpy as np

    text = str(text).strip()
    if not text:
        arr = np.zeros((height, width, 4), dtype=np.uint8)
        return arr

    # Try to load a real font
    font = None
    font_paths = [
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for fp in font_paths:
        if os.path.exists(fp):
            try:
                font = ImageFont.truetype(fp, font_size)
                break
            except Exception:
                continue
    if font is None:
        font = ImageFont.load_default()

    # Wrap text
    chars_per_line = max(20, int(width / (font_size * 0.55)))
    wrapped = "\n".join(textwrap.wrap(text, width=chars_per_line))

    # Measure
    dummy = Image.new("RGBA", (1, 1))
    draw  = ImageDraw.Draw(dummy)
    bbox  = draw.multiline_textbbox((0,0), wrapped, font=font, spacing=8)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]

    img_w = width
    img_h = th + 30

    img = Image.new("RGBA", (img_w, img_h),
                    bg_color if bg_color else (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    x = (img_w - tw) // 2 if align == "center" else 20
    y = 12

    # Shadow
    draw.multiline_text((x+2, y+2), wrapped, font=font,
                        fill=(0,0,0,160), spacing=8, align=align)
    # Main text
    draw.multiline_text((x, y), wrapped, font=font,
                        fill=(*text_color, 255), spacing=8, align=align)

    return np.array(img)


def _make_image_clip(arr, duration, ver):
    """Wrap numpy RGBA array as an ImageClip."""
    if ver >= 2:
        from moviepy import ImageClip
    else:
        from moviepy.editor import ImageClip
    clip = ImageClip(arr)
    if ver >= 2:
        return clip.with_duration(duration)
    else:
        return clip.set_duration(duration)


def _set(clip, pos=None, dur=None, ver=1):
    if ver >= 2:
        if pos is not None: clip = clip.with_position(pos)
        if dur is not None: clip = clip.with_duration(dur)
    else:
        if pos is not None: clip = clip.set_position(pos)
        if dur is not None: clip = clip.set_duration(dur)
    return clip


# ─── TTS audio ───────────────────────────────────────────────────

def _make_audio(text, path, lang="en"):
    """Generate narration MP3 using gTTS."""
    try:
        from gtts import gTTS
        tts = gTTS(text=text[:500], lang=lang, slow=False)
        tts.save(path)
        return True
    except Exception as e:
        print(f"TTS error: {e}")
        return False


# ─── Pexels ──────────────────────────────────────────────────────

def fetch_video_clip(query, duration_needed=10):
    api_key = _get_pexels_key()
    if not api_key:
        return None
    headers = {"Authorization": api_key}
    fallbacks = [" ".join(str(query).split()[:5]), "nature landscape", "city aerial", "abstract background"]
    for q in fallbacks:
        try:
            r = requests.get(
                "https://api.pexels.com/videos/search",
                headers=headers,
                params={"query": q, "per_page": 5, "orientation": "landscape"},
                timeout=15,
            )
            if r.status_code != 200:
                continue
            videos = r.json().get("videos", [])
            if not videos:
                continue
            best = next((v for v in videos if v.get("duration", 0) >= duration_needed), videos[0])
            mp4s = [f for f in best.get("video_files", []) if f.get("file_type") == "video/mp4"]
            if mp4s:
                mp4s.sort(key=lambda x: x.get("width", 9999))
                return mp4s[0].get("link")
        except Exception as e:
            print(f"Pexels error for '{q}': {e}")
    return None


def download_clip(url, dest):
    try:
        r = requests.get(url, stream=True, timeout=60)
        with open(dest, "wb") as f:
            for chunk in r.iter_content(8192):
                f.write(chunk)
        return True
    except Exception as e:
        print(f"Download error: {e}")
        return False


# ─── Overlays ────────────────────────────────────────────────────

def _section_overlay(base_clip, sec, dur, ver):
    """Add themed title + subtitle text overlay to a clip using PIL."""
    try:
        if ver >= 2:
            from moviepy import CompositeVideoClip
        else:
            from moviepy.editor import CompositeVideoClip

        layers = [base_clip]

        # Semi-transparent dark bar at top
        import numpy as np
        bar_h = 70
        bar = np.zeros((bar_h, 1280, 4), dtype=np.uint8)
        bar[:, :, 3] = 160  # alpha
        bar_clip = _set(_make_image_clip(bar, dur, ver), pos=(0, 0), ver=ver)
        layers.append(bar_clip)

        # Section title
        title_arr = _text_image(
            sec.get("name", ""), width=1280,
            font_size=36, text_color=(255, 107, 53), bold=True
        )
        title_clip = _set(_make_image_clip(title_arr, dur, ver), pos=(0, 8), ver=ver)
        layers.append(title_clip)

        # Bottom subtitle bar
        narration = sec.get("narration", "")
        preview = narration[:100] + "..." if len(narration) > 100 else narration

        bot_bar = np.zeros((90, 1280, 4), dtype=np.uint8)
        bot_bar[:, :, 3] = 180
        bot_clip = _set(_make_image_clip(bot_bar, dur, ver), pos=(0, 630), ver=ver)
        layers.append(bot_clip)

        sub_arr = _text_image(
            preview, width=1240,
            font_size=22, text_color=(220, 220, 220)
        )
        sub_clip = _set(_make_image_clip(sub_arr, dur, ver), pos=(20, 640), ver=ver)
        layers.append(sub_clip)

        return CompositeVideoClip(layers)
    except Exception as e:
        print(f"Overlay error: {e}")
        return base_clip


def _title_card_clip(title, hook, ColorClip, ver, dur=4):
    """Opening title card with gradient-style dark background."""
    try:
        import numpy as np
        if ver >= 2:
            from moviepy import CompositeVideoClip, ImageClip
        else:
            from moviepy.editor import CompositeVideoClip, ImageClip

        # Gradient background
        bg = np.zeros((720, 1280, 3), dtype=np.uint8)
        for y in range(720):
            t = y / 720
            bg[y, :] = [
                int(8  + t * 20),
                int(11 + t * 15),
                int(20 + t * 30),
            ]
        if ver >= 2:
            bg_clip = ImageClip(bg).with_duration(dur)
        else:
            bg_clip = ImageClip(bg).set_duration(dur)

        layers = [bg_clip]

        # Orange accent bar
        bar = np.zeros((6, 1280, 4), dtype=np.uint8)
        bar[:, :, 0] = 255; bar[:, :, 1] = 107; bar[:, :, 2] = 53; bar[:, :, 3] = 255
        bar_clip = _set(_make_image_clip(bar, dur, ver), pos=(0, 240), ver=ver)
        layers.append(bar_clip)

        # Main title
        title_arr = _text_image(
            title, width=1200,
            font_size=58, text_color=(255, 107, 53), bold=True
        )
        h = title_arr.shape[0]
        title_clip = _set(_make_image_clip(title_arr, dur, ver), pos=(40, 260), ver=ver)
        layers.append(title_clip)

        # Hook subtitle
        if hook:
            hook_arr = _text_image(
                hook[:120], width=1100,
                font_size=28, text_color=(180, 180, 180)
            )
            hook_clip = _set(_make_image_clip(hook_arr, dur, ver), pos=(40, 380), ver=ver)
            layers.append(hook_clip)

        # "CineAI" watermark
        wm_arr = _text_image("🎬 CineAI", width=300, font_size=22, text_color=(100,100,100))
        wm_clip = _set(_make_image_clip(wm_arr, dur, ver), pos=(20, 680), ver=ver)
        layers.append(wm_clip)

        return CompositeVideoClip(layers)

    except Exception as e:
        print(f"Title card error: {e}")
        if ver >= 2:
            return ColorClip(size=(1280, 720), color=(8, 11, 20)).with_duration(dur)
        return ColorClip(size=(1280, 720), color=(8, 11, 20), duration=dur)


def _placeholder_clip(name, dur, ColorClip, ver):
    """Dark themed placeholder when no Pexels clip available."""
    try:
        import numpy as np
        if ver >= 2:
            from moviepy import CompositeVideoClip, ImageClip
        else:
            from moviepy.editor import CompositeVideoClip, ImageClip

        bg = np.zeros((720, 1280, 3), dtype=np.uint8)
        bg[:, :] = [13, 18, 33]

        # Grid lines for visual interest
        for x in range(0, 1280, 80): bg[:, x] = [25, 35, 55]
        for y in range(0, 720, 80):  bg[y, :] = [25, 35, 55]

        if ver >= 2:
            bg_clip = ImageClip(bg).with_duration(dur)
        else:
            bg_clip = ImageClip(bg).set_duration(dur)

        txt_arr = _text_image(name, width=1000, font_size=48, text_color=(255,107,53), bold=True)
        txt_clip = _set(_make_image_clip(txt_arr, dur, ver), pos=("center", 310), ver=ver)

        return CompositeVideoClip([bg_clip, txt_clip])
    except Exception:
        if ver >= 2:
            return ColorClip(size=(1280,720), color=(13,18,33)).with_duration(dur)
        return ColorClip(size=(1280,720), color=(13,18,33), duration=dur)


# ─── Main builder ─────────────────────────────────────────────────

def build_video(script, output_path, on_progress=None):
    try:
        import moviepy
        ver = int(getattr(moviepy, "__version__", "1").split(".")[0])
    except ImportError:
        return None, "moviepy not installed. Run: pip install moviepy"

    try:
        if ver >= 2:
            from moviepy import (VideoFileClip, CompositeVideoClip,
                                  concatenate_videoclips, ColorClip, AudioFileClip)
        else:
            from moviepy.editor import (VideoFileClip, CompositeVideoClip,
                                         concatenate_videoclips, ColorClip, AudioFileClip)
    except Exception as e:
        return None, f"MoviePy import error: {e}"

    sections = script.get("sections", [])
    if not sections:
        return None, "No sections in script."

    tmp = tempfile.mkdtemp()
    clips = []
    total = len(sections)

    def prog(i, msg):
        if on_progress: on_progress(i, total, msg)

    for i, sec in enumerate(sections):
        prog(i, f"Fetching clip {i+1}/{total}: {sec.get('name','')}")
        dur = min(int(sec.get("duration_seconds", 15)), 25)
        query = sec.get("b_roll") or sec.get("visual_description") or sec.get("name","nature")

        clip_path = os.path.join(tmp, f"clip_{i}.mp4")
        url = fetch_video_clip(query, duration_needed=dur)

        base = None
        if url and download_clip(url, clip_path):
            try:
                vc = VideoFileClip(clip_path)
                actual_dur = min(dur, vc.duration)
                if ver >= 2:
                    base = vc.with_subclip(0, actual_dur).resized((1280, 720))
                else:
                    base = vc.subclip(0, actual_dur).resize((1280, 720))
                dur = actual_dur  # use real duration
            except Exception as e:
                print(f"Clip load error: {e}")
                base = None

        if base is None:
            base = _placeholder_clip(sec.get("name","Scene"), dur, ColorClip, ver)

        # Text overlay
        composed = _section_overlay(base, sec, dur, ver)

        # TTS audio
        narration = sec.get("narration", "")
        if narration:
            audio_path = os.path.join(tmp, f"audio_{i}.mp3")
            if _make_audio(narration, audio_path):
                try:
                    audio = AudioFileClip(audio_path)
                    audio_dur = min(audio.duration, dur)
                    if ver >= 2:
                        audio = audio.with_duration(audio_dur)
                        composed = composed.with_audio(audio)
                    else:
                        audio = audio.set_duration(audio_dur)
                        composed = composed.set_audio(audio)
                except Exception as e:
                    print(f"Audio attach error: {e}")

        clips.append(composed)
        prog(i + 1, f"✅ Clip {i+1}/{total} ready")

    prog(total, "Building title card...")
    hook_text = script.get("hook", "")
    tc = _title_card_clip(script.get("title","CineAI Video"), hook_text, ColorClip, ver, dur=4)

    # Hook audio
    if hook_text:
        hook_audio_path = os.path.join(tmp, "hook_audio.mp3")
        if _make_audio(hook_text, hook_audio_path):
            try:
                ha = AudioFileClip(hook_audio_path)
                if ver >= 2:
                    ha = ha.with_duration(min(ha.duration, 4))
                    tc = tc.with_audio(ha)
                else:
                    ha = ha.set_duration(min(ha.duration, 4))
                    tc = tc.set_audio(ha)
            except Exception as e:
                print(f"Hook audio error: {e}")

    prog(total, "Concatenating all clips...")
    try:
        final = concatenate_videoclips([tc] + clips, method="compose")
    except Exception as e:
        return None, f"Concatenation failed: {e}"

    prog(total, "Writing MP4 (please wait)...")
    try:
        if ver >= 2:
            final.write_videofile(
                output_path, fps=24, codec="libx264",
                audio_codec="aac", audio=True
            )
        else:
            final.write_videofile(
                output_path, fps=24, codec="libx264",
                audio_codec="aac", audio=True,
                verbose=False, logger=None
            )
    except Exception as e:
        return None, f"Write failed: {e}"

    try: final.close()
    except Exception: pass

    return output_path, None
