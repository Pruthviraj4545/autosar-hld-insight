import streamlit as st

from api_client import APIError, find_inconsistencies
from styles import active_project, inject_css, page_header


inject_css()
page_header("04 / QUALITY", "Find design drift", "Compare repeated definitions and surface contradictions before they reach implementation.")

project_id = active_project()
if not project_id:
	st.warning("Choose an active project on the Home page first.")
	st.stop()

st.markdown(f'<div class="status-card"><div class="status-label">AUDITING</div><div class="status-value">{project_id}</div></div>', unsafe_allow_html=True)
st.markdown('<div class="section-rule"></div>', unsafe_allow_html=True)
if st.button("⚠️ Run Inconsistency Check", type="primary"):
	with st.spinner("Comparing repeated definitions across the document…"):
		try:
			st.session_state.inconsistencies = find_inconsistencies(project_id)
			st.session_state.inconsistency_error = False
		except APIError as exc:
			st.session_state.inconsistency_error = True
			st.error(str(exc))

issues = st.session_state.get("inconsistencies", [])
if st.session_state.get("inconsistency_error", False):
	st.info("Fix the backend error and run the check again.")
elif not issues:
	st.success("✅ No significant inconsistencies were detected in this document.")
else:
	st.warning(f"{len(issues)} likely inconsistency{'ies' if len(issues) != 1 else 'y'} detected.")
	for issue in issues:
		st.markdown(f'<div class="warning-card"><div class="eyebrow">⚠️ LIKELY MISMATCH</div><h3>{issue.get("entity_name", "Unnamed entity")}</h3><p>{issue.get("explanation", "The model flagged differing descriptions.")}</p></div>', unsafe_allow_html=True)
		with st.expander("View source citations"):
			for source in issue.get("sources", []):
				st.markdown(f'<div class="source-card"><strong>{source.get("heading", "Untitled section")}</strong><br>Chunk {source.get("chunk_id", "?")} · Pages {source.get("page_start", "?")}–{source.get("page_end", "?")}</div>', unsafe_allow_html=True)
