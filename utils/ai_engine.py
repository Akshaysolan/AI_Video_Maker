"""
AI Video Engine - RAG + LLM Agents
Powered by Groq (Free API) — llama-3.3-70b-versatile
Get your free key: https://console.groq.com/keys
"""
import os
import json
import time

def _get_client():
    from groq import Groq
    try:
        import streamlit as st
        api_key = st.secrets.get("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY", "")
    except Exception:
        api_key = os.environ.get("GROQ_API_KEY", "")
    return Groq(api_key=api_key)

def _call_llm(system, prompt, max_tokens=4096):
    client = _get_client()
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=max_tokens,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
    )
    raw = response.choices[0].message.content.strip()
    raw = raw.lstrip("```json").lstrip("```").rstrip("```").strip()
    return json.loads(raw)

# ─────────────────────────────────────────────
# RAG: In-memory knowledge base for video styles
# ─────────────────────────────────────────────
VIDEO_KNOWLEDGE_BASE = {
    "cinematic": {
        "transitions": ["fade", "cross-dissolve", "wipe", "push"],
        "music": ["orchestral", "ambient", "dramatic"],
        "color_grade": "warm tones, high contrast",
        "pacing": "slow to fast build"
    },
    "corporate": {
        "transitions": ["cut", "fade", "slide"],
        "music": ["upbeat corporate", "inspiring", "minimal"],
        "color_grade": "cool blues, clean whites",
        "pacing": "steady, professional"
    },
    "social_media": {
        "transitions": ["quick cut", "zoom", "spin"],
        "music": ["trending pop", "energetic", "viral beats"],
        "color_grade": "vibrant, saturated",
        "pacing": "very fast, attention-grabbing"
    },
    "documentary": {
        "transitions": ["slow dissolve", "natural cut"],
        "music": ["ambient nature", "subtle", "world music"],
        "color_grade": "natural, desaturated",
        "pacing": "measured, informative"
    },
    "educational": {
        "transitions": ["slide", "zoom", "fade"],
        "music": ["light background", "focus-friendly"],
        "color_grade": "bright, clear",
        "pacing": "methodical, clear"
    },
}

def rag_retrieve(query, style="cinematic"):
    """RAG: Retrieve relevant style/production context."""
    key = style.lower().replace(" ", "_")
    data = VIDEO_KNOWLEDGE_BASE.get(key, VIDEO_KNOWLEDGE_BASE["cinematic"])
    return f"""VIDEO PRODUCTION KNOWLEDGE:
Style: {style}
Transitions: {', '.join(data['transitions'])}
Music Genre: {', '.join(data['music'])}
Color Grade: {data['color_grade']}
Pacing: {data['pacing']}"""

# ─────────────────────────────────────────────
# AGENTS
# ─────────────────────────────────────────────

def script_agent(topic, duration_minutes, style, tone, target_audience):
    """Agent 1: Generates detailed video script."""
    rag = rag_retrieve(topic, style)
    word_count = int(duration_minutes * 120)
    return _call_llm(
        f"""You are a professional video scriptwriter and content strategist.
{rag}
IMPORTANT: Return ONLY a valid JSON object. No explanation, no markdown, no preamble.""",
        f"""Create a video script:
Topic: {topic}
Duration: {duration_minutes} minutes (~{word_count} words)
Style: {style} | Tone: {tone} | Audience: {target_audience}

Return this exact JSON structure:
{{
  "title": "Compelling Video Title",
  "hook": "Opening 10-second hook sentence",
  "sections": [
    {{
      "name": "Section Name",
      "duration_seconds": 60,
      "narration": "Full narration text for this section...",
      "visual_description": "What appears on screen",
      "b_roll": "B-roll footage suggestions",
      "on_screen_text": "Text overlays for this section"
    }}
  ],
  "call_to_action": "Closing CTA text",
  "total_duration_seconds": {int(duration_minutes * 60)}
}}""",
        max_tokens=4096
    )


