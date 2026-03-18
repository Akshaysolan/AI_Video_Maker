import streamlit as st
import hashlib
import json
import os
from datetime import datetime

DB_FILE = "data/users.json"

def load_users():
    os.makedirs("data", exist_ok=True)
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w") as f:
            json.dump({}, f)
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(DB_FILE, "w") as f:
        json.dump(users, f, indent=2)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def init_session():
    defaults = {
        "authenticated": False,
        "user": None,
        "current_page": "dashboard",
        "videos_generated": 0,
        "plan": "free",
        "video_history": [],
        "auth_tab": "login",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

def signup(name, email, password):
    users = load_users()
    if email in users:
        return False, "Email already registered."
    users[email] = {
        "name": name,
        "email": email,
        "password": hash_password(password),
        "plan": "free",
        "videos_generated": 0,
        "video_history": [],
        "created_at": datetime.now().isoformat()
    }
    save_users(users)
    return True, "Account created!"

def login(email, password):
    users = load_users()
    if email not in users:
        return False, "Email not found."
    if users[email]["password"] != hash_password(password):
        return False, "Incorrect password."
    user = users[email]
    st.session_state.authenticated = True
    st.session_state.user = {"name": user["name"], "email": user["email"]}
    st.session_state.plan = user.get("plan", "free")
    st.session_state.videos_generated = user.get("videos_generated", 0)
    st.session_state.video_history = user.get("video_history", [])
    return True, "Logged in!"

def update_user_in_db(email, updates):
    users = load_users()
    if email in users:
        users[email].update(updates)
        save_users(users)

def render_auth_page():
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("""
        <div style="text-align:center; padding: 2rem 0 1.5rem;">
            <div style="font-size:3.5rem;">🎬</div>
            <div style="font-family:'Syne',sans-serif; font-size:2.8rem; font-weight:800;
                background:linear-gradient(135deg,#FF6B35,#FF9F1C);
                -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
                CineAI
            </div>
            <div style="color:#64748B; margin-top:0.5rem; font-size:1rem;">
                Transform text into cinematic AI videos
            </div>
        </div>
        """, unsafe_allow_html=True)

        tab_login, tab_signup = st.tabs(["🔐 Login", "✨ Sign Up"])

        with tab_login:
            st.markdown("<br>", unsafe_allow_html=True)
            email = st.text_input("Email", key="login_email", placeholder="you@example.com")
            password = st.text_input("Password", type="password", key="login_pass", placeholder="••••••••")
            st.markdown("<br>", unsafe_allow_html=True)
            with st.container():
                st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
                if st.button("Login to CineAI", use_container_width=True, key="do_login"):
                    if email and password:
                        ok, msg = login(email, password)
                        if ok:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
                    else:
                        st.warning("Please fill in all fields.")
                st.markdown('</div>', unsafe_allow_html=True)

            st.markdown("""
            <div style="text-align:center; color:#64748B; font-size:0.8rem; margin-top:1rem;">
                Demo: test@demo.com / demo123
            </div>
            """, unsafe_allow_html=True)

        with tab_signup:
            st.markdown("<br>", unsafe_allow_html=True)
            name = st.text_input("Full Name", key="reg_name", placeholder="John Doe")
            email2 = st.text_input("Email", key="reg_email", placeholder="you@example.com")
            pass2 = st.text_input("Password", type="password", key="reg_pass", placeholder="Min 6 characters")
            st.markdown("""
            <div class="alert-box alert-info" style="margin: 0.75rem 0; font-size:0.82rem;">
                🎁 Free plan: 5 videos included. No credit card required.
            </div>
            """, unsafe_allow_html=True)
            st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
            if st.button("Create Free Account", use_container_width=True, key="do_signup"):
                if name and email2 and pass2:
                    if len(pass2) < 6:
                        st.error("Password must be at least 6 characters.")
                    else:
                        ok, msg = signup(name, email2, pass2)
                        if ok:
                            st.success(msg + " Please login.")
                        else:
                            st.error(msg)
                else:
                    st.warning("Please fill in all fields.")
            st.markdown('</div>', unsafe_allow_html=True)

        # create demo user if not exists
        _create_demo_user()

def _create_demo_user():
    users = load_users()
    if "test@demo.com" not in users:
        users["test@demo.com"] = {
            "name": "Demo User",
            "email": "test@demo.com",
            "password": hash_password("demo123"),
            "plan": "free",
            "videos_generated": 2,
            "video_history": [
                {
                    "id": "v001", "title": "Product Launch Video", "duration": "2:30",
                    "status": "done", "created": "2024-01-10", "topic": "Tech startup product launch",
                    "results": {
                        "script": {
                            "title": "Product Launch Video",
                            "hook": "What if your next product launch could reach 10x more people?",
                            "sections": [
                                {"name": "Introduction", "duration_seconds": 30,
                                 "narration": "Welcome to the future of productivity. Today we reveal a product that changes everything.",
                                 "visual_description": "Modern office, team celebrating", "b_roll": "startup office energy", "on_screen_text": "The Future is Here"},
                                {"name": "Problem", "duration_seconds": 40,
                                 "narration": "Every day, teams waste hours on repetitive tasks that slow them down.",
                                 "visual_description": "Frustrated workers at computers", "b_roll": "busy office workers", "on_screen_text": "Sound familiar?"},
                                {"name": "Solution", "duration_seconds": 50,
                                 "narration": "Introducing our AI-powered platform. Built for teams that move fast.",
                                 "visual_description": "Clean app interface demo", "b_roll": "technology innovation", "on_screen_text": "Introducing CineAI"}
                            ],
                            "call_to_action": "Sign up free at cineai.app",
                            "total_duration_seconds": 150
                        },
                        "scenes": [], "metadata": {}, "timeline": {}
                    }
                },
                {
                    "id": "v002", "title": "Travel Vlog Intro", "duration": "1:45",
                    "status": "done", "created": "2024-01-09", "topic": "Summer travel adventures",
                    "results": {
                        "script": {
                            "title": "Travel Vlog Intro",
                            "hook": "This summer I traveled to 5 countries in 30 days. Here is what I learned.",
                            "sections": [
                                {"name": "Opening", "duration_seconds": 20,
                                 "narration": "Pack your bags. We are going on an adventure across the world.",
                                 "visual_description": "Aerial travel shots", "b_roll": "airplane travel sky", "on_screen_text": "Summer 2024"},
                                {"name": "Destinations", "duration_seconds": 45,
                                 "narration": "From the beaches of Bali to the streets of Tokyo, every destination had something unique.",
                                 "visual_description": "Montage of travel destinations", "b_roll": "tropical beach paradise", "on_screen_text": "5 Countries"},
                                {"name": "Highlights", "duration_seconds": 40,
                                 "narration": "The food, the people, the culture. Travel changes you in ways you never expect.",
                                 "visual_description": "Street food markets, local culture", "b_roll": "street food market", "on_screen_text": "Unforgettable Moments"}
                            ],
                            "call_to_action": "Subscribe for more travel adventures!",
                            "total_duration_seconds": 105
                        },
                        "scenes": [], "metadata": {}, "timeline": {}
                    }
                }
            ],
            "created_at": "2024-01-01T00:00:00"
        }
        save_users(users)
