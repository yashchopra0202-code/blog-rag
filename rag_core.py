import os
import shutil

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_voyageai import VoyageAIEmbeddings
from langchain_chroma import Chroma

import article_format as af

EMBED_MODEL = "voyage-3.5"


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise SystemExit(f"Missing {name}. Copy .env.example to .env and set it.")
    return value


def get_embeddings() -> VoyageAIEmbeddings:
    return VoyageAIEmbeddings(model=EMBED_MODEL)


def load_articles(articles_dir: str) -> list[Document]:
    docs = []
    if not os.path.isdir(articles_dir):
        return docs
    for name in sorted(os.listdir(articles_dir)):
        if not name.endswith(".md"):
            continue
        meta, body = af.parse_article(os.path.join(articles_dir, name))
        if not body.strip():
            continue
        docs.append(Document(page_content=body, metadata={
            "source": meta.get("url", ""), "title": meta.get("title", ""),
            "site": meta.get("site", ""), "date": meta.get("date", "")}))
    return docs


def chunk_documents(docs, chunk_size: int = 500, overlap: int = 50):
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=overlap)
    return splitter.split_documents(docs)


def reset_index_dir(persist_dir: str) -> None:
    if os.path.isdir(persist_dir):
        shutil.rmtree(persist_dir)


def build_index(chunks, persist_dir: str) -> Chroma:
    return Chroma.from_documents(documents=chunks, embedding=get_embeddings(),
                                 persist_directory=persist_dir)


def load_index(persist_dir: str) -> Chroma:
    return Chroma(persist_directory=persist_dir, embedding_function=get_embeddings())


def get_retriever(store: Chroma, k: int = 4):
    return store.as_retriever(search_kwargs={"k": k})


def format_docs(docs) -> str:
    return "\n\n".join(d.page_content for d in docs)
