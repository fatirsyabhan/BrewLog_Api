# BrewLog API

Tugas UTS Pemrograman Web Lanjutan
**Oleh:** Fathir Syabhan (H071241091)

BrewLog API adalah RESTful API sederhana yang dibangun menggunakan FastAPI dan SQLite. API ini digunakan untuk mencatat data biji kopi (Coffee Beans) dan resep seduhannya (Brew Recipes) dengan relasi One-to-Many, serta dilengkapi dengan sistem autentikasi JWT.

## Fitur Utama
- **Autentikasi**: Register dan Login user menggunakan JWT.
- **Coffee Beans**: CRUD data biji kopi.
- **Brew Recipes**: CRUD data resep seduh kopi (berelasi dengan tabel coffee beans).
- **Protected Endpoints**: Endpoint untuk modifikasi data (Create, Update, Delete) diamankan dengan token akses.

## Cara Menjalankan Project

1. Pastikan Python sudah terinstall.
2. Buka terminal dan masuk ke dalam folder project ini.
3. Install library yang dibutuhkan:
   ```bash
   pip install -r requirements.txt
   ```
4. Jalankan server FastAPI:
   ```bash
   python -m uvicorn main:app --reload
   ```
5. Buka Swagger UI di browser untuk mencoba API:
   [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## Tech Stack
- Python 3.9+
- FastAPI
- SQLAlchemy (ORM)
- Pydantic (Validasi Skema)
- SQLite (Database)
- Passlib & Jose (Keamanan JWT)
