"""Upload local article .md files to Supabase Storage (run after scrape, in the
project venv). Best-effort per file. Because data/articles is gitignored, a CI
checkout only holds THIS run's new articles — so this naturally uploads just the
new ones while ingest.py downloads the full set."""
import glob
import os
from dotenv import load_dotenv

import article_store

ARTICLES_DIR = "data/articles"


def upload_dir(articles_dir=ARTICLES_DIR):
    article_store.ensure_bucket()
    uploaded = failed = 0
    for path in sorted(glob.glob(os.path.join(articles_dir, "*.md"))):
        try:
            article_store.upload_article(path)
            uploaded += 1
        except Exception as e:  # noqa: BLE001 - one bad file must not abort the run
            print(f"  [warn] upload failed for {path}: {e}")
            failed += 1
    print(f"Uploaded {uploaded} article(s) to Storage; {failed} failed.")
    return {"uploaded": uploaded, "failed": failed}


def main():
    load_dotenv()
    upload_dir()


if __name__ == "__main__":
    main()
