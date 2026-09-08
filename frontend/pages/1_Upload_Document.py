import streamlit as st

from api_client import APIError, ingest_document
from styles import active_project, inject_css, page_header


inject_css()
page_header("01 / INGESTION", "Upload a design document", "Turn a PDF architecture document into a searchable, cited workspace.")

project_id = active_project()
if not project_id:
	st.warning("Set an active Project ID on the Home page before ingesting a document.")
else:
	st.markdown(f'<div class="status-card"><div class="status-label">INGESTING INTO</div><div class="status-value">{project_id}</div></div>', unsafe_allow_html=True)

st.markdown('<div class="section-rule"></div>', unsafe_allow_html=True)
left, right = st.columns([1.5, 1], gap="large")
with left:
	st.markdown('<div class="card"><div class="eyebrow">SOURCE DOCUMENT</div><h3>Drop your PDF here</h3><p>HLD Insight will detect sections, create overlapping chunks, embed the content, and store it for retrieval.</p>', unsafe_allow_html=True)
	uploaded = st.file_uploader("PDF document", type=["pdf"], label_visibility="collapsed")
	if uploaded and st.button("Upload & Process Document", type="primary", use_container_width=True, disabled=not bool(project_id)):
		with st.spinner("Parsing, embedding, and indexing your document…"):
			try:
				result = ingest_document(project_id, uploaded)
				st.success("Document ingested and ready for analysis.")
				metric_a, metric_b = st.columns(2)
				metric_a.metric("Status", result.get("status", "ready").upper())
				metric_b.metric("Indexed chunks", result.get("num_chunks", 0))
			except APIError as exc:
				st.error(str(exc))
	st.markdown('</div>', unsafe_allow_html=True)
with right:
	st.markdown('<div class="card"><div class="eyebrow">PIPELINE</div><h3>What happens next</h3><p>01 · Extract sections</p><p>02 · Build semantic chunks</p><p>03 · Generate embeddings</p><p>04 · Isolate by project</p><p>05 · Enable cited answers</p></div>', unsafe_allow_html=True)

st.info("Supported format: PDF. For best results, use a text-based HLD export with clear section headings.")
