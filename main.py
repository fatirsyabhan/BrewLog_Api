"""
main.py - Entry point aplikasi BrewLog API.

File ini adalah titik masuk utama aplikasi FastAPI.
Bertanggung jawab untuk:
1. Membuat instance aplikasi FastAPI dengan metadata (title, desc, version).
2. Membuat tabel database secara otomatis saat aplikasi pertama kali dijalankan.
3. Mendaftarkan semua router (auth, coffee_beans, brew_recipes).
4. Menyediakan endpoint root (/) sebagai health check.

Cara menjalankan:
    uvicorn main:app --reload

Dokumentasi Swagger UI tersedia di:
    http://127.0.0.1:8000/docs

Dokumentasi ReDoc tersedia di:
    http://127.0.0.1:8000/redoc
"""

from fastapi import FastAPI
from database import engine, Base

# Import semua model agar SQLAlchemy tahu tabel mana yang harus dibuat
# Penting: import ini harus ada sebelum Base.metadata.create_all()
from models import CoffeeBean, BrewRecipe, User  # noqa: F401

# Import semua router
from routers import auth, coffee_beans, brew_recipes

# ─────────────────────────────────────────────
# Inisialisasi Aplikasi FastAPI
# ─────────────────────────────────────────────
app = FastAPI(
    title="☕ BrewLog API",
    description="""
## Sistem Manajemen Resep & Teknik Seduh Kopi

BrewLog API memungkinkan Anda untuk:
- 🫘 **Mengelola CoffeeBean** — Tambah, lihat, update, dan hapus data biji kopi.
- 📋 **Mengelola BrewRecipe** — Catat resep seduh untuk setiap biji kopi.
- 🔒 **Autentikasi JWT** — Register dan login untuk mendapatkan akses ke endpoint terproteksi.

### Cara Menggunakan Autentikasi:
1. **Register** di endpoint `POST /auth/register`.
2. **Login** di endpoint `POST /auth/login` untuk mendapatkan token.
3. Klik tombol **Authorize 🔓** di pojok kanan atas, masukkan token.
4. Sekarang Anda bisa mengakses endpoint yang bertanda 🔒.
    """,
    version="1.0.0",
    contact={
        "name": "BrewLog API",
        "email": "brewlog@example.com",
    },
    license_info={
        "name": "MIT License",
    },
)

# ─────────────────────────────────────────────
# Buat Tabel Database Otomatis
# ─────────────────────────────────────────────
# create_all() akan membuat semua tabel yang belum ada di database.
# Jika tabel sudah ada, perintah ini akan diabaikan (tidak menghapus data).
Base.metadata.create_all(bind=engine)


# ─────────────────────────────────────────────
# Daftarkan Semua Router
# ─────────────────────────────────────────────
# Setiap router memiliki prefix dan tag tersendiri
app.include_router(auth.router)           # /auth/...
app.include_router(coffee_beans.router)   # /coffee-beans/...
app.include_router(brew_recipes.router)   # /brew-recipes/...


# ─────────────────────────────────────────────
# Root Endpoint (Health Check)
# ─────────────────────────────────────────────
@app.get("/", tags=["Root"], summary="Health Check")
def root():
    """
    Endpoint root sebagai health check.
    Mengembalikan pesan selamat datang dan link ke dokumentasi.
    """
    return {
        "message": "☕ Selamat datang di BrewLog API!",
        "status": "running",
        "docs": "http://127.0.0.1:8000/docs",
        "redoc": "http://127.0.0.1:8000/redoc",
        "version": "1.0.0",
    }