def scene_agent(section, style):
    """Agent 2: Generates shot lists and scene directions."""
    rag = rag_retrieve(section.get("name", ""), style)
    return _call_llm(
        f"""You are a professional cinematographer and scene director.
{rag}
IMPORTANT: Return ONLY a valid JSON object. No explanation, no markdown, no preamble.""",
        f"""Create a detailed shot list for this video section:
Section: {section['name']}
Narration: {section['narration'][:250]}
Visual Description: {section.get('visual_description', '')}
Duration: {section.get('duration_seconds', 30)} seconds

Return this exact JSON structure:
{{
  "shots": [
    {{
      "shot_number": 1,
      "shot_type": "wide/medium/close-up/extreme close-up",
      "angle": "eye-level/high/low/dutch",
      "movement": "static/pan/tilt/dolly/zoom",
      "description": "Detailed shot description",
      "duration_seconds": 5,
      "audio_notes": "Sound design notes"
    }}
  ],
  "color_palette": ["#1a1a2e", "#e94560", "#f5a623"],
  "mood": "Scene mood description",
  "transitions_into_next": "Transition type and description"
}}""",
        max_tokens=2048
    )


def metadata_agent(script, style, tone):
    """Agent 3: SEO metadata and thumbnail ideas."""
    return _call_llm(
        """You are a video SEO expert and content strategist.
IMPORTANT: Return ONLY a valid JSON object. No explanation, no markdown, no preamble.""",
        f"""Generate complete metadata for this video:
Title: {script['title']}
Style: {style} | Tone: {tone}
Hook: {script['hook']}

Return this exact JSON structure:
{{
  "seo_title": "SEO optimized title under 60 chars",
  "description": "Full YouTube/social description about 150 words",
  "tags": ["tag1", "tag2", "tag3", "tag4", "tag5", "tag6", "tag7", "tag8", "tag9", "tag10"],
  "thumbnail_concepts": [
    {{"concept": "Concept 1 visual description", "text_overlay": "Bold text on thumbnail"}},
    {{"concept": "Concept 2 visual description", "text_overlay": "Bold text on thumbnail"}}
  ],
  "best_posting_time": "Best day and time to post",
  "estimated_engagement": "Engagement prediction with reasoning"
}}""",
        max_tokens=1024
    )


def production_timeline_agent(script):
    """Agent 4: Production plan, equipment, and timeline."""
    sections = [s['name'] for s in script.get("sections", [])]
    total_secs = script.get("total_duration_seconds", 120)
    return _call_llm(
        """You are a professional video production manager.
IMPORTANT: Return ONLY a valid JSON object. No explanation, no markdown, no preamble.""",
        f"""Create a full production plan for a {total_secs // 60}-minute video.
Sections: {sections}

Return this exact JSON structure:
{{
  "pre_production": [
    {{"task": "Task name", "estimated_hours": 2, "priority": "high"}}
  ],
  "production": [
    {{"task": "Task name", "estimated_hours": 3, "priority": "high"}}
  ],
  "post_production": [
    {{"task": "Task name", "estimated_hours": 4, "priority": "medium"}}
  ],
  "equipment_needed": ["Camera", "Tripod", "Lights", "Microphone"],
  "software_recommended": ["Premiere Pro", "After Effects", "DaVinci Resolve"],
  "total_estimated_hours": 20
}}""",
        max_tokens=1024
    )


# ─────────────────────────────────────────────
# ORCHESTRATOR
# ─────────────────────────────────────────────

def orchestrate_video_generation(
    topic, duration_minutes, style, tone, target_audience, on_progress=None
):
    """Main orchestrator — runs all 4 agents sequentially."""
    def progress(step, msg):
        if on_progress:
            on_progress(step, msg)

    # Agent 1
    progress(1, "Script Agent: Crafting your narration & structure...")
    script = script_agent(topic, duration_minutes, style, tone, target_audience)
    time.sleep(0.3)

    # Agent 2
    progress(2, "Scene Agent: Building shot lists & cinematography...")
    scenes = []
    for section in script.get("sections", [])[:3]:
        scene = scene_agent(section, style)
        scenes.append({"section": section["name"], "scene_data": scene})
        time.sleep(0.2)

    # Agent 3
    progress(3, "Metadata Agent: Optimizing SEO & engagement...")
    metadata = metadata_agent(script, style, tone)
    time.sleep(0.2)

    # Agent 4
    progress(4, "Production Agent: Creating timeline & resource plan...")
    timeline = production_timeline_agent(script)

    progress(5, "All agents complete! Your video package is ready.")
    return {
        "script": script,
        "scenes": scenes,
        "metadata": metadata,
        "timeline": timeline
    }
