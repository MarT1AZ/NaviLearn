import asyncio
import streamlit as st
from llm_recommendation import run_recommendation, ContentRecommendationList
 
# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="YT Tech Recommender",
    page_icon="▶",
    layout="centered",
)
 
# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;600&display=swap');
 
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background-color: #0e0e11; color: #e8e8f0; }
h1, h2, h3 { font-family: 'DM Mono', monospace !important; color: #e8e8f0 !important; }
 
.stTextArea textarea {
    background-color: #1a1a22 !important;
    border: 1px solid #2e2e3e !important;
    border-radius: 10px !important;
    color: #e8e8f0 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.95rem !important;
}
.stTextArea textarea:focus {
    border-color: #e8445a !important;
    box-shadow: 0 0 0 2px rgba(232,68,90,0.2) !important;
}
.stButton > button {
    background: linear-gradient(135deg, #e8445a, #f07060) !important;
    color: white !important; border: none !important;
    border-radius: 10px !important; padding: 0.55rem 2rem !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.9rem !important; width: 100%;
    transition: opacity 0.2s ease !important;
}
.stButton > button:hover { opacity: 0.85 !important; }
 
.card {
    background: #1a1a22; border: 1px solid #2e2e3e;
    border-radius: 12px; padding: 1.2rem 1.4rem; margin-bottom: 1rem;
}
.card-video  { border-left: 3px solid #5e9cf5; }
.card-playlist { border-left: 3px solid #7c6af7; }
 
.tag {
    display: inline-block; background: #2e2e3e; border-radius: 6px;
    padding: 2px 10px; font-family: 'DM Mono', monospace;
    font-size: 0.73rem; color: #aaaacc; margin-right: 6px; margin-bottom: 4px;
}
.section-title {
    font-family: 'DM Mono', monospace; font-size: 0.78rem;
    color: #e8445a; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 0.6rem;
}
.note-box {
    background: #1a1a22; border: 1px dashed #3e3e55;
    border-radius: 10px; padding: 1rem 1.2rem;
    color: #8888aa; font-size: 0.9rem; margin-top: 1.5rem;
}
hr { border-color: #2e2e3e !important; }
</style>
""", unsafe_allow_html=True)
 
 
# ── Render helpers ────────────────────────────────────────────────────────────
 
def render_video(i, video):
    st.markdown(f"""
    <div class="card card-video">
        <div class="section-title">▶ Video {i}</div>
        <strong style="font-size:1.05rem">{video.name}</strong><br><br>
        <span class="tag">⏱ {video.duration_minute} min</span>
        <span class="tag">📺 {video.channel}</span>
        <span class="tag">📅 {video.date_published}</span>
        <br><br>
        <div style="color:#c8c8e0;font-size:0.93rem;line-height:1.7">{video.content_summary}</div>
        <br>
        <div style="color:#8888aa;font-size:0.88rem">💬 {video.overall_comment_opinion_or_sentiment}</div>
        <br>
        <div style="color:#6666aa;font-size:0.83rem;font-style:italic">📝 {video.note}</div>
    </div>
    """, unsafe_allow_html=True)
 
 
def render_playlist(i, pl):
    bullets = "".join(f"<li>{b}</li>" for b in pl.bulletpoints)
    st.markdown(f"""
    <div class="card card-playlist">
        <div class="section-title">🗂 Playlist {i}</div>
        <strong style="font-size:1.05rem">{pl.name}</strong><br><br>
        <span class="tag">⏱ {pl.total_duration_hour}h total</span>
        <span class="tag">📺 {pl.channel}</span>
        <span class="tag">📅 {pl.first_published_year} → {pl.latest_update_year}</span>
        <br><br>
        <ul style="color:#c8c8e0;font-size:0.9rem;line-height:1.8;padding-left:1.2rem">{bullets}</ul>
        <div style="color:#c8c8e0;font-size:0.93rem;line-height:1.7">{pl.content_summary}</div>
        <br>
        <div style="color:#8888aa;font-size:0.88rem">💬 {pl.overall_comment_opinion_or_sentiment}</div>
        <br>
        <div style="color:#6666aa;font-size:0.83rem;font-style:italic">📝 {pl.note}</div>
    </div>
    """, unsafe_allow_html=True)
 
 
def render_results(result: ContentRecommendationList, tokens: int):
    st.markdown("---")
 
    st.markdown("### Recommended Videos")
    if result.recommended_videos:
        for i, v in enumerate(result.recommended_videos, 1):
            render_video(i, v)
    else:
        st.markdown('<div class="card" style="color:#555577">No videos recommended.</div>', unsafe_allow_html=True)
 
    st.markdown("### Recommended Playlists")
    if result.recommended_playlist:
        for i, pl in enumerate(result.recommended_playlist, 1):
            render_playlist(i, pl)
    else:
        st.markdown('<div class="card" style="color:#555577">No playlists recommended.</div>', unsafe_allow_html=True)
 
    st.markdown(f'<div class="note-box">📋 <strong>Final note:</strong> {result.final_note}</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div style="text-align:right;font-family:'DM Mono',monospace;font-size:0.75rem;color:#444466;margin-top:1rem">
        tokens used: {tokens:,}
    </div>
    """, unsafe_allow_html=True)
 
 
# ── Main UI ───────────────────────────────────────────────────────────────────
 
st.markdown("## ▶ YT Tech Recommender")
st.caption("Finds and summarises the best YouTube tutorials for your query.")
st.markdown("---")
 
query = st.text_area(
    "What do you want to learn?",
    placeholder="e.g. Advanced AWS for ML engineers, FastAPI for beginners…",
    height=110,
    label_visibility="collapsed",
)
 
submit = st.button("Find recommendations ↗")
 
if submit:
    if not query.strip():
        st.warning("Please enter a query first.")
    else:
        with st.spinner("Searching YouTube and analysing content… this may take a minute."):
            result, tokens = asyncio.run(run_recommendation(query))
        render_results(result, tokens)