# Scraping Mentah: Unpad News & X Data Pipeline

Proyek ini adalah pipeline scraping, penggabungan, dan pembersihan data berita serta tweet terkait Universitas Padjadjaran (Unpad) dari berbagai sumber berita online dan platform X (Twitter). Hasil akhirnya berupa dataset bersih yang siap digunakan untuk analisis data mining lebih lanjut.

## Hasil Pengumpulan Data

### Data Mentah (Raw Data)
1. **Data Twitter/X** (`data/raw_x.jsonl`)
   - Total data: 81 tweets
   - Format: JSONL dengan fields: id, source, url, author, published_at, text, lang_guess, meta (retweet_count, reply_count, like_count, quote_count)
   - Periode: November 2025

2. **Data Berita** (`data/raw_news.jsonl`)
   - Total data: 501 artikel berita
   - Sumber: Google News dengan filter site:unpad.ac.id
   - Format: JSONL dengan fields: id, source, url, author, published_at, title, text, lang_guess, meta

3. **Data Gabungan** (`data/raw_all.jsonl`)
   - Kombinasi data dari Twitter/X dan berita
   - Total: 582 entries

### Data Bersih (Processed Data)
1. **Data Terproses** (`data/clean.jsonl`)
   - Total entries: 549 records
   - Tambahan field: text_clean (hasil preprocessing)
   - Tag khusus: tag_unpad (boolean)
   - Bahasa: Mayoritas Indonesia (berdasarkan lang_guess)

2. **Dataset Final** (`data/clean.csv`)
   - Format: CSV untuk kemudahan analisis
   - Berisi data yang sudah dibersihkan dan distandarisasi

## Fitur Utama & Pipeline
- **Scraping X (Twitter):** Mengambil tweet terkait Unpad menggunakan API X.
- **Scraping Berita:** Mengambil artikel berita dari berbagai portal berita nasional dengan kata kunci terkait Unpad dan pendidikan.
- **Merge Data:** Menggabungkan hasil scraping tweet dan berita ke satu file.
- **Preprocessing:** Membersihkan, normalisasi, dan filtering data (stopword removal, stemming, dsb).
- **QC Report:** Menampilkan sampel data bersih untuk pengecekan kualitas.

## Statistik Data
- Total data mentah: 582 entries
- Total data bersih: 549 entries
- Rasio data Twitter:Berita ≈ 1:6
- Periode data: Juli - November 2025

## Preprocessing yang Dilakukan
- Pembersihan teks (text cleaning)
- Deteksi bahasa (menggunakan langdetect)
- Penandaan konten terkait UNPAD
- Standarisasi format tanggal dan waktu
- Penghapusan duplikasi

## Struktur Folder
```
├── data/
│   ├── raw_x.jsonl      # Hasil scraping X
│   ├── raw_news.jsonl   # Hasil scraping berita
│   ├── raw_all.jsonl    # Gabungan raw_x + raw_news
│   ├── clean.jsonl      # Data bersih (JSONL)
│   └── clean.csv        # Data bersih (CSV)
├── src/
│   ├── collector_x.py   # Scraper X
│   ├── collector_news.py# Scraper berita
│   ├── merge.py         # Penggabungan data
│   ├── preprocess_id.py # Preprocessing & cleaning
│   ├── qc_report.py     # QC sample data
│   └── config.py        # Konfigurasi token, dsb
├── requirements.txt     # Dependensi Python
├── run_all.py           # Pipeline otomatis
└── .env                 # Token API X 
```

## Cara Menjalankan
1. **Install dependensi:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Siapkan file `.env`** berisi token X:
   ```env
   X_BEARER_TOKEN=isi_token_x_anda
   ```
3. **Jalankan pipeline:**
   ```bash
   python run_all.py
   ```
   Atau jalankan per modul sesuai kebutuhan.

## Hasil Akhir
- `data/clean.jsonl` : Dataset bersih dalam format JSONL
- `data/clean.csv`   : Dataset bersih dalam format CSV
- Contoh output QC:
  - source: x/news
  - text_clean: "...teks hasil pembersihan..."

## Catatan
- Token API X tidak dibagikan, silakan buat sendiri di https://developer.x.com/
- Kata kunci scraping dapat disesuaikan di `src/collector_x.py` dan `src/collector_news.py`.

---

