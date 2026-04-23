"""
routers/auth.py - Endpoint untuk registrasi dan login user.

Endpoint:
    POST /auth/register  - Mendaftarkan user baru
    POST /auth/login     - Login dan mendapatkan JWT token
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from database import get_db
from models.user import User
from schemas.user import UserCreate, UserResponse, Token
from auth.jwt_handler import get_password_hash, verify_password, create_access_token

# APIRouter memisahkan endpoint auth dari router lain
# prefix="/auth": semua endpoint di file ini akan diawali /auth
# tags=["Auth"]: pengelompokan di Swagger UI
router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrasi User Baru",
    description="Mendaftarkan user baru dengan username dan password."
)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Endpoint registrasi user baru.
    
    Alur:
    1. Cek apakah username sudah digunakan.
    2. Hash password menggunakan bcrypt.
    3. Simpan user baru ke database.
    4. Return data user yang baru dibuat (tanpa password).
    
    Returns:
        201 Created: Berhasil membuat user baru.
        400 Bad Request: Username sudah digunakan.
    """
    # Cek apakah username sudah ada
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Username '{user_data.username}' sudah digunakan"
        )

    # Hash password sebelum disimpan ke database
    hashed_pw = get_password_hash(user_data.password)

    # Buat objek User baru
    new_user = User(username=user_data.username, hashed_password=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)  # Refresh untuk mendapatkan ID yang baru di-generate

    return new_user


@router.post(
    "/login",
    response_model=Token,
    status_code=status.HTTP_200_OK,
    summary="Login User",
    description="Login dengan username dan password untuk mendapatkan JWT token."
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Endpoint login user.

    Menggunakan OAuth2PasswordRequestForm sehingga Swagger UI menampilkan
    form username & password dengan tombol "Authorize".

    Alur:
    1. Cari user berdasarkan username.
    2. Verifikasi password dengan bcrypt.
    3. Buat JWT access token.
    4. Return token ke client.

    Returns:
        200 OK: Login berhasil, return JWT token.
        401 Unauthorized: Username atau password salah.
    """
    # Cari user di database
    user = db.query(User).filter(User.username == form_data.username).first()

    # Verifikasi user dan password
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username atau password salah",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Buat JWT token dengan username sebagai "subject" (sub)
    access_token = create_access_token(data={"sub": user.username})

    return {"access_token": access_token, "token_type": "bearer"}
