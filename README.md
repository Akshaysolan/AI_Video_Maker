# 🎬 CineAI — AI Video Maker

Transform any text into a complete video production package using AI agents, RAG, and LLM technology.

## 🚀 Tech Stack

| Component | Technology |
|-----------|-----------|
| **Frontend** | Streamlit |
| **LLM** | Anthropic Claude (claude-opus-4-5) |
| **RAG** | In-memory vector knowledge base |
| **Agents** | 4 specialized AI agents |
| **Auth** | JSON-based user store |
| **Deployment** | Streamlit Cloud |

## 🤖 AI Agents

1. **Script Agent** — RAG-enhanced narration & structure writing
2. **Scene Agent** — Shot lists, cinematography, color direction
3. **Metadata Agent** — SEO titles, tags, thumbnail concepts
4. **Production Agent** — Timeline, equipment, software recommendations

## 💰 Plans

- **Free**: 5 videos total (forever)
- **PRO**: $9.99/month — Unlimited videos
- **Enterprise**: $49/month — API access + unlimited

## 🛠️ Local Setup

```bash
# 1. Clone / extract project
cd ai_video_maker

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set API key
export GROQ_API_KEY=gsk_...r-key

# 4. Run
streamlit run app.py
```

## ☁️ Deploy to Streamlit Cloud

1. Push to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repo, set main file: `app.py`
4. Add secrets:
   ```toml
   GROQ_API_KEY = "gsk_your_key_here"
   ```
5. Deploy! 🎉

## 📁 Project Structure

```
ai_video_maker/
├── app.py                    # Main Streamlit entry point
├── requirements.txt
├── .streamlit/
│   └── config.toml           # Theme & server config
├── utils/
│   ├── ai_engine.py          # RAG + LLM + 4 AI Agents
│   ├── auth.py               # Signup/login/quota management
│   └── styles.py             # Global CSS theming
├── pages/
│   ├── dashboard.py          # Home dashboard
│   ├── video_generator.py    # Main video creation page
│   ├── my_videos.py          # Video history
│   └── subscription.py       # Plan management
└── data/
    └── users.json            # Auto-created user database
```

## 🎯 Features

- ✅ Text-to-video package generation
- ✅ Up to 5-minute videos
- ✅ Free tier (5 videos) + paid subscription
- ✅ 4 specialized AI agents with RAG
- ✅ Full script with narration
- ✅ Professional shot lists
- ✅ SEO metadata & thumbnail ideas
- ✅ Production timeline & equipment list
- ✅ Download packages as JSON/Markdown
- ✅ User authentication & quota enforcement
- ✅ Dark cinematic UI

## 🔑 Demo Account

- Email: `test@demo.com`
- Password: `demo123`
