"""FastAPI wrapper around ingest + ask."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

import ingest as ingest_mod
import answer as answer_mod

load_dotenv()

app = FastAPI()
app.add_middleware(
    CORSMiddleware, allow_origins=["http://localhost:5173"],
    allow_methods=["*"], allow_headers=["*"],
)


class IngestBody(BaseModel):
    folder: str


@app.post("/ingest")
def do_ingest(body: IngestBody):
    return {"chunks": ingest_mod.ingest(body.folder)}


class AskBody(BaseModel):
    question: str


@app.post("/ask")
def do_ask(body: AskBody):
    return answer_mod.ask(body.question)