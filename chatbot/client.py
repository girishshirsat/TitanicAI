import streamlit as st
import requests
import uuid
import base64

API_URL = "https://titanicai.onrender.com"

st.set_page_config(
    page_title="TitanicAI",
    page_icon="🚢",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

    * { font-family: 'Inter', sans-serif; }

    .stApp {
        background: linear-gradient(135deg, #020817 0%, #0a0f2c 40%, #0d1340 100%);
        color: white;
    }

    #MainMenu, footer, header { visibility: hidden; }

    .hero-section {
        text-align: center;
        padding: 80px 20px 60px;
        background: linear-gradient(180deg, rgba(0,212,255,0.05) 0%, transparent 100%);
    }

    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: rgba(0,212,255,0.1);
        border: 1px solid rgba(0,212,255,0.3);
        border-radius: 50px;
        padding: 6px 16px;
        font-size: 13px;
        color: #00d4ff;
        margin-bottom: 28px;
    }

    .hero-title {
        font-size: clamp(2.5rem, 6vw, 5rem);
        font-weight: 900;
        line-height: 1.1;
        color: white;
        margin-bottom: 8px;
    }

    .hero-title span {
        background: linear-gradient(90deg, #00d4ff, #7c3aed);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .hero-subtitle {
        font-size: 1.1rem;
        color: rgba(255,255,255,0.6);
        max-width: 560px;
        margin: 0 auto 40px;
        line-height: 1.7;
    }

    .hero-stats {
        display: flex;
        justify-content: center;
        gap: 12px;
        margin-top: 20px;
        flex-wrap: wrap;
    }

    .stat-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 8px;
        padding: 6px 14px;
        font-size: 12px;
        color: rgba(255,255,255,0.7);
    }

    .stat-badge strong { color: #00d4ff; }

    .features-section {
        padding: 60px 20px;
        max-width: 1100px;
        margin: 0 auto;
    }

    .section-title {
        text-align: center;
        font-size: 2rem;
        font-weight: 800;
        color: white;
        margin-bottom: 8px;
    }

    .section-subtitle {
        text-align: center;
        color: rgba(255,255,255,0.5);
        margin-bottom: 48px;
        font-size: 0.95rem;
    }

    .features-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 20px;
    }

    @media (max-width: 768px) { .features-grid { grid-template-columns: 1fr; } }

    .feature-card {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 16px;
        padding: 28px;
        transition: border-color 0.3s;
    }

    .feature-card:hover { border-color: rgba(0,212,255,0.3); }

    .feature-icon {
        width: 48px;
        height: 48px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 22px;
        margin-bottom: 16px;
    }

    .feature-title {
        font-size: 1rem;
        font-weight: 700;
        color: white;
        margin-bottom: 8px;
    }

    .feature-desc {
        font-size: 0.85rem;
        color: rgba(255,255,255,0.5);
        line-height: 1.6;
    }

    .cta-section {
        text-align: center;
        padding: 80px 20px;
        background: linear-gradient(135deg, #1e3a8a 0%, #7c3aed 100%);
        border-radius: 24px;
        margin: 40px 20px;
    }

    .cta-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: white;
        margin-bottom: 12px;
    }

    .cta-subtitle {
        color: rgba(255,255,255,0.75);
        margin-bottom: 32px;
        font-size: 1rem;
    }

    .launch-btn {
        display: inline-block;
        background: white;
        color: #1e3a8a;
        border: none;
        border-radius: 10px;
        padding: 14px 36px;
        font-size: 1rem;
        font-weight: 700;
        cursor: pointer;
        text-decoration: none;
    }

    .nav-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 16px 32px;
        background: rgba(10,15,44,0.95);
        border-bottom: 1px solid rgba(255,255,255,0.07);
        position: sticky;
        top: 0;
        z-index: 100;
        backdrop-filter: blur(12px);
    }

    .nav-logo {
        font-size: 1.3rem;
        font-weight: 800;
        color: white;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .nav-logo span { color: #00d4ff; }

    .chat-container {
        max-width: 860px;
        margin: 0 auto;
        padding: 20px;
    }

    .chat-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 20px 28px;
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 16px 16px 0 0;
        margin-bottom: 0;
    }

    .chat-title {
        font-size: 1rem;
        font-weight: 700;
        color: white;
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .status-dot {
        width: 8px;
        height: 8px;
        background: #10b981;
        border-radius: 50%;
        display: inline-block;
    }

    .message-bubble-user {
        background: linear-gradient(135deg, #1e3a8a, #7c3aed);
        color: white;
        border-radius: 16px 16px 4px 16px;
        padding: 14px 18px;
        max-width: 80%;
        margin-left: auto;
        font-size: 0.92rem;
        line-height: 1.6;
        margin-bottom: 16px;
    }

    .message-bubble-ai {
        background: rgba(255,255,255,0.06);
        border: 1px solid rgba(255,255,255,0.1);
        color: rgba(255,255,255,0.9);
        border-radius: 16px 16px 16px 4px;
        padding: 14px 18px;
        max-width: 85%;
        font-size: 0.92rem;
        line-height: 1.7;
        margin-bottom: 16px;
    }

    .message-label {
        font-size: 11px;
        color: rgba(255,255,255,0.35);
        margin-bottom: 4px;
        font-weight: 600;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }

    .messages-area {
        background: rgba(5,10,30,0.8);
        border: 1px solid rgba(255,255,255,0.07);
        border-top: none;
        border-bottom: none;
        padding: 24px 28px;
        min-height: 420px;
        max-height: 520px;
        overflow-y: auto;
    }

    .input-area {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 0 0 16px 16px;
        padding: 16px 20px;
    }

    .suggestion-chip {
        display: inline-block;
        background: rgba(0,212,255,0.08);
        border: 1px solid rgba(0,212,255,0.2);
        border-radius: 50px;
        padding: 5px 14px;
        font-size: 12px;
        color: #00d4ff;
        cursor: pointer;
        margin: 4px;
        transition: background 0.2s;
    }

    .tech-section {
        padding: 60px 20px;
        max-width: 1100px;
        margin: 0 auto;
    }

    .tech-card {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 12px;
        padding: 18px 22px;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .tech-dot {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background: #00d4ff;
        flex-shrink: 0;
    }

    .tech-name { font-weight: 700; color: white; font-size: 0.95rem; }
    .tech-desc { color: rgba(255,255,255,0.45); font-size: 0.82rem; }

    .footer {
        background: rgba(5,10,30,0.9);
        border-top: 1px solid rgba(255,255,255,0.07);
        padding: 40px 32px 24px;
        margin-top: 60px;
    }

    .footer-brand { font-size: 1.1rem; font-weight: 800; color: white; margin-bottom: 6px; }
    .footer-tagline { color: rgba(255,255,255,0.4); font-size: 0.82rem; }
    .footer-copy {
        color: rgba(255,255,255,0.25);
        font-size: 0.78rem;
        text-align: center;
        margin-top: 32px;
        padding-top: 20px;
        border-top: 1px solid rgba(255,255,255,0.06);
    }

    div[data-testid="stTextInput"] input {
        background: rgba(255,255,255,0.06) !important;
        border: 1px solid rgba(255,255,255,0.12) !important;
        border-radius: 10px !important;
        color: white !important;
        padding: 12px 16px !important;
    }

    div[data-testid="stTextInput"] input:focus {
        border-color: #00d4ff !important;
        box-shadow: 0 0 0 2px rgba(0,212,255,0.15) !important;
    }

    .stButton button {
        background: linear-gradient(135deg, #1e3a8a, #7c3aed) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        padding: 10px 24px !important;
        transition: opacity 0.2s !important;
    }

    .stButton button:hover { opacity: 0.88 !important; }

    .stSpinner > div { border-top-color: #00d4ff !important; }

    .empty-state {
        text-align: center;
        padding: 60px 20px;
        color: rgba(255,255,255,0.3);
    }

    .empty-icon { font-size: 3rem; margin-bottom: 12px; }
    .empty-text { font-size: 0.9rem; }

    ::-webkit-scrollbar { width: 4px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.15); border-radius: 4px; }

    .nav-links a {
        color: rgba(255,255,255,0.6);
        text-decoration: none;
        font-size: 0.9rem;
        transition: color 0.2s;
    }
    .nav-links a:hover { color: #00d4ff; }

    .dev-links a {
        color: #00d4ff;
        text-decoration: none;
        font-size: 0.82rem;
        display: inline-flex;
        align-items: center;
        gap: 5px;
        padding: 4px 10px;
        border: 1px solid rgba(0,212,255,0.25);
        border-radius: 6px;
        transition: background 0.2s;
    }
    .dev-links a:hover { background: rgba(0,212,255,0.1); }

    .footer-link a {
        color: rgba(255,255,255,0.45);
        text-decoration: none;
        font-size: 0.82rem;
        transition: color 0.2s;
    }
    .footer-link a:hover { color: #00d4ff; }
</style>
""", unsafe_allow_html=True)

BRAIN_IMG_B64 = "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"

if "page" not in st.session_state:
    st.session_state.page = "home"
if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []


def new_chat_session():
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.messages = []
    st.session_state.page = "chat"


def go_home():
    if st.session_state.session_id:
        try:
            requests.delete(f"{API_URL}/session/{st.session_state.session_id}", timeout=3)
        except Exception:
            pass
    st.session_state.session_id = None
    st.session_state.messages = []
    st.session_state.page = "home"


def send_message(question: str):
    if not question.strip():
        return

    st.session_state.messages.append({"role": "user", "content": question})

    try:
        resp = requests.post(
            f"{API_URL}/chat",
            json={"session_id": st.session_state.session_id, "question": question},
            timeout=60,
        )
        data = resp.json()
        st.session_state.messages.append({
            "role": "ai",
            "content": data.get("answer", "Sorry, I couldn't process that."),
            "chart": data.get("chart_base64"),
        })
    except requests.exceptions.ConnectionError:
        st.session_state.messages.append({
            "role": "ai",
            "content": "⚠️ Cannot connect to the backend. Make sure `uvicorn main:app` is running on port 8000.",
            "chart": None,
        })
    except Exception as e:
        st.session_state.messages.append({
            "role": "ai",
            "content": f"⚠️ Error: {str(e)}",
            "chart": None,
        })


def render_home():
    st.markdown("""
    <div class="nav-bar">
        <div class="nav-logo">🚢 <span>TitanicAI</span></div>
        <div style="display:flex;align-items:center;gap:20px;">
            <div class="nav-links" style="display:flex;gap:20px;">
                <a href="#features">Features</a>
                <a href="#technology">Technology</a>
            </div>
            <div class="dev-links" style="display:flex;gap:8px;">
                <a href="https://github.com/girishshirsat" target="_blank">⚙️ GitHub</a>
                <a href="https://exploregms.wordpress.com/" target="_blank">🌐 Portfolio</a>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="hero-section">
        <div class="hero-badge">✨ AI-Powered Analytics</div>
        <div class="hero-title">Explore Titanic<br><span>Data with AI</span></div>
        <div class="hero-subtitle">
            Chat naturally with your data using our advanced AI chatbot.
            Powered by Mistral-Saba-24B, FastAPI, and LangChain for intelligent, conversational analytics.
        </div>
        <div class="hero-stats">
            <div class="stat-badge">📊 <strong>891</strong> Passengers</div>
            <div class="stat-badge">⚡ <strong>0.3s</strong> Response Time</div>
            <div class="stat-badge">🎯 <strong>98%</strong> Accuracy</div>
            <div class="stat-badge">💬 <strong>1000+</strong> Queries Processed</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🚀  Launch TitanicAI Chat →", use_container_width=True):
            new_chat_session()
            st.rerun()

    st.markdown("""
    <div class="features-section">
        <div class="section-title">Powerful Features</div>
        <div class="section-subtitle">Everything you need for intelligent data exploration</div>
        <div class="features-grid">
            <div class="feature-card">
                <div class="feature-icon" style="background:linear-gradient(135deg,#3b82f6,#1d4ed8)">🧠</div>
                <div class="feature-title">Conversational Memory</div>
                <div class="feature-desc">Context-aware responses with full conversation history. Ask follow-up questions naturally.</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon" style="background:linear-gradient(135deg,#7c3aed,#5b21b6)">📊</div>
                <div class="feature-title">Dynamic Visualization</div>
                <div class="feature-desc">Generate real-time graphs and charts from natural language queries instantly.</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon" style="background:linear-gradient(135deg,#ec4899,#be185d)">💬</div>
                <div class="feature-title">Natural Language Queries</div>
                <div class="feature-desc">No SQL required. Just ask questions in plain English and get intelligent answers.</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon" style="background:linear-gradient(135deg,#ef4444,#b91c1c)">🗄️</div>
                <div class="feature-title">Smart Data Interpretation</div>
                <div class="feature-desc">Advanced statistical analysis with aggregations, filtering, and grouping operations.</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon" style="background:linear-gradient(135deg,#f59e0b,#d97706)">⚡</div>
                <div class="feature-title">Lightning Fast</div>
                <div class="feature-desc">Powered by FastAPI and optimized algorithms for instant query responses.</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon" style="background:linear-gradient(135deg,#10b981,#059669)">📈</div>
                <div class="feature-title">Deep Insights</div>
                <div class="feature-desc">Uncover patterns and trends in the Titanic dataset with AI-driven analytics.</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_tech, col_img = st.columns([1, 1])
    with col_tech:
        st.markdown("""
        <div style="padding:40px 20px;">
            <div style="font-size:1.8rem;font-weight:800;color:white;margin-bottom:8px;">Cutting-Edge Technology</div>
            <div style="color:rgba(255,255,255,0.5);margin-bottom:32px;font-size:0.9rem;">Built with the latest AI and web technologies for optimal performance.</div>
            <div class="tech-card"><div class="tech-dot"></div><div><div class="tech-name">llama-3.3-70b-versatile</div><div class="tech-desc">Advanced language model</div></div></div>
            <div class="tech-card"><div class="tech-dot" style="background:#7c3aed"></div><div><div class="tech-name">LangChain</div><div class="tech-desc">LLM orchestration framework</div></div></div>
            <div class="tech-card"><div class="tech-dot" style="background:#f59e0b"></div><div><div class="tech-name">FastAPI</div><div class="tech-desc">High-performance backend</div></div></div>
            <div class="tech-card"><div class="tech-dot" style="background:#10b981"></div><div><div class="tech-name">Streamlit</div><div class="tech-desc">Interactive frontend</div></div></div>
            <div class="tech-card"><div class="tech-dot" style="background:#ef4444"></div><div><div class="tech-name">Pandas & NumPy</div><div class="tech-desc">Data processing powerhouse</div></div></div>
        </div>
        """, unsafe_allow_html=True)
    with col_img:
        st.markdown(f"""
        <div style="margin-top:80px;display:flex;align-items:flex-start;justify-content:center;padding:0 20px;">
            <div style="position:relative;border-radius:20px;overflow:hidden;width:100%;
                        border:1px solid rgba(0,212,255,0.2);
                        box-shadow:0 0 40px rgba(0,212,255,0.15), 0 0 80px rgba(124,58,237,0.1);">
                <img src="data:image/png;base64,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"
                     style="width:100%;display:block;border-radius:20px;opacity:0.92;" />
                <div style="position:absolute;inset:0;border-radius:20px;
                            background:linear-gradient(135deg,rgba(0,212,255,0.08),rgba(124,58,237,0.08));
                            pointer-events:none;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div class="cta-section">
        <div class="cta-title">Ready to Explore Your Data?</div>
        <div class="cta-subtitle">Start chatting with the Titanic dataset now. No setup required, just click and explore.</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🚀  Launch TitanicAI Chat", key="cta_btn", use_container_width=True):
            new_chat_session()
            st.rerun()

    st.markdown("""
    <div class="footer">
        <div style="display:flex;justify-content:space-between;flex-wrap:wrap;gap:32px;">
            <div>
                <div class="footer-brand">🚢 TitanicAI</div>
                <div class="footer-tagline">AI-powered conversational analytics<br>for exploring the Titanic dataset.</div>
                <div class="dev-links" style="display:flex;gap:8px;margin-top:14px;">
                    <a href="https://github.com/girishshirsat" target="_blank">⚙️ GitHub</a>
                    <a href="https://exploregms.wordpress.com/" target="_blank">🌐 Portfolio</a>
                </div>
            </div>
            <div>
                <div style="font-weight:700;color:white;margin-bottom:12px;">Product</div>
                <div style="font-size:0.85rem;line-height:2.2;" class="footer-link">
                    <div><a href="#">Features</a></div>
                    <div><a href="#">Technology</a></div>
                    <div><a href="#">Chat</a></div>
                </div>
            </div>
            <div>
                <div style="font-weight:700;color:white;margin-bottom:12px;">Developer</div>
                <div style="font-size:0.85rem;line-height:2.2;" class="footer-link">
                    <div><a href="https://github.com/girishshirsat" target="_blank">⚙️ GitHub Profile</a></div>
                    <div><a href="https://exploregms.wordpress.com/" target="_blank">🌐 Portfolio</a></div>
                    <div><a href="https://github.com/girishshirsat/TitanicAI" target="_blank">📁 Source Code</a></div>
                </div>
            </div>
        </div>
        <div class="footer-copy">© 2026 TitanicAI. Built with FastAPI, Groq & LLaMA-3.3-70B &nbsp;|&nbsp;
            Made by <a href="https://exploregms.wordpress.com/" target="_blank" style="color:#00d4ff;text-decoration:none;">Girish Shirsat</a>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_chat():
    st.markdown("""
    <div class="nav-bar">
        <div class="nav-logo">🚢 <span>TitanicAI</span></div>
        <div style="display:flex;align-items:center;gap:16px;">
            <div style="color:rgba(255,255,255,0.4);font-size:0.85rem;">AI Chat • Titanic Dataset Explorer</div>
            <div class="dev-links" style="display:flex;gap:8px;">
                <a href="https://github.com/girishshirsat" target="_blank">⚙️ GitHub</a>
                <a href="https://exploregms.wordpress.com/" target="_blank">🌐 Portfolio</a>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_main, col_side = st.columns([3, 1])

    with col_main:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)

        st.markdown(f"""
        <div class="chat-header">
            <div class="chat-title">
                <span class="status-dot"></span>
                TitanicAI Chat
            </div>
            <div style="font-size:11px;color:rgba(255,255,255,0.3);">
                Session: {str(st.session_state.session_id)[:8]}...
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="messages-area">', unsafe_allow_html=True)

        if not st.session_state.messages:
            st.markdown("""
            <div class="empty-state">
                <div class="empty-icon">🚢</div>
                <div class="empty-text">Ask me anything about the Titanic dataset!<br>
                Try: "What was the survival rate?" or "Show me a histogram of ages"</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            for msg in st.session_state.messages:
                if msg["role"] == "user":
                    st.markdown(f"""
                    <div style="text-align:right">
                        <div class="message-label">You</div>
                        <div class="message-bubble-user">{msg["content"]}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div>
                        <div class="message-label">🤖 TitanicAI</div>
                        <div class="message-bubble-ai">{msg["content"]}</div>
                    </div>
                    """, unsafe_allow_html=True)

                    if msg.get("chart"):
                        img_data = msg["chart"]
                        st.markdown(
                            f'<div style="margin:8px 0 16px;border-radius:12px;overflow:hidden;border:1px solid rgba(255,255,255,0.08);">'
                            f'<img src="data:image/png;base64,{img_data}" style="width:100%;display:block;" />'
                            f'</div>',
                            unsafe_allow_html=True,
                        )

        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="input-area">', unsafe_allow_html=True)

        suggestions = [
            "What % were male?",
            "Show age histogram",
            "Average ticket fare?",
            "Embarked port counts",
            "Survival by gender",
        ]
        cols = st.columns(len(suggestions))
        for i, (col, s) in enumerate(zip(cols, suggestions)):
            with col:
                if st.button(s, key=f"sug_{i}", use_container_width=True):
                    with st.spinner("Thinking..."):
                        send_message(s)
                    st.rerun()

        with st.form("chat_form", clear_on_submit=True):
            col_input, col_btn = st.columns([5, 1])
            with col_input:
                user_input = st.text_input(
                    "message",
                    placeholder="Ask anything about the Titanic dataset...",
                    label_visibility="collapsed",
                )
            with col_btn:
                submitted = st.form_submit_button("Send →", use_container_width=True)

            if submitted and user_input:
                with st.spinner("Thinking..."):
                    send_message(user_input)
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_side:
        st.markdown("""
        <div style="padding:20px 8px;">
            <div style="font-weight:700;color:white;margin-bottom:16px;font-size:0.95rem;">📊 Quick Stats</div>
        </div>
        """, unsafe_allow_html=True)

        stats = [
            ("🧑‍🤝‍🧑", "Passengers", "891"),
            ("💀", "Survival Rate", "38.4%"),
            ("👨", "Male", "64.8%"),
            ("👩", "Female", "35.2%"),
            ("📅", "Avg Age", "29.7 yrs"),
            ("💰", "Avg Fare", "$32.20"),
        ]

        for icon, label, value in stats:
            st.markdown(f"""
            <div style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.07);
                        border-radius:10px;padding:12px 14px;margin-bottom:10px;">
                <div style="font-size:11px;color:rgba(255,255,255,0.4);margin-bottom:2px;">{icon} {label}</div>
                <div style="font-size:1.1rem;font-weight:700;color:#00d4ff;">{value}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🏠 Back to Home", use_container_width=True):
            go_home()
            st.rerun()

        if st.button("🗑️ Clear Chat", use_container_width=True):
            if st.session_state.session_id:
                try:
                    requests.delete(f"{API_URL}/session/{st.session_state.session_id}", timeout=3)
                except Exception:
                    pass
            st.session_state.session_id = str(uuid.uuid4())
            st.session_state.messages = []
            st.rerun()

        st.markdown("""
        <div style="margin-top:24px;padding:14px;background:rgba(0,212,255,0.06);
                    border:1px solid rgba(0,212,255,0.15);border-radius:10px;">
            <div style="font-size:11px;color:#00d4ff;font-weight:600;margin-bottom:6px;">💡 Memory Active</div>
            <div style="font-size:11px;color:rgba(255,255,255,0.45);line-height:1.5;">
                Your conversation is remembered within this session. Starting a new chat clears the context.
            </div>
        </div>
        """, unsafe_allow_html=True)


if st.session_state.page == "home":
    render_home()
elif st.session_state.page == "chat":
    render_chat()