from pydantic import BaseModel


class QueryRequest(BaseModel):
	project_id: str
	question: str
