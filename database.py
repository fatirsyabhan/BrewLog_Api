"""
database.py - Konfigurasi koneksi database SQLite menggunakan SQLAlchemy.

File ini bertanggung jawab untuk:
1. Membuat engine SQLAlchemy yang terhubung ke SQLite.
2. Membuat session factory untuk interaksi database.
3. Menyediakan dependency `get_db` untuk FastAPI agar setiap request
   mendapat session database sendiri (dan otomatis ditutup setelahnya).
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# URL koneksi SQLite - file database akan dibuat otomatis di folder project
# "check_same_thread=False" diperlukan karena FastAPI berjalan multi-thread
SQLALCHEMY_DATABASE_URL = "sqlite:///./brewlog.db"

# Engine adalah "inti" koneksi ke database
# connect_args khusus untuk SQLite agar bisa diakses dari thread berbeda
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# SessionLocal adalah factory untuk membuat session database
# autocommit=False: kita harus commit manual (lebih aman)
# autoflush=False: data tidak otomatis dikirim ke DB sebelum query
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class untuk semua model SQLAlchemy kita
# Semua model akan mewarisi (inherit) dari class ini
Base = declarative_base()


def get_db():
    """
    Dependency function untuk FastAPI.
    
    Fungsi ini menjadi "generator" yang:
    1. Membuat session database baru untuk setiap request.
    2. Menyediakan session tersebut ke endpoint yang membutuhkan.
    3. Menutup session setelah request selesai (di blok finally).
    
    Penggunaan di endpoint:
        @router.get("/")
        def read_items(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db  # Menyediakan session ke endpoint
    finally:
        db.close()  # Pastikan session ditutup setelah request selesai
