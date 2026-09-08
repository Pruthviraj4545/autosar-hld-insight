import requests


BASE_URL = "http://localhost:8000"
TIMEOUT = 120


class APIError(RuntimeError):
	pass


def _request(method: str, path: str, **kwargs):
	try:
		response = requests.request(method, f"{BASE_URL}{path}", timeout=TIMEOUT, **kwargs)
	except requests.RequestException as exc:
		raise APIError("Backend is unavailable. Start FastAPI at http://localhost:8000.") from exc
	if not response.ok:
		try:
			detail = response.json().get("detail", response.text)
		except ValueError:
			detail = response.text
		raise APIError(f"Backend returned HTTP {response.status_code}: {detail}")
	return response


def ingest_document(project_id: str, uploaded_file) -> dict:
	response = _request(
		"POST",
		"/ingest",
		files={"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")},
		data={"project_id": project_id},
	)
	return response.json()


def ask_question(project_id: str, question: str) -> dict:
	return _request("POST", "/query", json={"project_id": project_id, "question": question}).json()


def extract_entities(project_id: str) -> dict:
	return _request("GET", f"/extract-entities/{project_id}").json()


def find_inconsistencies(project_id: str) -> list[dict]:
	return _request("GET", f"/inconsistencies/{project_id}").json()