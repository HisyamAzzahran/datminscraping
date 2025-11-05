import os
import re
import json
import hashlib
import pandas as pd
from collections import Counter
from langdetect import detect, DetectorFactory
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

DetectorFactory.seed = 0
factory = StemmerFactory()
stemmer = factory.create_stemmer()

INPUT_PATH = os.path.join("data", "raw_all.jsonl")
OUT_JSONL = os.path.join("data", "clean.jsonl")
OUT_CSV = os.path.join("data", "clean.csv")

ID_STOPWORDS = set("""
yang dan di ke dari untuk pada dengan sebagai kepada dalam adalah itu ini atau juga akan sudah karena oleh tidak
saya kamu kita mereka dia ia ada telah bisa dapat hingga agar supaya para tiap setiap pun saja bahwa
""".split())

SLANG_MAP = {
    "gak":"tidak","ga":"tidak","ngga":"tidak","nggak":"tidak",
    "aja":"saja","bgt":"banget","bener":"benar","kalo":"kalau",
    "udh":"sudah","sdh":"sudah","blm":"belum","yg":"yang","dlm":"dalam",
}

URL_RE = re.compile(r"https?://\S+")
MENTION_RE = re.compile(r"[@#]\w+")
ELONG_RE = re.compile(r"(.)\1{2,}")       # huruf panjang: "parahhh" -> "parahh"
PUNC_RE = re.compile(r"[^0-9a-zA-Záéíóúàèìòùüäëïöñ’'’\-\s]")


UNPAD_PATTERNS = [
    r"\bunpad\b",
    r"\buniversitas\s+padjadjaran\b",
    r"\bjatinangor\b"
]

def has_unpad(text):
    if not text:
        return False
    t = text.lower()
    import re
    return any(re.search(pat, t) for pat in UNPAD_PATTERNS)

def normalize(text):
    t = text.lower()
    t = URL_RE.sub(" ", t)
    t = MENTION_RE.sub(" ", t)
    t = ELONG_RE.sub(r"\1\1", t)
    t = PUNC_RE.sub(" ", t)
    t = re.sub(r"\s+", " ", t).strip()
    tokens = t.split()
    tokens = [SLANG_MAP.get(tok, tok) for tok in tokens]
    return " ".join(tokens)

def remove_stopwords(tokens):
    return [t for t in tokens if t not in ID_STOPWORDS and len(t) > 2]

def pipeline(doc):
    txt = doc.get("text","")
    if not txt.strip():
        return None

    # deteksi bahasa
    try:
        lang = detect(txt)
    except:
        lang = ""

    # hanya simpan bahasa indonesia
    # langdetect kadang return "id", X kadang pakai "in"
    if lang not in ["id","in",""]:  
        return None

    norm = normalize(txt)
    tokens = norm.split()
    tokens = remove_stopwords(tokens)
    stemmed = [stemmer.stem(t) for t in tokens]
    clean = " ".join(stemmed)

    if len(clean.split()) < 5:
        return None

    doc_out = {
        "id": doc.get("id",""),
        "source": doc.get("source",""),
        "url": doc.get("url",""),
        "author": doc.get("author",""),
        "published_at": doc.get("published_at",""),
        "title": doc.get("title",""),
        "text": txt,
        "text_clean": clean,
        "lang_guess": lang if lang else doc.get("lang_guess",""),
        "meta": doc.get("meta",{})
    }

    # tambahkan fingerprint buat deduplikasi
    fp = hashlib.md5(doc_out["text_clean"].encode("utf-8")).hexdigest()
    doc_out["_fp"] = fp
    return doc_out

def preprocess():
    rows = []
    seen_fp = set()

    with open(INPUT_PATH, "r", encoding="utf-8") as f, \
         open(OUT_JSONL, "w", encoding="utf-8") as g:

        for line in f:
            if not line.strip():
                continue
            raw_doc = json.loads(line)
            doc2 = pipeline(raw_doc)
            if not doc2:
                continue
            if doc2["_fp"] in seen_fp:
                continue
            seen_fp.add(doc2["_fp"])
            
            tag_unpad = any([
                has_unpad(doc2.get("title","")),
                has_unpad(doc2.get("text","")),
                has_unpad(doc2.get("url","")),
            ])

            # tulis ke clean.jsonl tanpa _fp
            to_write = {k:v for k,v in doc2.items() if k != "_fp"}
            to_write["tag_unpad"] = tag_unpad
            g.write(json.dumps(to_write, ensure_ascii=False) + "\n")

            rows.append(to_write)

    if rows:
        cols = ["id","source","url","author","published_at","title","text","text_clean","lang_guess","tag_unpad","meta"]
        pd.DataFrame([{k:r.get(k,"") for k in cols} for r in rows]).to_csv(OUT_CSV, index=False, encoding="utf-8")

    # QC cepat
    lengths = [len(r["text_clean"].split()) for r in rows]
    vocab_counter = Counter(" ".join(r["text_clean"] for r in rows).split())
    total = len(rows)
    prop_unpad = sum(1 for r in rows if r.get("tag_unpad")) / total if total else 0
    print("Jumlah dokumen bersih:", len(rows))
    if lengths:
        print("Rata-rata panjang dokumen (token):", sum(lengths)/len(lengths))
    print("Top 30 token paling sering:", vocab_counter.most_common(30))
    print("Proporsi dokumen terkait Unpad:", round(prop_unpad*100, 2), "%")

if __name__ == "__main__":
    preprocess()
