"""One-time: upload every existing data/articles/*.md to Supabase Storage.
Run once, before removing articles from git (see the plan's Cutover section).
`upload_dir` calls ensure_bucket first, so this also creates the bucket."""
import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import upload_articles


def main():
    load_dotenv()
    result = upload_articles.upload_dir("data/articles")
    print(f"Backfill complete: {result}")


if __name__ == "__main__":
    main()
