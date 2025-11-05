import os
import json

RAW_X = os.path.join("data", "raw_x.jsonl")
RAW_NEWS = os.path.join("data", "raw_news.jsonl")
OUT_ALL = os.path.join("data", "raw_all.jsonl")

def merge_raw():
    docs = []

    def load_file(path):
        if not os.path.exists(path):
            return
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line=line.strip()
                if not line:
                    continue
                docs.append(json.loads(line))

    load_file(RAW_X)
    load_file(RAW_NEWS)

    with open(OUT_ALL, "w", encoding="utf-8") as g:
        for d in docs:
            g.write(json.dumps(d, ensure_ascii=False) + "\n")

    print("Total gabungan:", len(docs))

if __name__ == "__main__":
    merge_raw()
