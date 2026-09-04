# ingest.py
from dotenv import load_dotenv
import rag_core

ARTICLES_DIR = "data/articles"
PERSIST_DIR = "chroma_db"


def main() -> None:
    load_dotenv()
    rag_core.require_env("VOYAGE_API_KEY")
    docs = rag_core.load_articles(ARTICLES_DIR)
    if not docs:
        raise SystemExit(f"No articles in {ARTICLES_DIR}/. Run the scraper first.")
    chunks = rag_core.chunk_documents(docs)
    print(f"Rebuilding index in {PERSIST_DIR}/ ...")
    rag_core.reset_index_dir(PERSIST_DIR)
    rag_core.build_index(chunks, PERSIST_DIR)
    print(f"Indexed {len(chunks)} chunks from {len(docs)} articles into {PERSIST_DIR}/.")


if __name__ == "__main__":
    main()
