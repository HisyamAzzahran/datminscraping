import os
from src.collector_x import collect_x
from src.collector_news import collect_news
from src.merge import merge_raw
from src.preprocess_id import preprocess
from src.qc_report import qc_sample

def ensure_dirs():
    os.makedirs("data", exist_ok=True)

def main():
    ensure_dirs()
    print("Step 1. Scrap X ...")
    total_x = collect_x(target_count=80)
    print("Tweet didapat:", total_x)

    print("Step 2. Scrap News ...")
    total_news = collect_news(target_count=600)
    print("Artikel berita didapat:", total_news)

    print("Step 3. Merge ...")
    merge_raw()

    print("Step 4. Preprocess ...")
    preprocess()

    print("Step 5. QC sample ...")
    qc_sample(n=5)

if __name__ == "__main__":
    main()
