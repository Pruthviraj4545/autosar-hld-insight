from pathlib import Path

import streamlit as st

from styles import inject_css


st.set_page_config(page_title="AUTOSAR HLD Insight", page_icon="◈", layout="wide", initial_sidebar_state="expanded")
inject_css()

pages_dir = Path(__file__).parent / "pages"
pages = [
	st.Page(str(pages_dir / "0_Home.py"), title="Overview", icon=":material/home:"),
	st.Page(str(pages_dir / "1_Upload_Document.py"), title="Upload Document", icon=":material/upload_file:"),
	st.Page(str(pages_dir / "2_Ask_Questions.py"), title="Ask Questions", icon=":material/forum:"),
	st.Page(str(pages_dir / "3_Entity_Extraction.py"), title="Entity Extraction", icon=":material/account_tree:"),
	st.Page(str(pages_dir / "4_Inconsistency_Check.py"), title="Inconsistency Check", icon=":material/warning:"),
]
navigation = st.navigation(pages, position="hidden")

with st.sidebar:
	st.markdown('<div class="eyebrow">DOCUMENT INTELLIGENCE</div>', unsafe_allow_html=True)
	st.markdown("## ◈ HLD Insight")
	st.caption("A grounded workspace for AUTOSAR architecture analysis.")
	st.markdown('<div class="section-rule"></div>', unsafe_allow_html=True)
	for page in pages:
		st.page_link(page, label=page.title, icon=page.icon)
	st.markdown('<div class="section-rule"></div>', unsafe_allow_html=True)
	st.markdown('<div class="status-label">ACTIVE PROJECT</div>', unsafe_allow_html=True)
	st.markdown(f'<div class="status-value">{st.session_state.get("project_id", "") or "Not selected"}</div>', unsafe_allow_html=True)

navigation.run()
