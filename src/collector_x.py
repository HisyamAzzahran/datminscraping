import os
import json
import time
import requests
from datetime import datetime
from tqdm import tqdm
from .config import get_x_bearer_token

OUTPUT_PATH = os.path.join("data", "raw_x.jsonl")

SEARCH_QUERY = (
    "(Unpad OR Maba Unpad OR BEM Unpad OR pad!) lang:id -is:retweet"
)
# quey disesuaikan dengan kebutuhan
# pakai lang:id biar dominan bahasa indonesia

def fetch_tweets_page(bearer_token, query, next_token=None, max_results=100):
    url = "https://api.x.com/2/tweets/search/recent"
    params = {
        "query": query,
        "tweet.fields": "author_id,created_at,lang,public_metrics,text",
        "max_results": max_results,
    }
    if next_token:
        params["next_token"] = next_token

    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "User-Agent": "ScraperForClassProject/1.0"
    }

    r = requests.get(url, headers=headers, params=params, timeout=30)
    if r.status_code != 200:
        raise RuntimeError(f"X API error {r.status_code}: {r.text}")
    return r.json()

def collect_x(target_count=80):
    bearer = get_x_bearer_token()
    all_docs = []
    next_token = None

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        pbar = tqdm(total=target_count, desc="Scraping X")
        while len(all_docs) < target_count:
            data = fetch_tweets_page(bearer, SEARCH_QUERY, next_token=next_token)
            tweets = data.get("data", [])
            meta = data.get("meta", {})
            next_token = meta.get("next_token", None)

            for tw in tweets:
                # filter tweet yg pendek dan bukan bahasa indonesia
                text = tw.get("text","").strip()
                lang = tw.get("lang","")
                if len(text.split()) < 5:
                    continue
                if lang != "in" and lang != "id":  # X kadang pakai "in" buat indo
                    continue

                doc = {
                    "id": f"x_{tw['id']}",
                    "source": "x",
                    "url": f"https://x.com/i/web/status/{tw['id']}",
                    "author": tw.get("author_id",""),
                    "published_at": tw.get("created_at",""),
                    "title": "",
                    "text": text,
                    "lang_guess": lang,
                    "meta": {
                        "retweet_count": tw.get("public_metrics",{}).get("retweet_count"),
                        "reply_count": tw.get("public_metrics",{}).get("reply_count"),
                        "like_count": tw.get("public_metrics",{}).get("like_count"),
                        "quote_count": tw.get("public_metrics",{}).get("quote_count"),
                    }
                }

                f.write(json.dumps(doc, ensure_ascii=False) + "\n")
                all_docs.append(doc)
                pbar.update(1)
                if len(all_docs) >= target_count:
                    break

            if not next_token:
                break  # tidak ada halaman lanjut
            time.sleep(1)  # biar ga spam

    return len(all_docs)

if __name__ == "__main__":
    total = collect_x()
    print("Tweet tersimpan:", total)
