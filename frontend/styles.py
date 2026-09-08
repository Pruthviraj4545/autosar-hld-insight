import streamlit as st


def inject_css() -> None:
	st.markdown(
		"""
		<style>
		@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Space+Grotesk:wght@400;500;600;700&display=swap');
		:root { --ink:#101b2d; --ink-soft:#172740; --paper:#f4f1ea; --muted:#9cafc4; --cyan:#72e0db; --amber:#ffc978; --line:rgba(171,198,220,.18); }
		.stApp { background: radial-gradient(circle at 75% 0%, #203a57 0, transparent 38%), linear-gradient(135deg, #0d1828 0%, #152841 58%, #102033 100%); color:var(--paper); font-family:'Space Grotesk', sans-serif; }
		[data-testid="stSidebar"] { background:#0b1625; border-right:1px solid var(--line); }
		[data-testid="stSidebar"] > div:first-child { padding-top:2rem; }
		[data-testid="stSidebarNavLink"][href$="/"] { display:none !important; }
		[data-testid="stAppDeployButton"], .stAppDeployButton, [data-testid="stToolbar"], [data-testid="stBaseButton-header"] { display:none !important; }
		.anchor-link { display:none !important; }
		h1,h2,h3,h4,p,span,label { font-family:'Space Grotesk', sans-serif; }
		h1 { letter-spacing:-.03em; font-size:clamp(2.2rem, 6vw, 5.4rem); line-height:.98; }
		h2 { letter-spacing:-.02em; }
		.hero { padding:3.5rem 0 2.5rem; border-bottom:1px solid var(--line); }
		.eyebrow { color:var(--cyan); font:500 .72rem 'DM Mono', monospace; letter-spacing:.14em; text-transform:uppercase; }
		.hero-copy { max-width:700px; color:#c5d3df; font-size:1.12rem; line-height:1.6; }
		.card { background:rgba(25,45,70,.82); border:1px solid var(--line); border-radius:12px; padding:1.25rem; height:100%; box-shadow:0 16px 38px rgba(0,0,0,.15); }
		.card h3 { margin:.55rem 0 .35rem; color:#fff; }
		.card p { color:var(--muted); line-height:1.5; margin:0; }
		.feature-mark { color:var(--amber); font-size:1.6rem; }
		.status-card { background:linear-gradient(120deg, rgba(114,224,219,.14), rgba(255,201,120,.08)); border:1px solid rgba(114,224,219,.35); border-radius:10px; padding:1rem; }
		.status-label { color:var(--muted); font:500 .68rem 'DM Mono', monospace; letter-spacing:.1em; text-transform:uppercase; }
		.status-value { color:#fff; font-size:1.05rem; font-weight:600; overflow-wrap:anywhere; }
		.section-rule { border-top:1px solid var(--line); margin:2.3rem 0 1.4rem; padding-top:1.2rem; }
		.source-card { border-left:3px solid var(--cyan); background:rgba(114,224,219,.08); padding:.75rem 1rem; margin:.5rem 0; border-radius:0 8px 8px 0; }
		.warning-card { border-left:3px solid var(--amber); background:rgba(255,201,120,.1); padding:1rem 1.1rem; margin:.8rem 0; border-radius:0 10px 10px 0; }
		.chat-user { background:#23415f; border-radius:12px 12px 3px 12px; padding:1rem 1.1rem; margin:.7rem 0 .25rem 12%; }
		.chat-ai { background:rgba(255,255,255,.08); border:1px solid var(--line); border-radius:12px 12px 12px 3px; padding:1rem 1.1rem; margin:.25rem 12% .9rem 0; }
		.metric-label { color:var(--muted); font:500 .68rem 'DM Mono', monospace; text-transform:uppercase; letter-spacing:.08em; }
		.metric-value { color:#fff; font-size:2rem; font-weight:700; }
		footer { color:#71869d; font:400 .72rem 'DM Mono', monospace; border-top:1px solid var(--line); margin-top:3rem; padding-top:1rem; }
		.stButton > button { border-radius:8px; border:1px solid rgba(114,224,219,.35); background:#72e0db; color:#0b1928; font-weight:700; padding:.65rem 1rem; }
		.stButton > button:hover { border-color:#ffc978; background:#ffc978; color:#101b2d; }
		.stTextInput input, .stTextArea textarea { background:rgba(255,255,255,.07); color:#fff; border:1px solid var(--line); border-radius:8px; }
		[data-testid="stFileUploader"] { background:rgba(255,255,255,.045); border:1px dashed rgba(114,224,219,.45); border-radius:10px; padding:.6rem; }
		[data-testid="stMetric"] { background:rgba(25,45,70,.82); border:1px solid var(--line); border-radius:10px; padding:.8rem; }
		</style>
		""",
		unsafe_allow_html=True,
	)


def page_header(eyebrow: str, title: str, description: str) -> None:
	st.markdown(f'<div class="eyebrow">{eyebrow}</div>', unsafe_allow_html=True)
	st.title(title)
	st.markdown(f'<p class="hero-copy">{description}</p>', unsafe_allow_html=True)


def active_project() -> str:
	return st.session_state.get("project_id", "").strip()


def require_project() -> str | None:
	project_id = active_project()
	if not project_id:
		st.warning("Choose an active project on the Home page before using this workspace.")
		return None
	return project_id