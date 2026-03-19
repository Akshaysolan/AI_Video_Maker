import streamlit as st
from datetime import datetime

def render_dashboard():
    user = st.session_state.user
    plan = st.session_state.get("plan", "free")
    videos_used = st.session_state.get("videos_generated", 0)
    history = st.session_state.get("video_history", [])
    max_free = 5

    hour = datetime.now().hour
    greeting = "Good morning" if hour < 12 else "Good afternoon" if hour < 17 else "Good evening"

    st.markdown(f"""
    <div style="margin-bottom:2rem;">
        <div class="page-header">{greeting}, {user['name'].split()[0]}! 👋</div>
        <div class="page-sub">Here's your video creation overview.</div>
    </div>
    """, unsafe_allow_html=True)

    # Metrics
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">🎬</div>
            <div class="metric-value">{len(history)}</div>
            <div class="metric-label">Videos Created</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        remaining = max(0, max_free - videos_used) if plan == "free" else "∞"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">🎯</div>
            <div class="metric-value">{remaining}</div>
            <div class="metric-label">Videos Remaining</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">⏱️</div>
            <div class="metric-value">5</div>
            <div class="metric-label">Max Duration (min)</div>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">{'⭐' if plan == 'pro' else '🆓'}</div>
            <div class="metric-value">{'PRO' if plan == 'pro' else 'FREE'}</div>
            <div class="metric-label">Current Plan</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.markdown("### 🚀 Quick Actions")
        st.markdown("<br>", unsafe_allow_html=True)

        a1, a2 = st.columns(2)
        with a1:
            st.markdown("""
            <div class="step-card">
                <div class="step-num">1</div>
                <div class="step-content">
                    <h4>Write Your Text</h4>
                    <p>Describe your video idea, topic, or paste your script</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with a2:
            st.markdown("""
            <div class="step-card">
                <div class="step-num">2</div>
                <div class="step-content">
                    <h4>Set Parameters</h4>
                    <p>Choose style, duration, tone, and target audience</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        a3, a4 = st.columns(2)
        with a3:
            st.markdown("""
            <div class="step-card">
                <div class="step-num">3</div>
                <div class="step-content">
                    <h4>AI Generates</h4>
                    <p>4 specialized agents build your complete video package</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with a4:
            st.markdown("""
            <div class="step-card">
                <div class="step-num">4</div>
                <div class="step-content">
                    <h4>Download & Use</h4>
                    <p>Get script, shot list, metadata, and production plan</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
        if st.button("🎬 Create New Video", use_container_width=True):
            st.session_state.current_page = "create"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with col_right:
        st.markdown("### 📊 Usage")
        if plan == "free":
            pct = min(100, int((videos_used / max_free) * 100))
            st.markdown(f"""
            <div style="background:var(--surface); border:1px solid var(--border); border-radius:16px; padding:1.5rem;">
                <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
                    <span style="color:var(--text); font-weight:600;">Free Plan</span>
                    <span style="color:var(--muted); font-size:0.85rem;">{videos_used}/{max_free}</span>
                </div>
                <div class="progress-bar-outer">
                    <div class="progress-bar-inner" style="width:{pct}%"></div>
                </div>
                <div style="color:var(--muted); font-size:0.8rem; margin-top:8px;">{max_free - videos_used} videos remaining</div>
                <br>
                <div class="alert-box alert-warning" style="font-size:0.8rem;">
                    Upgrade to PRO for unlimited videos!
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("⭐ Upgrade to PRO", use_container_width=True):
                st.session_state.current_page = "subscription"
                st.rerun()
        else:
            st.markdown("""
            <div style="background:var(--surface); border:1px solid var(--accent); border-radius:16px; padding:1.5rem; text-align:center;">
                <div style="font-size:2rem;">⭐</div>
                <div style="font-family:'Syne',sans-serif; font-weight:800; color:var(--accent2); font-size:1.2rem; margin:0.5rem 0;">PRO Active</div>
                <div style="color:var(--muted); font-size:0.85rem;">Unlimited video generation</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 🤖 AI Agents")
        agents = [
            ("📝", "Script Agent", "Crafts full narration"),
            ("🎬", "Scene Agent", "Shot lists & direction"),
            ("📊", "Metadata Agent", "SEO optimization"),
            ("📋", "Production Agent", "Timeline & resources"),
        ]
        for icon, name, desc in agents:
            st.markdown(f"""
            <div style="display:flex; gap:10px; align-items:center; padding:8px 0; border-bottom:1px solid var(--border);">
                <span style="font-size:1.3rem;">{icon}</span>
                <div>
                    <div style="font-weight:600; font-size:0.85rem; color:var(--text);">{name}</div>
                    <div style="color:var(--muted); font-size:0.75rem;">{desc}</div>
                </div>
                <div style="margin-left:auto; color:var(--success); font-size:0.75rem;">● Ready</div>
            </div>
            """, unsafe_allow_html=True)

    # Recent videos
    if history:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 📁 Recent Videos")
        cols = st.columns(3)
        for i, video in enumerate(history[-3:]):
            with cols[i % 3]:
                status_badge = f'<span class="video-badge badge-done">✓ Done</span>' if video.get("status") == "done" else f'<span class="video-badge badge-process">⟳ Processing</span>'
                st.markdown(f"""
                <div class="video-card">
                    <div class="video-thumb">🎬</div>
                    <div class="video-info">
                        <div class="video-title">{video.get('title','Untitled')}</div>
                        <div class="video-meta">⏱ {video.get('duration','N/A')} · {video.get('created','')}</div>
                        {status_badge}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
        
