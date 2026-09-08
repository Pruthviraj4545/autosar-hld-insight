from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.ingest import router as ingest_router
from app.api.routes.query import router as query_router
from app.api.routes.extraction import router as extraction_router


app = FastAPI(title="AUTOSAR HLD Document Analysis Assistant")
app.add_middleware(
	CORSMiddleware,
	allow_origins=[
		"http://localhost",
		"http://localhost:3000",
		"http://localhost:8501",
	],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)
app.include_router(ingest_router)
app.include_router(query_router)
app.include_router(extraction_router)
