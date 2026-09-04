from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from langchain_anthropic import ChatAnthropic

import rag_core

load_dotenv()
PERSIST_DIR = "chroma_db"
MODEL = "claude-haiku-4-5"
PROMPT_TMPL = (
    "Answer the question using ONLY the context below. "
    "If the answer is not in the context, say you don't know.\n\n"
    "Context:\n{context}\n\nQuestion: {question}"
)

app = FastAPI(title="blog-rag")


class Ask(BaseModel):
    question: str


def _llm():
    return ChatAnthropic(model=MODEL, max_tokens=1024)


def answer_question(question: str) -> dict:
    store = rag_core.load_index(PERSIST_DIR)
    retriever = rag_core.get_retriever(store, k=4)
    docs = retriever.invoke(question)
    context = rag_core.format_docs(docs)
    answer = _llm().invoke(PROMPT_TMPL.format(context=context, question=question)).content
    sources, seen = [], set()
    for d in docs:
        url = d.metadata.get("source", "")
        if url and url not in seen:
            seen.add(url)
            sources.append({"title": d.metadata.get("title", ""), "url": url,
                            "site": d.metadata.get("site", "")})
    return {"answer": answer, "sources": sources}


@app.post("/ask")
def ask(payload: Ask):
    q = payload.question.strip()
    if not q:
        raise HTTPException(status_code=400, detail="Question is empty.")
    return answer_question(q)


@app.get("/")
def index():
    return FileResponse("static/index.html")
