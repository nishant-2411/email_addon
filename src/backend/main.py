from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from .schema import EmailRecord
from .ingest_imap import fetch_emails_imap
import logging

logging.basicConfig(level=logging.INFO)
app = FastAPI(title="ShipCube Backend Prototype")

@app.get("/health")
def health():
    return {"status": "ok"}

class IngestRequest(BaseModel):
    provider: str  # 'imap' or 'graph'
    config: dict

@app.post("/ingest_imap")
def ingest_imap(req: IngestRequest, background_tasks: BackgroundTasks):
    """Start IMAP ingestion in background (simple demo)."""
    if req.provider != "imap":
        return {"error": "This endpoint is for IMAP provider only. Use /ingest_graph for Graph API."}
    background_tasks.add_task(fetch_emails_imap, req.config)
    return {"status": "ingestion_started"}
