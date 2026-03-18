import streamlit as st
import json
import time
import os
import tempfile
from utils.video_builder import build_video


def _get_pexels_key():
    try:
        import streamlit as _st
        key = _st.secrets.get("PEXELS_API_KEY", "")
        if key:
            return key
    except Exception:
        pass
    return os.environ.get("PEXELS_API_KEY", "")


def _check_moviepy():
    try:
        import moviepy
        ver = int(getattr(moviepy, "__version__", "1.0.0").split(".")[0])
        if ver >= 2:
            from moviepy import VideoFileClip, ColorClip
        else:
            from moviepy.editor import VideoFileClip, ColorClip
        return True
    except Exception:
        return False


def render_my_videos():
    history = st.session_state.get("video_history", [])

    st.markdown("""
    <div class="page-header">📁 My Videos</div>
    <div class="page-sub">All your generated video packages in one place.</div>
    """, unsafe_allow_html=True)

    if not history:
        st.markdown("""
        <div style="text-align:center; padding:4rem 2rem; background:var(--surface);
            border:1px dashed var(--border); border-radius:20px;">
            <div style="font-size:4rem; margin-bottom:1rem;">🎬</div>
            <div style="font-family:'Syne',sans-serif; font-size:1.5rem; font-weight:700; color:var(--text);">
                No videos yet
            </div>
            <div style="color:var(--muted); margin:0.5rem 0 1.5rem;">
                Create your first AI video package to get started
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚀 Create Your First Video"):
            st.session_state.current_page = "create"
            st.rerun()
        return

    search = st.text_input("🔍 Search videos", placeholder="Search by title or topic...")
    st.markdown("<br>", unsafe_allow_html=True)

    filtered = history if not search else [
        v for v in history
        if search.lower() in v.get("title", "").lower()
        or search.lower() in v.get("topic", "").lower()
    ]

    if not filtered:
        st.info("No videos match your search.")
        return

    for i, video in enumerate(reversed(filtered)):
        vid_id    = video.get("id", str(i))
        results   = video.get("results") or {}
        script    = results.get("script") or {}
        sections  = script.get("sections") or []
        title     = video.get("title", "Untitled")
        duration  = video.get("duration", "N/A")
        created   = video.get("created", "N/A")
        topic_txt = (video.get("topic") or "")[:60] + "..."
        has_script = bool(sections)

        # ── Pure HTML card (NO widgets inside) ──────────────────
        badge_sections = (
            f'<span style="background:rgba(59,130,246,0.15);color:#3B82F6;'
            f'border-radius:20px;padding:3px 12px;font-size:0.75rem;font-weight:600;">'
            f'{len(sections)} sections</span>'
        ) if has_script else ""

        st.markdown(f"""
        <div style="background:var(--surface); border:1px solid var(--border);
            border-radius:16px; overflow:hidden; margin-bottom:0.75rem;">
            <div style="height:140px; background:linear-gradient(135deg,#1E2A3D,#0D1221);
                display:flex; align-items:center; justify-content:center; font-size:3rem;">
                🎬
            </div>
            <div style="padding:1rem 1.25rem 0.75rem;">
                <div style="font-weight:700;font-size:1.05rem;color:var(--text);margin-bottom:6px;">
                    {title}
                </div>
                <div style="color:var(--muted);font-size:0.82rem;">
                    ⏱ {duration} &nbsp;·&nbsp; 📅 {created}
                </div>
                <div style="color:var(--muted);font-size:0.8rem;margin-top:4px;">
                    📝 {topic_txt}
                </div>
                <div style="margin-top:10px;display:flex;gap:6px;flex-wrap:wrap;">
                    <span style="background:rgba(16,185,129,0.15);color:#10B981;
                        border-radius:20px;padding:3px 12px;font-size:0.75rem;font-weight:600;">
                        ✓ Complete
                    </span>
                    {badge_sections}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Buttons BELOW html card ──────────────────────────────
        b1, b2, b3 = st.columns([1, 1, 1])

        with b1:
            if st.button("📄 View Script", key=f"s_{vid_id}_{i}", use_container_width=True):
                cur = st.session_state.get(f"panel_{vid_id}")
                st.session_state[f"panel_{vid_id}"] = None if cur == "script" else "script"
                st.rerun()

        with b2:
            if st.button("▶ Play Video", key=f"p_{vid_id}_{i}", use_container_width=True):
                cur = st.session_state.get(f"panel_{vid_id}")
                st.session_state[f"panel_{vid_id}"] = None if cur == "play" else "play"
                st.rerun()

        with b3:
            if results:
                st.download_button(
                    "⬇️ JSON",
                    json.dumps(results, indent=2),
                    file_name=f"video_{vid_id}.json",
                    mime="application/json",
                    key=f"d_{vid_id}_{i}",
                    use_container_width=True,
                )

        # ── Panels ──────────────────────────────────────────────
        panel = st.session_state.get(f"panel_{vid_id}")

        if panel == "script":
            if not has_script:
                st.warning(
                    "⚠️ This is a **demo video** — no script data is saved. "
                    "Generate a new video from **🎬 Create Video** to get full script access."
                )
            else:
                with st.container():
                    st.markdown(f"**🎬 Title:** {script.get('title','N/A')}")
                    st.markdown(f"**🪝 Hook:** {script.get('hook','N/A')}")
                    st.markdown(f"**📢 CTA:** {script.get('call_to_action','N/A')}")
                    st.markdown("---")
                    for j, sec in enumerate(sections):
                        st.markdown(
                            f"**Section {j+1}: {sec.get('name','')}** "
                            f"({sec.get('duration_seconds',0)}s)"
                        )
                        st.write((sec.get("narration","")[:200]) + "...")

        elif panel == "play":
            _render_panel(script, sections, vid_id)

        st.markdown(
            "<hr style='border-color:var(--border);margin:0.5rem 0 1.5rem;'>",
            unsafe_allow_html=True
        )


def _render_panel(script, sections, vid_id):
    """Video render panel."""

    # ── Already rendered — show immediately ─────────────────────
    cached = st.session_state.get(f"rendered_{vid_id}")
    if cached:
        st.success("✅ Video ready!")
        st.video(cached)
        st.download_button(
            "⬇️ Download MP4",
            cached,
            file_name=f"{script.get('title','video')}.mp4",
            mime="video/mp4",
            key=f"dl_c_{vid_id}",
        )
        return

    # ── No script sections = demo / old video ───────────────────
    if not sections:
        st.markdown("""
        <div style="background:rgba(255,107,53,0.08);border:1px solid var(--accent);
            border-radius:12px;padding:1.25rem;font-size:0.9rem;line-height:1.9;">
            <strong>⚠️ Cannot render this video</strong><br><br>
            This is a <b>demo / legacy video</b> that was created before full AI generation
            was enabled. It has no script sections stored.<br><br>
            👉 Go to <b>🎬 Create Video</b>, generate a new video,
            then come back here to render it as an MP4.
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🎬 Go Create a Video", key=f"goto_create_{vid_id}"):
            st.session_state.current_page = "create"
            st.rerun()
        return

    # ── Check dependencies ───────────────────────────────────────
    has_moviepy = _check_moviepy()
    pexels_key  = _get_pexels_key()
    has_pexels  = bool(pexels_key)

    c1, c2 = st.columns(2)
    with c1:
        st.success("✅ MoviePy installed") if has_moviepy else st.error("❌ MoviePy missing — pip install moviepy")
    with c2:
        st.success("✅ Pexels API key found") if has_pexels else st.error("❌ Pexels key missing")

    if not has_moviepy or not has_pexels:
        st.markdown("""
        <div style="background:rgba(255,107,53,0.08);border:1px solid var(--accent);
            border-radius:12px;padding:1.25rem;margin-top:0.75rem;font-size:0.88rem;line-height:2;">
            <strong>Setup needed:</strong><br>
            1️⃣ &nbsp;<code>pip install moviepy</code><br>
            2️⃣ &nbsp;Get free key →
            <a href="https://www.pexels.com/api/" target="_blank" style="color:var(--accent);">
            pexels.com/api</a><br>
            3️⃣ &nbsp;Add to <code>.streamlit/secrets.toml</code>:<br>
            &nbsp;&nbsp;<code>PEXELS_API_KEY = "your_key_here"</code>
        </div>
        """, unsafe_allow_html=True)
        return

    # ── Ready to render ──────────────────────────────────────────
    st.info(
        f"🎬 Ready! {len(sections)} sections found. "
        "Click below to fetch Pexels clips and assemble your MP4."
    )

    if st.button("🚀 Start Rendering Now", key=f"render_{vid_id}", use_container_width=True):
        out = os.path.join(tempfile.gettempdir(), f"cineai_{vid_id}_{int(time.time())}.mp4")
        bar    = st.progress(0)
        status = st.empty()

        def on_prog(cur, total, msg):
            bar.progress(int((cur / max(total, 1)) * 90))
            status.markdown(f"⚙️ **{msg}**")

        with st.spinner("Fetching clips & rendering — please wait..."):
            path, err = build_video(script, out, on_progress=on_prog)

        if err:
            st.error(f"❌ Render error: {err}")
        elif path and os.path.exists(path):
            bar.progress(100)
            status.markdown("✅ **Done!**")
            with open(path, "rb") as f:
                vbytes = f.read()
            st.session_state[f"rendered_{vid_id}"] = vbytes
            st.video(vbytes)
            st.download_button(
                "⬇️ Download MP4",
                vbytes,
                file_name=f"{script.get('title','video')}.mp4",
                mime="video/mp4",
                key=f"dl_done_{vid_id}",
            )
