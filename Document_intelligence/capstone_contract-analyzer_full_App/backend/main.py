"""FastAPI backend for the Contract Analyzer."""
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

import store, extract, analyze

load_dotenv()
store.init_db()

app = FastAPI()
app.add_middleware(
    CORSMiddleware, allow_origins=["http://localhost:5173"],
    allow_methods=["*"], allow_headers=["*"],
)


@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    pdf_bytes = await file.read()
    parsed = extract.extract_pages(pdf_bytes)
    doc_id = store.save_doc(file.filename, parsed["pages"], parsed["audit"])
    insights = analyze.summarize_and_extract(parsed["pages"])
    return {"doc_id": doc_id, "insights": insights, "audit": parsed["audit"]}


@app.get("/docs/{doc_id}")
def read_doc(doc_id: str):
    doc = store.get_doc(doc_id)
    if not doc:
        raise HTTPException(404, "not found")
    return doc


class Ask(BaseModel):
    doc_id: str
    question: str


@app.post("/ask")
def ask(body: Ask):
    doc = store.get_doc(body.doc_id)
    if not doc:
        raise HTTPException(404, "not found")
    return analyze.answer_question(doc["pages"], body.question) 