import article_format as af
import rag_core

def test_load_articles_sets_metadata(tmp_path):
    meta = {"url": "https://x.com/a", "title": "Title A", "site": "s",
            "date": "2026-08-30", "scraped_at": "2026-09-04T00:00:00Z"}
    af.write_article(str(tmp_path), meta, "Body content here.")
    docs = rag_core.load_articles(str(tmp_path))
    assert len(docs) == 1
    d = docs[0]
    assert "Body content here." in d.page_content
    assert d.metadata["source"] == "https://x.com/a"
    assert d.metadata["title"] == "Title A"
    assert d.metadata["site"] == "s"

def test_chunk_documents_splits():
    from langchain_core.documents import Document
    docs = [Document(page_content="word " * 400, metadata={"source": "u"})]
    chunks = rag_core.chunk_documents(docs, chunk_size=200, overlap=20)
    assert len(chunks) > 1
    assert all(c.metadata["source"] == "u" for c in chunks)
