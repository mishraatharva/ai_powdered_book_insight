import os
import django
import sys


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(BASE_DIR, "book_ai"))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'book_ai.settings')
django.setup()

import glob
import pandas as pd
from book_ai.books.models import Book

# Your CSV folder
data_dir = r"U:\assignment\ai_powdered_book_insight\scraper\data\with_description"

csv_files = glob.glob(os.path.join(data_dir, "*.csv"))

# 🧹 Clean function
def clean(val):
    if pd.isna(val):
        return None
    if isinstance(val, str) and val.strip() == "":
        return None
    return val

total_inserted = 0

for file in csv_files:
    print(f"\n📄 Processing: {file}")

    df = pd.read_csv(file)

    books = []

    for _, row in df.iterrows():
        title = clean(row.get("title"))

        # ❗ Skip useless rows
        if not title:
            continue

        books.append(Book(
            asin = clean(row.get("asin")),
            title=title,
            author=clean(row.get("author")),
            rating=clean(row.get("rating")),
            reviews=clean(row.get("reviews")),
            description=clean(row.get("description")),
            url=clean(row.get("url"))
        ))

    # 🚀 Bulk insert (FAST)
    Book.objects.bulk_create(books, ignore_conflicts=True)

    total_inserted += len(books)
    print(f"✅ Inserted {len(books)} rows")

print(f"\n🎉 TOTAL INSERTED: {total_inserted}")