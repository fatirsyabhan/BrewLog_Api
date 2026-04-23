"""
routers/coffee_beans.py - Endpoint CRUD untuk entitas CoffeeBean (Parent).

Endpoint:
    GET    /coffee-beans/         - Ambil semua CoffeeBean
    POST   /coffee-beans/         - Buat CoffeeBean baru (🔒 Protected)
    GET    /coffee-beans/{id}     - Ambil CoffeeBean berdasarkan ID (+ recipes)
    PUT    /coffee-beans/{id}     - Update CoffeeBean (🔒 Protected)
    DELETE /coffee-beans/{id}     - Hapus CoffeeBean (🔒 Protected)

Endpoint bertanda 🔒 membutuhkan JWT token di header:
    Authorization: Bearer <token>
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models.coffee_bean import CoffeeBean
from models.user import User
from schemas.coffee_bean import (
    CoffeeBeanCreate,
    CoffeeBeanUpdate,
    CoffeeBeanResponse,
    CoffeeBeanWithRecipes,
)
from auth.jwt_handler import get_current_user

router = APIRouter(prefix="/coffee-beans", tags=["Coffee Beans"])


# ─────────────────────────────────────────────
# READ ALL - Tidak perlu autentikasi (publik)
# ─────────────────────────────────────────────
@router.get(
    "/",
    response_model=List[CoffeeBeanResponse],
    status_code=status.HTTP_200_OK,
    summary="Daftar Semua Coffee Bean",
)
def get_all_coffee_beans(db: Session = Depends(get_db)):
    """
    Mengambil semua data CoffeeBean dari database.
    Endpoint ini bersifat publik (tidak membutuhkan token).
    """
    beans = db.query(CoffeeBean).all()
    return beans


# ─────────────────────────────────────────────
# CREATE - 🔒 Membutuhkan JWT token
# ─────────────────────────────────────────────
@router.post(
    "/",
    response_model=CoffeeBeanResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Tambah Coffee Bean Baru 🔒",
)
def create_coffee_bean(
    bean_data: CoffeeBeanCreate,
    db: Session = Depends(get_db),
    # Dependency get_current_user memastikan request memiliki JWT token yang valid
    current_user: User = Depends(get_current_user),
):
    """
    Membuat CoffeeBean baru. Membutuhkan autentikasi (JWT token).

    Alur:
    1. Validasi token JWT (dilakukan otomatis oleh `get_current_user`).
    2. Buat objek CoffeeBean dari data yang diterima.
    3. Simpan ke database.
    4. Return data yang baru dibuat dengan status 201 Created.
    """
    new_bean = CoffeeBean(**bean_data.model_dump())
    db.add(new_bean)
    db.commit()
    db.refresh(new_bean)
    return new_bean


# ─────────────────────────────────────────────
# READ ONE - Publik, menampilkan data + recipes
# ─────────────────────────────────────────────
@router.get(
    "/{bean_id}",
    response_model=CoffeeBeanWithRecipes,
    status_code=status.HTTP_200_OK,
    summary="Detail Coffee Bean (dengan Resep)",
)
def get_coffee_bean(bean_id: int, db: Session = Depends(get_db)):
    """
    Mengambil detail satu CoffeeBean beserta semua BrewRecipe yang terkait.
    Memanfaatkan SQLAlchemy relationship() untuk memuat data relasi.

    Returns:
        200 OK: Data CoffeeBean + list BrewRecipe terkait.
        404 Not Found: CoffeeBean dengan ID tersebut tidak ditemukan.
    """
    bean = db.query(CoffeeBean).filter(CoffeeBean.id == bean_id).first()
    if not bean:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"CoffeeBean dengan ID {bean_id} tidak ditemukan"
        )
    return bean


# ─────────────────────────────────────────────
# UPDATE - 🔒 Membutuhkan JWT token
# ─────────────────────────────────────────────
@router.put(
    "/{bean_id}",
    response_model=CoffeeBeanResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Coffee Bean 🔒",
)
def update_coffee_bean(
    bean_id: int,
    bean_data: CoffeeBeanUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Mengupdate data CoffeeBean. Membutuhkan autentikasi JWT.
    Hanya field yang dikirim yang akan diupdate (partial update).

    Returns:
        200 OK: Data CoffeeBean yang sudah diupdate.
        404 Not Found: CoffeeBean tidak ditemukan.
    """
    bean = db.query(CoffeeBean).filter(CoffeeBean.id == bean_id).first()
    if not bean:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"CoffeeBean dengan ID {bean_id} tidak ditemukan"
        )

    # exclude_unset=True: hanya update field yang benar-benar dikirim oleh client
    update_data = bean_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(bean, field, value)

    db.commit()
    db.refresh(bean)
    return bean


# ─────────────────────────────────────────────
# DELETE - 🔒 Membutuhkan JWT token
# ─────────────────────────────────────────────
@router.delete(
    "/{bean_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Hapus Coffee Bean 🔒",
)
def delete_coffee_bean(
    bean_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Menghapus CoffeeBean. Membutuhkan autentikasi JWT.
    Karena ada cascade, semua BrewRecipe terkait juga ikut terhapus.

    Returns:
        204 No Content: Berhasil dihapus (tidak ada response body).
        404 Not Found: CoffeeBean tidak ditemukan.
    """
    bean = db.query(CoffeeBean).filter(CoffeeBean.id == bean_id).first()
    if not bean:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"CoffeeBean dengan ID {bean_id} tidak ditemukan"
        )

    db.delete(bean)
    db.commit()
    # 204 No Content - tidak perlu return apapun
