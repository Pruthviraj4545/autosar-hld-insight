import streamlit as st

from styles import inject_css


inject_css()

if "project_id" not in st.session_state:
    st.session_state.project_id = ""

st.markdown('<div class="hero"><div class="eyebrow">AUTOSAR / ARCHITECTURE WORKSPACE</div><h1>Read the design.<br><span style="color:#72e0db">See the system.</span></h1><p class="hero-copy">AI-Powered Document Intelligence Platform for analysis, question answering, entity extraction, and inconsistency detection across AUTOSAR HLD documents.</p></div>', unsafe_allow_html=True)

st.markdown("### Start with a project")
project_id = st.text_input("Project ID", value=st.session_state.project_id, placeholder="e.g. powertrain-hld-v1", help="This ID keeps each document's vector collection and audit trail isolated.")
if project_id != st.session_state.project_id:
    st.session_state.project_id = project_id.strip()
    st.rerun()

st.markdown('<div class="section-rule"></div>', unsafe_allow_html=True)
st.markdown("### A sharper way to review architecture")
features = [
    ("📄", "Document processing", "Upload a PDF and transform its sections into searchable, cited knowledge."),
    ("💬", "Grounded Q&A", "Ask precise questions and trace every answer back to document pages."),
    ("🔍", "Entity extraction", "Surface components, interfaces, and descriptions from the design."),
    ("⚠️", "Inconsistency detection", "Spot conflicting definitions before they become implementation issues."),
]
columns = st.columns(4)
for column, (icon, title, description) in zip(columns, features):
    with column:
        st.markdown(f'<div class="card"><div class="feature-mark">{icon}</div><h3>{title}</h3><p>{description}</p></div>', unsafe_allow_html=True)

st.markdown('<footer>HLD INSIGHT / GROUNDED ANALYSIS FOR COMPLEX AUTOMOTIVE SYSTEMS</footer>', unsafe_allow_html=True)
