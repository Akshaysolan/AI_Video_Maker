import streamlit as st

def inject_styles():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

    :root {
        --bg: #080B14;
        --surface: #0D1221;
        --surface2: #131929;
        --border: #1E2A3D;
        --accent: #FF6B35;
        --accent2: #FF9F1C;
        --blue: #3B82F6;
        --purple: #8B5CF6;
        --text: #E2E8F0;
        --muted: #64748B;
        --success: #10B981;
    }

    .stApp {
        background: var(--bg) !important;
        font-family: 'DM Sans', sans-serif !important;
        color: var(--text) !important;
    }

    .stApp > header { display: none !important; }

    section[data-testid="stSidebar"] {
        background: var(--surface) !important;
        border-right: 1px solid var(--border) !important;
        width: 260px !important;
    }

    section[data-testid="stSidebar"] > div { padding: 1.5rem 1rem !important; }

    .sidebar-logo {
        display: flex; align-items: center; gap: 10px;
        padding: 0.5rem 0 1.5rem;
    }
    .logo-icon { font-size: 2rem; }
    .logo-text {
        font-family: 'Syne', sans-serif;
        font-size: 1.6rem; font-weight: 800;
        background: linear-gradient(135deg, var(--accent), var(--accent2));
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }

    .sidebar-tagline p {
        color: var(--muted); font-size: 0.85rem; line-height: 1.6;
        padding: 0.5rem 0;
    }

    .user-card {
        display: flex; align-items: center; gap: 12px;
        background: var(--surface2); border: 1px solid var(--border);
        border-radius: 12px; padding: 12px;
    }
    .user-avatar {
        width: 40px; height: 40px; border-radius: 50%;
        background: linear-gradient(135deg, var(--accent), var(--purple));
        display: flex; align-items: center; justify-content: center;
        font-family: 'Syne', sans-serif; font-weight: 800; font-size: 1.1rem;
        color: white;
    }
    .user-name { font-weight: 600; font-size: 0.9rem; color: var(--text); }
    .user-plan { font-size: 0.75rem; margin-top: 2px; font-weight: 500; }
    .plan-free { color: var(--muted); }
    .plan-pro { color: var(--accent2); }

    .stButton > button {
        background: transparent !important;
        border: 1px solid var(--border) !important;
        color: var(--text) !important;
        border-radius: 8px !important;
        font-family: 'DM Sans', sans-serif !important;
        font-size: 0.875rem !important;
        padding: 0.5rem 1rem !important;
        transition: all 0.2s !important;
    }
    .stButton > button:hover {
        background: var(--surface2) !important;
        border-color: var(--accent) !important;
        color: var(--accent) !important;
    }

    .primary-btn > button {
        background: linear-gradient(135deg, var(--accent), var(--accent2)) !important;
        border: none !important; color: white !important;
        font-weight: 600 !important; font-size: 1rem !important;
        padding: 0.75rem 2rem !important; border-radius: 10px !important;
    }
    .primary-btn > button:hover {
        opacity: 0.9 !important; transform: translateY(-1px);
        box-shadow: 0 8px 25px rgba(255,107,53,0.3) !important;
    }

    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div {
        background: var(--surface2) !important;
        border: 1px solid var(--border) !important;
        color: var(--text) !important;
        border-radius: 10px !important;
        font-family: 'DM Sans', sans-serif !important;
    }
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 2px rgba(255,107,53,0.15) !important;
    }

    .stSlider > div > div > div { background: var(--accent) !important; }

    label, .stTextInput label, .stTextArea label, .stSelectbox label {
        color: var(--text) !important; font-weight: 500 !important;
    }

    .metric-card {
        background: var(--surface); border: 1px solid var(--border);
        border-radius: 16px; padding: 1.5rem;
        transition: border-color 0.2s;
    }
    .metric-card:hover { border-color: var(--accent); }
    .metric-icon { font-size: 1.8rem; margin-bottom: 0.5rem; }
    .metric-value {
        font-family: 'Syne', sans-serif; font-size: 2rem;
        font-weight: 800; color: var(--text);
    }
    .metric-label { color: var(--muted); font-size: 0.85rem; margin-top: 4px; }

    .page-header {
        font-family: 'Syne', sans-serif; font-size: 2.2rem;
        font-weight: 800; color: var(--text); margin-bottom: 0.25rem;
    }
    .page-sub { color: var(--muted); font-size: 1rem; margin-bottom: 2rem; }

    .video-card {
        background: var(--surface); border: 1px solid var(--border);
        border-radius: 16px; overflow: hidden; transition: all 0.2s;
    }
    .video-card:hover {
        border-color: var(--accent);
        box-shadow: 0 8px 32px rgba(255,107,53,0.1);
        transform: translateY(-2px);
    }
    .video-thumb {
        width: 100%; aspect-ratio: 16/9;
        background: linear-gradient(135deg, var(--surface2), var(--border));
        display: flex; align-items: center; justify-content: center;
        font-size: 3rem;
    }
    .video-info { padding: 1rem; }
    .video-title { font-weight: 600; font-size: 0.95rem; color: var(--text); margin-bottom: 4px; }
    .video-meta { color: var(--muted); font-size: 0.8rem; }
    .video-badge {
        display: inline-block; padding: 2px 8px; border-radius: 20px;
        font-size: 0.7rem; font-weight: 600; margin-top: 6px;
    }
    .badge-done { background: rgba(16,185,129,0.15); color: var(--success); }
    .badge-process { background: rgba(59,130,246,0.15); color: var(--blue); }

    .alert-box {
        border-radius: 12px; padding: 1rem 1.25rem;
        border-left: 3px solid;
    }
    .alert-warning { background: rgba(255,159,28,0.1); border-color: var(--accent2); color: var(--accent2); }
    .alert-info { background: rgba(59,130,246,0.1); border-color: var(--blue); color: var(--blue); }
    .alert-success { background: rgba(16,185,129,0.1); border-color: var(--success); color: var(--success); }

    .step-card {
        background: var(--surface); border: 1px solid var(--border);
        border-radius: 12px; padding: 1.25rem;
        display: flex; gap: 1rem; align-items: flex-start;
    }
    .step-num {
        width: 32px; height: 32px; border-radius: 50%; flex-shrink: 0;
        background: linear-gradient(135deg, var(--accent), var(--accent2));
        display: flex; align-items: center; justify-content: center;
        font-family: 'Syne', sans-serif; font-weight: 800; font-size: 0.9rem; color: white;
    }
    .step-content h4 { margin: 0 0 4px; font-family: 'Syne', sans-serif; font-weight: 700; color: var(--text); }
    .step-content p { margin: 0; color: var(--muted); font-size: 0.85rem; }

    .plan-card {
        background: var(--surface); border: 2px solid var(--border);
        border-radius: 20px; padding: 2rem; text-align: center;
        transition: all 0.3s;
    }
    .plan-card.featured {
        border-color: var(--accent);
        background: linear-gradient(135deg, rgba(255,107,53,0.05), rgba(255,159,28,0.05));
    }
    .plan-price {
        font-family: 'Syne', sans-serif; font-size: 3rem;
        font-weight: 800; color: var(--text);
    }
    .plan-period { color: var(--muted); font-size: 0.9rem; }

    .progress-bar-outer {
        background: var(--border); border-radius: 100px;
        height: 8px; overflow: hidden; margin: 8px 0;
    }
    .progress-bar-inner {
        height: 100%; border-radius: 100px;
        background: linear-gradient(90deg, var(--accent), var(--accent2));
        transition: width 0.5s;
    }

    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, var(--accent), var(--accent2)) !important;
    }

    div[data-testid="stMarkdownContainer"] h1,
    div[data-testid="stMarkdownContainer"] h2,
    div[data-testid="stMarkdownContainer"] h3 {
        font-family: 'Syne', sans-serif !important; color: var(--text) !important;
    }

    .stTabs [data-baseweb="tab-list"] {
        background: var(--surface) !important;
        border-radius: 10px !important; gap: 4px; padding: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        color: var(--muted) !important;
        border-radius: 8px !important;
        font-family: 'DM Sans', sans-serif !important;
    }
    .stTabs [aria-selected="true"] {
        background: var(--accent) !important;
        color: white !important;
    }

    hr { border-color: var(--border) !important; }

    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: var(--bg); }
    ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
    
    /* Previous styles remain... */
    
    /* Image hover effects */
    .image-hover {
        transition: transform 0.3s, box-shadow 0.3s;
    }
    .image-hover:hover {
        transform: scale(1.02);
        box-shadow: 0 10px 30px rgba(255,107,53,0.3);
    }
    
    /* Colorful badges */
    .color-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        margin: 2px;
        transition: transform 0.2s;
    }
    .color-badge:hover {
        transform: translateY(-2px);
    }
    
    /* Animated gradient borders */
    @keyframes borderGlow {
        0% { border-color: #ff6b6b; }
        25% { border-color: #4ecdc4; }
        50% { border-color: #45b7d1; }
        75% { border-color: #96ceb4; }
        100% { border-color: #ff6b6b; }
    }
    .gradient-border {
        border: 2px solid;
        animation: borderGlow 4s linear infinite;
    }
    </style>
    """, unsafe_allow_html=True)
    
    


