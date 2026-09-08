import streamlit as st

from api_client import APIError, extract_entities
from styles import active_project, inject_css, page_header


inject_css()
page_header("03 / STRUCTURE", "Map the architecture", "Extract the named components and interfaces that shape the system design.")

project_id = active_project()
if not project_id:
	st.warning("Choose an active project on the Home page first.")
	st.stop()

st.markdown(f'<div class="status-card"><div class="status-label">ACTIVE PROJECT</div><div class="status-value">{project_id}</div></div>', unsafe_allow_html=True)
st.markdown('<div class="section-rule"></div>', unsafe_allow_html=True)
if st.button("🔍 Extract Entities", type="primary"):
	with st.spinner("Reading the architecture and resolving entities…"):
		try:
			st.session_state.extracted_entities = extract_entities(project_id).get("entities", [])
			st.session_state.entity_error = False
		except APIError as exc:
			st.session_state.entity_error = True
			st.error(str(exc))

entities = st.session_state.get("extracted_entities", [])
if not st.session_state.get("entity_error", False):
	st.metric("Entities found", len(entities))
if st.session_state.get("entity_error", False):
	st.info("Fix the backend error and run extraction again.")
elif not entities:
	st.info("No entities loaded yet. Run extraction to build an architecture map.")
else:
	query = st.text_input("Filter entities", placeholder="Search by component, interface, or description…")
	filtered = [entity for entity in entities if not query or query.casefold() in str(entity).casefold()]
	st.dataframe(
		[
			{
				"Component Name": entity.get("component_name", ""),
				"Interfaces": ", ".join(entity.get("interfaces", [])),
				"Description": entity.get("description", ""),
			}
			for entity in filtered
		],
		use_container_width=True,
		hide_index=True,
	)
