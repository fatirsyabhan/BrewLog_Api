"""
auth/jwt_handler.py - Logika JWT (JSON Web Token) dan keamanan.

File ini menangani:
1. Hashing password menggunakan bcrypt.
2. Pembuatan JWT access token.
3. Verifikasi dan decode JWT token.
4. Dependency `get_current_user` untuk melindungi endpoint.

Alur autentikasi:
  Register -> Password di-hash -> Simpan ke DB
  Login -> Verifikasi password -> Buat JWT token -> Kirim ke client
  Request terproteksi -> Client kirim token di header -> Decode & validasi
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from database import get_db
from models.user import User
from schemas.user import TokenData

# --- Konfigurasi Secret Key & Algoritma ---
# SECRET_KEY: kunci rahasia untuk menandatangani JWT token
# PENTING: Di production, gunakan environment variable, jangan hardcode!
SECRET_KEY = "brewlog-secret-key-uts-2026-sangat-rahasia"
ALGORITHM = "HS256"  # Algoritma hashing untuk JWT
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Token berlaku 30 menit

# --- Password Hashing Context ---
# CryptContext menggunakan bcrypt untuk hashing password
# schemes=["bcrypt"]: algoritma yang digunakan
# deprecated="auto": otomatis migrasi jika ada scheme lama
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- OAuth2 Scheme ---
# OAuth2PasswordBearer menentukan URL untuk mendapatkan token
# FastAPI akan otomatis menambahkan tombol "Authorize" di Swagger UI
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Memverifikasi apakah plain password cocok dengan hashed password.
    Menggunakan bcrypt untuk perbandingan yang aman.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Meng-hash password menggunakan bcrypt.
    Setiap kali di-hash, hasilnya berbeda (karena salt random).
    """
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Membuat JWT access token.
    
    Args:
        data: Data yang akan disimpan di dalam token (biasanya {"sub": username})
        expires_delta: Durasi token berlaku (default: 30 menit)
    
    Returns:
        JWT token string yang sudah di-encode
    
    Token berisi:
        - sub: subject (username)
        - exp: expiration time (waktu kadaluarsa)
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency untuk mendapatkan user yang sedang login dari JWT token.
    
    Digunakan sebagai dependency di endpoint yang membutuhkan autentikasi:
        @router.post("/", dependencies=[Depends(get_current_user)])
        def protected_endpoint():
            ...
    
    Alur:
    1. Ambil token dari header "Authorization: Bearer <token>"
    2. Decode token menggunakan SECRET_KEY
    3. Ambil username dari payload token
    4. Cari user di database berdasarkan username
    5. Jika valid, return User object; jika tidak, raise 401 error
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token tidak valid atau sudah kadaluarsa",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    # Cari user di database
    user = db.query(User).filter(User.username == token_data.username).first()
    if user is None:
        raise credentials_exception
    
    return user
