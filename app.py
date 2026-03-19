import streamlit as st
st.set_page_config(
    page_title="CineAI - AI Video Maker",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

from utils.auth import init_session, render_auth_page
from utils.styles import inject_styles
from pages.dashboard import render_dashboard
from pages.video_generator import render_video_generator
from pages.my_videos import render_my_videos
from pages.subscription import render_subscription

inject_styles()
init_session()

st.set_page_config(layout="wide")

st.markdown("""
<style>
[data-testid="stSidebarNav"] {
    display: none;
}
</style>
""", unsafe_allow_html=True)


# Sidebar navigation
with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">
        <span class="logo-icon">🎬</span>
        <span class="logo-text">CineAI</span>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.get("authenticated"):
        user = st.session_state.user
        free_used = st.session_state.get("videos_generated", 0)
        plan = st.session_state.get("plan", "free")

        st.markdown(f"""
        <div class="user-card">
            <div class="user-avatar">{user['name'][0].upper()}</div>
            <div class="user-info">
                <div class="user-name">{user['name']}</div>
                <div class="user-plan {'plan-pro' if plan == 'pro' else 'plan-free'}">
                    {'⭐ PRO' if plan == 'pro' else f'🆓 FREE ({free_used}/5)'}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")
        pages = {
            "🏠 Dashboard": "dashboard",
            "🎬 Create Video": "create",
            "📁 My Videos": "my_videos",
            "💎 Subscription": "subscription",
        }
        for label, page_key in pages.items():
            if st.button(label, key=f"nav_{page_key}", use_container_width=True):
                st.session_state.current_page = page_key

        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    else:
        st.markdown("""
        <div class="sidebar-tagline">
            <p>Transform text into stunning AI-powered videos in minutes.</p>
        </div>
        """, unsafe_allow_html=True)

# Main content
if not st.session_state.get("authenticated"):
    render_auth_page()
else:
    page = st.session_state.get("current_page", "dashboard")
    if page == "dashboard":
        render_dashboard()
    elif page == "create":
        render_video_generator()
    elif page == "my_videos":
        render_my_videos()
    elif page == "subscription":
        render_subscription()
