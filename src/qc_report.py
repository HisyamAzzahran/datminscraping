import os, json, random
INPUT_CLEAN = os.path.join("data","clean.jsonl")

def qc_sample(n=5):
    docs = []
    with open(INPUT_CLEAN,"r",encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            docs.append(json.loads(line))
    print("Total dokumen bersih:", len(docs))
    print("Contoh acak:")
    for d in random.sample(docs, min(n,len(docs))):
        print("source:", d["source"])
        print("text_clean:", d["text_clean"][:200], "...")
        print("---")

if __name__ == "__main__":
    qc_sample()
