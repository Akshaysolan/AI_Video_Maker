import streamlit as st
import json
import time
import os
import tempfile
from datetime import datetime
from utils.ai_engine import orchestrate_video_generation
from utils.auth import update_user_in_db
from utils.video_builder import build_video


def render_video_generator():
    plan = st.session_state.get("plan", "free")
    videos_used = st.session_state.get("videos_generated", 0)
    max_free = 5

    st.markdown("""
    <div class="page-header">🎬 Create Your Video</div>
    <div class="page-sub">Describe your idea — our AI agents will build the complete video package.</div>
    """, unsafe_allow_html=True)

    
    # Quota check
    if plan == "free" and videos_used >= max_free:
        st.markdown("""
        <div class="alert-box alert-warning" style="font-size:1rem; padding:1.5rem; border-radius:16px;">
            <strong>🚫 Free Limit Reached</strong><br><br>
            You've used all 5 free videos. Upgrade to PRO for unlimited video generation,
            priority processing, and exclusive features!
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
        if st.button("⭐ Upgrade to PRO — $9.99/mo", use_container_width=False):
            st.session_state.current_page = "subscription"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        return

    col_form, col_tips = st.columns([2, 1])

    with col_form:
        st.markdown("#### 📝 Your Video Content")
        topic = st.text_area(
            "Describe your video topic or paste your script",
            height=180,
            placeholder="E.g.: A 3-minute product launch video for our new AI-powered fitness app. Target audience: health-conscious millennials. Highlights: personalized workouts, sleep tracking, nutrition AI, 30-day free trial...",
            key="video_topic"
        )
        char_count = len(topic) if topic else 0
        st.caption(f"{char_count} characters · Min 20 recommended")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### ⚙️ Video Settings")

        c1, c2 = st.columns(2)
        with c1:
            duration = st.slider(
                "Duration (minutes)",
                min_value=0.5,
                max_value=5.0,
                value=2.0,
                step=0.5,
                help="Maximum 5 minutes per video"
            )
            style = st.selectbox(
                "Video Style",
                ["Cinematic", "Corporate", "Social Media", "Documentary", "Educational"],
            )
        with c2:
            tone = st.selectbox(
                "Tone",
                ["Inspirational", "Professional", "Casual & Fun", "Serious", "Energetic", "Emotional"],
            )
            audience = st.text_input(
                "Target Audience",
                placeholder="e.g. Young professionals 25-35",
                value="General audience"
            )

        st.markdown("<br>", unsafe_allow_html=True)

        # Usage indicator
        if plan == "free":
            remaining = max_free - videos_used
            pct = min(100, int((videos_used / max_free) * 100))
            st.markdown(f"""
            <div style="background:var(--surface2); border:1px solid var(--border); border-radius:10px; padding:1rem; margin-bottom:1rem;">
                <div style="display:flex; justify-content:space-between; font-size:0.85rem; color:var(--muted); margin-bottom:6px;">
                    <span>Free quota: {videos_used}/{max_free} used</span>
                    <span>{remaining} remaining</span>
                </div>
                <div class="progress-bar-outer"><div class="progress-bar-inner" style="width:{pct}%"></div></div>
            </div>
            """, unsafe_allow_html=True)

        can_generate = bool(topic and len(topic.strip()) >= 20)
        st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
        generate_btn = st.button(
            f"🚀 Generate Video Package ({duration} min)",
            use_container_width=True,
            disabled=not can_generate
        )
        st.markdown('</div>', unsafe_allow_html=True)
        if not can_generate and topic is not None:
            st.caption("⚠️ Please enter at least 20 characters describing your video.")

    with col_tips:
        st.markdown("""
        <div style="background:var(--surface); border:1px solid var(--border); border-radius:16px; padding:1.5rem;">
            <div style="font-family:'Syne',sans-serif; font-weight:700; margin-bottom:1rem;">💡 Pro Tips</div>
        </div>
        """, unsafe_allow_html=True)

        tips = [
            ("🎯", "Be specific", "Include key messages, brand name, and unique selling points"),
            ("👥", "Define audience", "Mention demographics, pain points, and desires"),
            ("📌", "Add context", "Include industry, competitors, or inspiration sources"),
            ("🎨", "Set the mood", "Describe the emotion you want viewers to feel"),
            ("📢", "Include CTA", "What should viewers do after watching?"),
        ]
        for icon, title, desc in tips:
            st.markdown(f"""
            <div style="display:flex; gap:10px; padding:10px 0; border-bottom:1px solid var(--border);">
                <span style="font-size:1.2rem;">{icon}</span>
                <div>
                    <div style="font-weight:600; font-size:0.85rem; color:var(--text);">{title}</div>
                    <div style="color:var(--muted); font-size:0.75rem; margin-top:2px;">{desc}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="background:var(--surface); border:1px solid var(--border); border-radius:16px; padding:1.5rem;">
            <div style="font-family:'Syne',sans-serif; font-weight:700; margin-bottom:0.75rem;">🤖 What You'll Get</div>
            <div style="color:var(--muted); font-size:0.82rem; line-height:2;">
                ✅ Full narration script<br>
                ✅ Scene-by-scene shot list<br>
                ✅ B-roll suggestions<br>
                ✅ SEO metadata & tags<br>
                ✅ Thumbnail concepts<br>
                ✅ Production timeline<br>
                ✅ Equipment list<br>
                ✅ Rendered MP4 video<br>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # GENERATION
    if generate_btn and can_generate:
        _run_generation(
            topic, duration,
            style.lower().replace(" ", "_"),
            tone.lower().replace(" & ", "_").replace(" ", "_"),
            audience
        )


def _run_generation(topic, duration, style, tone, audience):
    st.markdown("---")
    st.markdown("### 🤖 AI Agents at Work")

    agent_labels = [
        "📝 Script Agent", "🎬 Scene Agent",
        "📊 Metadata Agent", "📋 Production Agent"
    ]
    agent_descs = [
        "Crafting your full narration script...",
        "Building detailed shot lists...",
        "Optimizing SEO and metadata...",
        "Creating production timeline...",
    ]

    progress_bar = st.progress(0)
    status_text = st.empty()
    agent_status_cols = st.columns(4)
    agent_status = ["pending", "pending", "pending", "pending"]

    def render_agents():
        for i, col in enumerate(agent_status_cols):
            icon = "✅" if agent_status[i] == "done" else "🔄" if agent_status[i] == "running" else "⏳"
            color = "var(--success)" if agent_status[i] == "done" else "var(--accent)" if agent_status[i] == "running" else "var(--muted)"
            col.markdown(f"""
            <div style="background:var(--surface); border:1px solid var(--border); border-radius:12px; padding:1rem; text-align:center;">
                <div style="font-size:1.5rem;">{icon}</div>
                <div style="font-weight:600; font-size:0.82rem; color:{color}; margin-top:4px;">{agent_labels[i]}</div>
                <div style="color:var(--muted); font-size:0.72rem; margin-top:2px;">{agent_descs[i]}</div>
            </div>
            """, unsafe_allow_html=True)

    agent_status[0] = "running"
    render_agents()
    progress_bar.progress(5)
    status_text.markdown("**Agent 1/4** — Generating script with RAG-enhanced prompting...")

    results = {}
    error = None

    def on_progress(step, msg):
        step_idx = step - 1
        if step_idx > 0:
            agent_status[step_idx - 1] = "done"
        if step_idx < 4:
            agent_status[step_idx] = "running"
        render_agents()
        progress_bar.progress(min(95, step * 20))
        status_text.markdown(f"**Agent {step}/4** — {msg}")

    try:
        results = orchestrate_video_generation(
            topic=topic,
            duration_minutes=duration,
            style=style,
            tone=tone,
            target_audience=audience,
            on_progress=on_progress
        )
        for i in range(4):
            agent_status[i] = "done"
        render_agents()
        progress_bar.progress(100)
        status_text.markdown("✅ **All agents complete!** Your video package is ready.")
    except Exception as e:
        error = str(e)
        status_text.markdown(f"⚠️ Error: {error}")
        st.error(f"Generation failed: {error}")

    if not error and results:
        _save_video(results, topic, duration)
        time.sleep(0.5)
        st.markdown("---")
        _display_results(results)


def _save_video(results, topic, duration):
    script = results.get("script", {})
    title = script.get("title", topic[:50])
    mins = int(duration)
    secs = int((duration % 1) * 60)
    duration_str = f"{mins}:{secs:02d}"

    video_entry = {
        "id": f"v{int(time.time())}",
        "title": title,
        "duration": duration_str,
        "status": "done",
        "created": datetime.now().strftime("%Y-%m-%d"),
        "topic": topic[:100],
        "results": results  # Keep full results in session state
    }

    # Update session state
    history = st.session_state.get("video_history", [])
    history.append(video_entry)
    st.session_state.video_history = history
    st.session_state.videos_generated = st.session_state.get("videos_generated", 0) + 1

    # Save to database - include results in the stored data
    email = st.session_state.user["email"]
    
    # Create a copy of history for database with results included
    db_history = []
    for vid in history:
        # Deep copy to avoid modifying session state
        vid_copy = vid.copy()
        if "results" in vid_copy:
            # Keep results in database too
            vid_copy["results"] = vid_copy["results"]
        db_history.append(vid_copy)
    
    update_user_in_db(email, {
        "videos_generated": st.session_state.videos_generated,
        "video_history": db_history  # Store full history with results
    })


def _display_results(results):
    script = results.get("script", {})
    scenes = results.get("scenes", [])
    metadata = results.get("metadata", {})
    timeline = results.get("timeline", {})

    st.markdown(f"""
    <div style="background:linear-gradient(135deg, rgba(255,107,53,0.1), rgba(255,159,28,0.05));
        border:1px solid var(--accent); border-radius:20px; padding:2rem; margin-bottom:2rem;">
        <div style="font-family:'Syne',sans-serif; font-size:1.8rem; font-weight:800; color:var(--text);">
            🎬 {script.get('title', 'Your Video')}
        </div>
        <div style="color:var(--muted); margin-top:0.5rem;">
            ⏱ {int(script.get('total_duration_seconds', 120) / 60)} min {script.get('total_duration_seconds', 120) % 60} sec
            · {len(script.get('sections', []))} sections · {len(scenes)} scene directions
        </div>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["📝 Script", "🎬 Shot List", "📊 Metadata & SEO", "📋 Production Plan"])

    with tab1:
        st.markdown(f"""
        <div class="alert-box alert-success" style="margin-bottom:1.5rem;">
            <strong>🪝 Hook:</strong> {script.get('hook', '')}
        </div>
        """, unsafe_allow_html=True)

        for i, section in enumerate(script.get("sections", [])):
            with st.expander(f"Section {i+1}: {section.get('name', '')} ({section.get('duration_seconds', 0)}s)", expanded=(i == 0)):
                c1, c2 = st.columns([3, 2])
                with c1:
                    st.markdown("**🎙️ Narration**")
                    st.markdown(f'<div style="background:var(--surface2); padding:1rem; border-radius:10px; color:var(--text); line-height:1.8; font-size:0.9rem;">{section.get("narration", "")}</div>', unsafe_allow_html=True)
                with c2:
                    st.markdown("**📸 Visual Description**")
                    st.info(section.get("visual_description", ""))
                    st.markdown("**🎥 B-Roll**")
                    st.info(section.get("b_roll", ""))
                    if section.get("on_screen_text"):
                        st.markdown("**💬 On-Screen Text**")
                        st.info(section.get("on_screen_text", ""))

        st.markdown(f"""
        <div class="alert-box alert-info" style="margin-top:1rem;">
            <strong>📢 Call to Action:</strong> {script.get('call_to_action', '')}
        </div>
        """, unsafe_allow_html=True)

        script_text = f"# {script.get('title', 'Video Script')}\n\n"
        script_text += f"**Hook:** {script.get('hook', '')}\n\n"
        for i, s in enumerate(script.get("sections", [])):
            script_text += f"## Section {i+1}: {s.get('name', '')} ({s.get('duration_seconds', 0)}s)\n\n"
            script_text += f"**Narration:**\n{s.get('narration', '')}\n\n"
            script_text += f"**Visuals:** {s.get('visual_description', '')}\n\n"
        script_text += f"**CTA:** {script.get('call_to_action', '')}"
        st.download_button("⬇️ Download Script", script_text, f"script_{int(time.time())}.md", "text/markdown")

    with tab2:
        for scene_data in scenes:
            section_name = scene_data.get("section", "")
            shots = scene_data.get("scene_data", {}).get("shots", [])
            mood = scene_data.get("scene_data", {}).get("mood", "")
            colors = scene_data.get("scene_data", {}).get("color_palette", [])

            st.markdown(f"#### 🎞️ {section_name}")
            if mood:
                st.markdown(f'<div class="alert-box alert-info" style="font-size:0.85rem; margin-bottom:1rem;">🎭 Mood: {mood}</div>', unsafe_allow_html=True)
            if colors:
                color_html = "".join([f'<span style="display:inline-block; width:24px; height:24px; border-radius:50%; background:{c}; margin-right:4px; border:1px solid var(--border);"></span>' for c in colors])
                st.markdown(f'<div style="margin-bottom:1rem;">🎨 Color Palette: {color_html}</div>', unsafe_allow_html=True)

            for shot in shots:
                st.markdown(f"""
                <div style="background:var(--surface2); border:1px solid var(--border); border-radius:10px; padding:1rem; margin-bottom:0.75rem;">
                    <div style="display:flex; gap:1rem; align-items:flex-start;">
                        <div style="background:var(--accent); color:white; border-radius:8px; padding:4px 10px; font-family:'Syne',sans-serif; font-weight:800; font-size:0.85rem; flex-shrink:0;">#{shot.get('shot_number', '?')}</div>
                        <div style="flex:1;">
                            <div style="font-weight:600; color:var(--text); margin-bottom:4px;">{shot.get('description', '')}</div>
                            <div style="display:flex; gap:1rem; flex-wrap:wrap; color:var(--muted); font-size:0.8rem; margin-top:4px;">
                                <span>📐 {shot.get('shot_type', '')}</span>
                                <span>📷 {shot.get('angle', '')}</span>
                                <span>🎥 {shot.get('movement', '')}</span>
                                <span>⏱ {shot.get('duration_seconds', 0)}s</span>
                            </div>
                            {f'<div style="color:var(--muted); font-size:0.78rem; margin-top:6px;">🔊 {shot.get("audio_notes", "")}</div>' if shot.get("audio_notes") else ""}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            transition = scene_data.get("scene_data", {}).get("transitions_into_next", "")
            if transition:
                st.markdown(f'<div style="color:var(--muted); font-size:0.8rem; text-align:center; padding:0.5rem;">↓ {transition}</div>', unsafe_allow_html=True)
            st.markdown("---")

    with tab3:
        c1, c2 = st.columns([3, 2])
        with c1:
            st.markdown("#### 🔍 SEO Optimization")
            st.markdown(f"**Optimized Title:** {metadata.get('seo_title', '')}")
            st.markdown("**Description:**")
            st.text_area("", metadata.get("description", ""), height=120, key="meta_desc", disabled=True)
            st.markdown("**Tags:**")
            tags = metadata.get("tags", [])
            tag_html = " ".join([f'<span style="background:var(--surface2); border:1px solid var(--border); border-radius:20px; padding:4px 12px; font-size:0.78rem; color:var(--text); margin:3px; display:inline-block;">#{t}</span>' for t in tags])
            st.markdown(f'<div>{tag_html}</div>', unsafe_allow_html=True)
        with c2:
            st.markdown("#### 🖼️ Thumbnail Ideas")
            for t in metadata.get("thumbnail_concepts", []):
                st.markdown(f"""
                <div style="background:var(--surface2); border:1px solid var(--border); border-radius:10px; padding:1rem; margin-bottom:0.75rem;">
                    <div style="font-size:0.85rem; color:var(--text);">{t.get('concept', '')}</div>
                    <div style="color:var(--accent2); font-size:0.78rem; margin-top:4px; font-weight:600;">Text: {t.get('text_overlay', '')}</div>
                </div>
                """, unsafe_allow_html=True)
            if metadata.get("best_posting_time"):
                st.markdown(f"""
                <div class="alert-box alert-success" style="font-size:0.82rem;">
                    📅 Best posting time: {metadata['best_posting_time']}
                </div>
                """, unsafe_allow_html=True)

    with tab4:
        total_hrs = timeline.get("total_estimated_hours", 0)
        st.markdown(f"""
        <div style="background:var(--surface2); border:1px solid var(--border); border-radius:12px; padding:1rem; margin-bottom:1.5rem; display:flex; gap:2rem;">
            <div><div style="font-family:'Syne',sans-serif; font-size:2rem; font-weight:800; color:var(--accent);">{total_hrs}</div><div style="color:var(--muted); font-size:0.85rem;">Total Hours</div></div>
            <div style="border-left:1px solid var(--border); padding-left:2rem;"><div style="font-family:'Syne',sans-serif; font-size:2rem; font-weight:800; color:var(--blue);">{len(timeline.get('pre_production', []))}</div><div style="color:var(--muted); font-size:0.85rem;">Pre-prod Tasks</div></div>
            <div style="border-left:1px solid var(--border); padding-left:2rem;"><div style="font-family:'Syne',sans-serif; font-size:2rem; font-weight:800; color:var(--purple);">{len(timeline.get('post_production', []))}</div><div style="color:var(--muted); font-size:0.85rem;">Post-prod Tasks</div></div>
        </div>
        """, unsafe_allow_html=True)

        phases = [
            ("Pre-Production", "pre_production", "#3B82F6"),
            ("Production", "production", "#FF6B35"),
            ("Post-Production", "post_production", "#8B5CF6"),
        ]
        for phase_name, phase_key, color in phases:
            tasks = timeline.get(phase_key, [])
            if tasks:
                st.markdown(f'<div style="font-weight:700; color:{color}; font-family:Syne,sans-serif; margin:1rem 0 0.5rem;">{phase_name}</div>', unsafe_allow_html=True)
                for task in tasks:
                    priority_color = {"high": "#EF4444", "medium": "#F59E0B", "low": "#10B981"}.get(task.get("priority", "medium"), "#64748B")
                    st.markdown(f"""
                    <div style="display:flex; align-items:center; gap:1rem; padding:0.6rem 0; border-bottom:1px solid var(--border);">
                        <span style="color:{priority_color}; font-size:0.7rem; font-weight:700; text-transform:uppercase; min-width:40px;">{task.get('priority', 'med')}</span>
                        <span style="color:var(--text); font-size:0.88rem; flex:1;">{task.get('task', '')}</span>
                        <span style="color:var(--muted); font-size:0.8rem;">~{task.get('estimated_hours', 0)}h</span>
                    </div>
                    """, unsafe_allow_html=True)

        equipment = timeline.get("equipment_needed", [])
        software = timeline.get("software_recommended", [])
        if equipment or software:
            st.markdown("<br>", unsafe_allow_html=True)
            ec, sc = st.columns(2)
            with ec:
                if equipment:
                    st.markdown("**🎥 Equipment Needed**")
                    for item in equipment:
                        st.markdown(f"- {item}")
            with sc:
                if software:
                    st.markdown("**💻 Recommended Software**")
                    for item in software:
                        st.markdown(f"- {item}")

        full_json = json.dumps(results, indent=2)
        st.download_button("⬇️ Download Full Video Package (JSON)", full_json, f"video_package_{int(time.time())}.json", "application/json")

    # Render actual video section
    _render_video_section(results)


def _get_pexels_key():
    """Safely get Pexels API key from secrets or environment."""
    try:
        return st.secrets.get("PEXELS_API_KEY") or os.environ.get("PEXELS_API_KEY", "")
    except Exception:
        return os.environ.get("PEXELS_API_KEY", "")


def _render_video_section(results):
    """Section to render the actual MP4 video."""
    script = results.get("script", {})

    st.markdown("---")
    st.markdown("""
    <div style="font-family:'Syne',sans-serif; font-size:1.5rem; font-weight:800; color:var(--text); margin-bottom:0.5rem;">
        🎥 Render Actual Video
    </div>
    <div style="color:var(--muted); font-size:0.9rem; margin-bottom:1.5rem;">
        Assembles real stock video clips (Pexels) + text overlays into a playable MP4.
    </div>
    """, unsafe_allow_html=True)

    pexels_key = _get_pexels_key()
    has_pexels = bool(pexels_key)

    has_moviepy = False
    try:
        import moviepy
        ver = int(getattr(moviepy, "__version__", "1.0.0").split(".")[0])
        if ver >= 2:
            from moviepy import VideoFileClip, ColorClip
        else:
            from moviepy.editor import VideoFileClip, ColorClip
        has_moviepy = True
    except Exception:
        pass

    # Status indicators
    c1, c2 = st.columns(2)
    with c1:
        if has_moviepy:
            st.markdown('<div class="alert-box alert-success">✅ MoviePy installed</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="alert-box alert-warning">⚠️ MoviePy not installed — run: pip install moviepy</div>', unsafe_allow_html=True)
    with c2:
        if has_pexels:
            st.markdown('<div class="alert-box alert-success">✅ Pexels API connected</div>', unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="alert-box alert-warning">
                ⚠️ PEXELS_API_KEY missing —
                <a href="https://www.pexels.com/api/" target="_blank" style="color:var(--accent);">Get free key →</a>
            </div>
            """, unsafe_allow_html=True)

    if not has_moviepy or not has_pexels:
        st.markdown("""
        <div class="alert-box alert-info" style="margin-top:1rem;">
            <strong>Setup needed to render video:</strong><br>
            1. Run: <code>pip install moviepy</code><br>
            2. Get free Pexels key at <a href="https://www.pexels.com/api/" target="_blank" style="color:var(--accent);">pexels.com/api</a><br>
            3. Add to your <code>.streamlit/secrets.toml</code>:<br>
            <code>PEXELS_API_KEY = "your_key_here"</code>
        </div>
        """, unsafe_allow_html=True)
        return

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
    render_btn = st.button("🎬 Render Video Now", use_container_width=False, key="render_video_btn")
    st.markdown('</div>', unsafe_allow_html=True)
    st.caption("⚠️ Rendering takes 1–3 minutes depending on video length.")

    if render_btn:
        output_path = os.path.join(tempfile.gettempdir(), f"cineai_{int(time.time())}.mp4")
        progress_bar = st.progress(0)
        status = st.empty()

        def on_render_progress(current, total, msg):
            pct = int((current / max(total, 1)) * 90)
            progress_bar.progress(pct)
            status.markdown(f"**{msg}**")

        with st.spinner("Rendering your video..."):
            path, error = build_video(script, output_path, on_progress=on_render_progress)

        if error:
            st.error(f"Render failed: {error}")
        elif path and os.path.exists(path):
            progress_bar.progress(100)
            status.markdown("✅ **Video ready!**")
            st.markdown("<br>", unsafe_allow_html=True)
            with open(path, "rb") as f:
                video_bytes = f.read()
            st.video(video_bytes)
            st.download_button(
                "⬇️ Download MP4 Video",
                video_bytes,
                file_name=f"{script.get('title', 'cineai_video')}.mp4",
                mime="video/mp4"
            )
