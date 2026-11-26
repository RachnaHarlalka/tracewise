from repolens.config import TopK
from repolens.db import connect, get_branch, load_files, search_chunks
from repolens.embeddings import embed_data

from fastapi import FastAPI


app = FastAPI()


@app.get("/")
async def root():
  return {"message":"Hello world"}

@app.get("/health")
def health():
  return {"status":"ok"}

@app.post("/chat")
def chat(req, res):
  if branch is None:
    return "No branch exist for this name"
  with connect() as conn:
    branch = get_branch(conn,req.branch_id)
    embedded_question = embed_data(req.question)
    results = search_chunks(conn,req.branch_id,embedded_question,TopK)
    files = load_files(conn, req.branch_id)







