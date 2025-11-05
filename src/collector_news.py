
import os, json, time, uuid, requests
from bs4 import BeautifulSoup
from urllib.parse import urlencode, quote_plus
from tqdm import tqdm
import feedparser
from concurrent.futures import ThreadPoolExecutor, as_completed
from requests.adapters import HTTPAdapter, Retry

OUTPUT_PATH = os.path.join("data", "raw_news.jsonl")
UNPAD_ONLY = os.getenv("UNPAD_ONLY", "0") == "1"

HEADERS = {"User-Agent": "ScraperForClassProject/1.0"}

# Kata kunci
UNPAD_KEYWORDS = [
    "unpad", "universitas padjadjaran", "jatinangor",
    "mahasiswa unpad", "rektor unpad", "fakultas unpad", "beasiswa unpad",
]
GENERAL_KEYWORDS = [
    "pendidikan", "mahasiswa", "kampus", "beasiswa",
    "teknologi", "AI", "ekonomi", "kebijakan", "riset", "startup"
]

KEYWORDS = UNPAD_KEYWORDS if UNPAD_ONLY else (UNPAD_KEYWORDS + GENERAL_KEYWORDS)

# Domain yang sering memuat berita Unpad
DOMAINS = [
    "unpad.ac.id",
    "pikiran-rakyat.com",
    "kompas.com",
    "detik.com",
    "tempo.co",
    "cnnindonesia.com",
    "ayobandung.com",
    "tribunnews.com",
    "antara.com"
]

def build_feed_urls():
    urls = []
    for kw in KEYWORDS:
        for dom in DOMAINS:
            q_val = f'{kw} site:{dom}'
            qs = urlencode({"q": q_val, "hl": "id", "gl": "ID", "ceid": "ID:id"}, quote_via=quote_plus)
            urls.append(f"https://news.google.com/rss/search?{qs}")
    # Satu feed agregat tanpa site: untuk jangkauan luas
    agg_q = '("unpad" OR "universitas padjadjaran" OR jatinangor)'
    qs = urlencode({"q": agg_q, "hl": "id", "gl": "ID", "ceid": "ID:id"}, quote_via=quote_plus)
    urls.append(f"https://news.google.com/rss/search?{qs}")
    return urls

from newspaper import Article



def collect_news(target_count=500):
def collect_news(target_count=80):
    items_saved = 0
    seen_urls = set()
    feed_urls = build_feed_urls()
    all_entries = []

    session = requests.Session()
    retries = Retry(total=3, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504])
    session.mount('http://', HTTPAdapter(max_retries=retries))
    session.mount('https://', HTTPAdapter(max_retries=retries))

    for feed_url in tqdm(feed_urls, desc="Mengambil feeds"):
        try:
            # Dapatkan dan parse feed
            resp = session.get(feed_url, headers=HEADERS, timeout=20)
            resp.raise_for_status()
            d = feedparser.parse(resp.content)
            
            # Untuk setiap entry dalam feed
            for e in d.entries:
                google_url = e.get("link", "").strip()
                if not google_url or google_url in seen_urls:
                    continue
                
                # Coba dapatkan URL asli dari Google News redirect
                try:
                    r = session.head(google_url, headers=HEADERS, allow_redirects=True, timeout=10)
                    real_url = r.url
                    if real_url and real_url not in seen_urls:
                        seen_urls.add(real_url)
                        all_entries.append((e, feed_url, real_url))
                except Exception as ex:
                    print(f"Gagal resolve URL: {google_url} ({ex})")
                    continue
                
            print(f"Feed {feed_url}: {len(d.entries)} entries")
            if len(all_entries) >= target_count * 3:
                break
                
        except Exception as ex:
            print(f"Feed gagal: {feed_url} ({ex})")
            continue

    print(f"\nTotal URLs unik: {len(all_entries)}")

    results = []
    def process_entry(args):
        e, feed_url, url = args

        # Skip URLs non-berita
        skip_patterns = ["login", "admin", "account", "pendaftaran", "register"]
        if any(p in url.lower() for p in skip_patterns):
            print(f"Skip URL non-berita: {url}")
            return None

        # Skip judul yang tidak diinginkan
        title = (e.get("title") or "").strip()
        skip_title_patterns = [
                "jurnal", "repository", "vol.", "volume", 
                "skripsi", "tesis", "disertasi",
                "portal unpad", "perpustakaan unpad"
        ]
        if any(p in title.lower() for p in skip_title_patterns):
            print(f"Skip judul tidak relevan: {title}")
            return None

        # Pastikan judul cukup panjang (minimal 8 kata)
            if len(title.split()) < 6:
            print(f"Skip judul terlalu pendek: {title}")
            return None
            
        # Coba ambil konten dengan newspaper3k
        try:
            article = Article(url)
                article.config.request_timeout = 15
            article.download()
            article.parse()
            
            text = article.text.strip()

        except Exception as ex:
            print(f"Gagal parse artikel: {url} ({ex})")
            return None

        # Jika text kosong, gunakan title sebagai text
        if not text:
            text = title

        doc = {
            "id": str(uuid.uuid4()),
            "source": "news",
            "url": url,
            "author": e.get("author",""),
            "published_at": e.get("published",""),
            "title": (e.get("title") or "").strip(),
            "text": text.strip(),
            "lang_guess": "id",
            "meta": {
                "feed": feed_url,
                "original_url": e.get("link","")
            }
        }
        return doc

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(process_entry, entry) for entry in all_entries]
        with open(OUTPUT_PATH, "w", encoding="utf-8") as f, tqdm(total=target_count, desc="Scraping News (fast)") as pbar:
            for future in as_completed(futures):
                doc = future.result()
                if doc:
                    f.write(json.dumps(doc, ensure_ascii=False) + "\n")
                    items_saved += 1
                    pbar.update(1)
                if items_saved >= target_count:
                    break

    return items_saved

if __name__ == "__main__":
    print("News tersimpan:", collect_news())
