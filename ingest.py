# ingest.py
from dotenv import load_dotenv
import rag_core
import article_store

ARTICLES_DIR = "data/articles"
PERSIST_DIR = "chroma_db"


def prepare_articles(articles_dir=ARTICLES_DIR):
    """Populate the local articles dir from Supabase Storage (the source of
    truth) when creds are present; otherwise leave whatever is on disk (offline
    dev). Returns the downloaded count, or None when skipped."""
    if article_store._creds_present():
        n = article_store.download_all(articles_dir)
        print(f"Downloaded {n} article(s) from Storage into {articles_dir}/.")
        return n
    print("[warn] SUPABASE creds absent — using on-disk articles (offline dev).")
    return None


def main() -> None:
    load_dotenv()
    rag_core.require_env("VOYAGE_API_KEY")
    prepare_articles(ARTICLES_DIR)
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
