# Scraping Mentah: Unpad News & X Data Pipeline

Proyek ini adalah pipeline scraping, penggabungan, dan pembersihan data berita serta tweet terkait Universitas Padjadjaran (Unpad) dari berbagai sumber berita online dan platform X (Twitter). Hasil akhirnya berupa dataset bersih yang siap digunakan untuk analisis data mining lebih lanjut.

## Fitur Utama
- **Scraping X (Twitter):** Mengambil tweet terkait Unpad menggunakan API X.
- **Scraping Berita:** Mengambil artikel berita dari berbagai portal berita nasional dengan kata kunci terkait Unpad dan pendidikan.
- **Merge Data:** Menggabungkan hasil scraping tweet dan berita ke satu file.
- **Preprocessing:** Membersihkan, normalisasi, dan filtering data (stopword removal, stemming, dsb).
- **QC Report:** Menampilkan sampel data bersih untuk pengecekan kualitas.

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
- Contoh output QC (5 data acak):
  - source: x/news
  - text_clean: "...teks hasil pembersihan..."

## Catatan
- Proyek ini untuk keperluan riset/akademik.
- Token API X tidak dibagikan, silakan buat sendiri di https://developer.x.com/
- Kata kunci scraping dapat disesuaikan di `src/collector_x.py` dan `src/collector_news.py`.

---

