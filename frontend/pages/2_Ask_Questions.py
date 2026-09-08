import streamlit as st

from api_client import APIError, ask_question
from styles import active_project, inject_css, page_header


inject_css()
page_header("02 / REASONING", "Ask the document", "Get grounded answers from your architecture corpus, with page-level traceability built in.")

project_id = active_project()
if not project_id:
	st.warning("No active project selected. Start on the Home page, then return here to ask questions.")
	st.stop()

if "chat_history" not in st.session_state:
	st.session_state.chat_history = []

st.markdown(f'<div class="status-card"><div class="status-label">ACTIVE DOCUMENT</div><div class="status-value">{project_id}</div></div>', unsafe_allow_html=True)
if not st.session_state.chat_history:
	st.markdown('<div class="card" style="margin-top:1.5rem"><div class="feature-mark">✦</div><h3>Start with a precise question</h3><p>Try: “Which interfaces connect the EngineController to other components?”</p></div>', unsafe_allow_html=True)

for message in st.session_state.chat_history:
	if message["role"] == "user":
		st.markdown(f'<div class="chat-user"><div class="status-label">YOU</div>{message["content"]}</div>', unsafe_allow_html=True)
	else:
		st.markdown('<div class="chat-ai"><div class="status-label">HLD INSIGHT</div>', unsafe_allow_html=True)
		st.markdown(message["content"])
		if message.get("sources"):
			with st.expander("📚 Sources"):
				for source in message["sources"]:
					st.markdown(f'<div class="source-card"><strong>{source.get("heading", "Untitled section")}</strong><br><span>Pages {source.get("page_start", "?")}–{source.get("page_end", "?")}</span></div>', unsafe_allow_html=True)
		st.markdown('</div>', unsafe_allow_html=True)

question = st.chat_input("Ask about components, interfaces, behavior, or constraints…")
if question:
	st.session_state.chat_history.append({"role": "user", "content": question})
	with st.spinner("Retrieving evidence and composing a cited answer…"):
		try:
			result = ask_question(project_id, question)
			st.session_state.chat_history.append({"role": "assistant", "content": result.get("answer", "No answer returned."), "sources": result.get("sources", [])})
		except APIError as exc:
			st.session_state.chat_history.append({"role": "assistant", "content": f"Unable to answer: {exc}", "sources": []})
	st.rerun()
