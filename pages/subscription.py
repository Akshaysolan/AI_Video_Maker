import streamlit as st
from utils.auth import update_user_in_db

def render_subscription():
    plan = st.session_state.get("plan", "free")
    videos_used = st.session_state.get("videos_generated", 0)

    st.markdown("""
    <div class="page-header">💎 Subscription Plans</div>
    <div class="page-sub">Unlock unlimited video generation and premium features.</div>
    """, unsafe_allow_html=True)

    if plan == "pro":
        st.markdown("""
        <div style="background:linear-gradient(135deg, rgba(255,107,53,0.15), rgba(255,159,28,0.1));
            border:2px solid var(--accent); border-radius:20px; padding:2rem; text-align:center; margin-bottom:2rem;">
            <div style="font-size:3rem;">⭐</div>
            <div style="font-family:'Syne',sans-serif; font-size:2rem; font-weight:800; color:var(--accent2);">
                You're on PRO!
            </div>
            <div style="color:var(--muted); margin-top:0.5rem;">
                Enjoy unlimited video generation and all premium features.
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Plans
    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(f"""
        <div class="plan-card {'featured' if plan == 'free' else ''}">
            <div style="font-family:'Syne',sans-serif; font-size:1.2rem; font-weight:800; margin-bottom:1rem;">
                🆓 Free
            </div>
            <div class="plan-price">$0</div>
            <div class="plan-period">forever</div>
            <hr style="margin:1.5rem 0;">
            <div style="text-align:left; color:var(--muted); font-size:0.85rem; line-height:2.2;">
                ✅ 5 videos total<br>
                ✅ Up to 5 min each<br>
                ✅ All 4 AI agents<br>
                ✅ Script + shot list<br>
                ✅ SEO metadata<br>
                ❌ Priority processing<br>
                ❌ Custom templates<br>
                ❌ API access<br>
            </div>
            <br>
            <div style="color:var(--muted); font-size:0.85rem; padding:0.75rem; background:var(--surface2); border-radius:8px;">
                {videos_used}/5 videos used
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div class="plan-card featured" style="position:relative;">
            <div style="position:absolute; top:-12px; left:50%; transform:translateX(-50%);
                background:linear-gradient(135deg,#FF6B35,#FF9F1C); color:white;
                padding:4px 16px; border-radius:20px; font-size:0.75rem; font-weight:700;">
                MOST POPULAR
            </div>
            <div style="font-family:'Syne',sans-serif; font-size:1.2rem; font-weight:800; margin-bottom:1rem;">
                ⭐ PRO
            </div>
            <div class="plan-price">$9.99</div>
            <div class="plan-period">per month</div>
            <hr style="margin:1.5rem 0;">
            <div style="text-align:left; color:var(--muted); font-size:0.85rem; line-height:2.2;">
                ✅ Unlimited videos<br>
                ✅ Up to 5 min each<br>
                ✅ All 4 AI agents<br>
                ✅ Script + shot list<br>
                ✅ SEO metadata<br>
                ✅ Priority processing<br>
                ✅ Custom templates<br>
                ❌ API access<br>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if plan != "pro":
            st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
            if st.button("🚀 Upgrade to PRO", use_container_width=True, key="upgrade_pro"):
                _upgrade_user("pro")
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.success("✅ Current Plan")

    with c3:
        st.markdown("""
        <div class="plan-card">
            <div style="font-family:'Syne',sans-serif; font-size:1.2rem; font-weight:800; margin-bottom:1rem;">
                🏢 Enterprise
            </div>
            <div class="plan-price">$49</div>
            <div class="plan-period">per month</div>
            <hr style="margin:1.5rem 0;">
            <div style="text-align:left; color:var(--muted); font-size:0.85rem; line-height:2.2;">
                ✅ Unlimited videos<br>
                ✅ Up to 5 min each<br>
                ✅ All 4 AI agents<br>
                ✅ Script + shot list<br>
                ✅ SEO metadata<br>
                ✅ Priority processing<br>
                ✅ Custom templates<br>
                ✅ API access<br>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("📧 Contact Sales", use_container_width=True, key="contact_sales"):
            st.info("Email: sales@cineai.app")

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("### ❓ FAQ")
    faqs = [
        ("Do I need a credit card for the free plan?", "No! Sign up with just your email and get 5 free video packages immediately. No credit card required."),
        ("What does 'video package' include?", "Each package includes: full narration script, scene-by-scene shot list, B-roll suggestions, SEO metadata, thumbnail concepts, and a production timeline."),
        ("Does CineAI actually render videos?", "CineAI generates comprehensive video production packages using AI. It creates scripts, shot lists, and all documentation needed to produce your video."),
        ("Can I cancel my subscription?", "Yes, cancel anytime from your account settings. You keep access until the end of your billing period."),
        ("What's the maximum video duration?", "All plans support up to 5-minute videos (300 seconds). This is optimized for social media and engagement."),
    ]
    for q, a in faqs:
        with st.expander(q):
            st.markdown(f'<div style="color:var(--muted); font-size:0.9rem; line-height:1.8;">{a}</div>', unsafe_allow_html=True)


def _upgrade_user(new_plan):
    email = st.session_state.user["email"]
    st.session_state.plan = new_plan
    update_user_in_db(email, {"plan": new_plan})
    st.success(f"🎉 You're now on the {new_plan.upper()} plan! Enjoy unlimited video generation.")
    st.balloons()
    st.rerun()
