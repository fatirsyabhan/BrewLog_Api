"""
routers/brew_recipes.py - Endpoint CRUD untuk entitas BrewRecipe (Child).

Endpoint:
    GET    /brew-recipes/         - Ambil semua BrewRecipe (bisa filter by coffee_id)
    POST   /brew-recipes/         - Buat BrewRecipe baru (🔒 Protected)
    GET    /brew-recipes/{id}     - Ambil BrewRecipe berdasarkan ID
    PUT    /brew-recipes/{id}     - Update BrewRecipe (🔒 Protected)
    DELETE /brew-recipes/{id}     - Hapus BrewRecipe (🔒 Protected)

Endpoint bertanda 🔒 membutuhkan JWT token di header:
    Authorization: Bearer <token>
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
from models.brew_recipe import BrewRecipe
from models.coffee_bean import CoffeeBean
from models.user import User
from schemas.brew_recipe import BrewRecipeCreate, BrewRecipeUpdate, BrewRecipeResponse
from auth.jwt_handler import get_current_user

router = APIRouter(prefix="/brew-recipes", tags=["Brew Recipes"])


# ─────────────────────────────────────────────
# READ ALL - Publik, bisa filter by coffee_id
# ─────────────────────────────────────────────
@router.get(
    "/",
    response_model=List[BrewRecipeResponse],
    status_code=status.HTTP_200_OK,
    summary="Daftar Semua Brew Recipe",
)
def get_all_recipes(
    coffee_id: Optional[int] = Query(None, description="Filter resep berdasarkan ID kopi"),
    db: Session = Depends(get_db),
):
    """
    Mengambil semua BrewRecipe. Bisa difilter menggunakan query parameter coffee_id.

    Contoh:
        GET /brew-recipes/              -> Semua resep
        GET /brew-recipes/?coffee_id=1  -> Hanya resep untuk kopi ID 1
    """
    query = db.query(BrewRecipe)
    if coffee_id is not None:
        query = query.filter(BrewRecipe.coffee_id == coffee_id)
    return query.all()


# ─────────────────────────────────────────────
# CREATE - 🔒 Membutuhkan JWT token
# ─────────────────────────────────────────────
@router.post(
    "/",
    response_model=BrewRecipeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Tambah Brew Recipe Baru 🔒",
)
def create_recipe(
    recipe_data: BrewRecipeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Membuat BrewRecipe baru. Membutuhkan autentikasi JWT.

    Validasi:
    - coffee_id harus merujuk ke CoffeeBean yang sudah ada di database.

    Returns:
        201 Created: Data BrewRecipe yang baru dibuat.
        404 Not Found: CoffeeBean dengan coffee_id tidak ditemukan.
    """
    # Validasi bahwa CoffeeBean dengan coffee_id tersebut ada
    coffee = db.query(CoffeeBean).filter(CoffeeBean.id == recipe_data.coffee_id).first()
    if not coffee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"CoffeeBean dengan ID {recipe_data.coffee_id} tidak ditemukan"
        )

    new_recipe = BrewRecipe(**recipe_data.model_dump())
    db.add(new_recipe)
    db.commit()
    db.refresh(new_recipe)
    return new_recipe


# ─────────────────────────────────────────────
# READ ONE - Publik
# ─────────────────────────────────────────────
@router.get(
    "/{recipe_id}",
    response_model=BrewRecipeResponse,
    status_code=status.HTTP_200_OK,
    summary="Detail Brew Recipe",
)
def get_recipe(recipe_id: int, db: Session = Depends(get_db)):
    """
    Mengambil detail satu BrewRecipe berdasarkan ID.

    Returns:
        200 OK: Data BrewRecipe.
        404 Not Found: BrewRecipe tidak ditemukan.
    """
    recipe = db.query(BrewRecipe).filter(BrewRecipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"BrewRecipe dengan ID {recipe_id} tidak ditemukan"
        )
    return recipe


# ─────────────────────────────────────────────
# UPDATE - 🔒 Membutuhkan JWT token
# ─────────────────────────────────────────────
@router.put(
    "/{recipe_id}",
    response_model=BrewRecipeResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Brew Recipe 🔒",
)
def update_recipe(
    recipe_id: int,
    recipe_data: BrewRecipeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Mengupdate BrewRecipe. Membutuhkan autentikasi JWT.
    Jika coffee_id diubah, validasi bahwa CoffeeBean baru ada di database.

    Returns:
        200 OK: Data BrewRecipe yang sudah diupdate.
        404 Not Found: BrewRecipe atau CoffeeBean tidak ditemukan.
    """
    recipe = db.query(BrewRecipe).filter(BrewRecipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"BrewRecipe dengan ID {recipe_id} tidak ditemukan"
        )

    update_data = recipe_data.model_dump(exclude_unset=True)

    # Jika coffee_id diubah, pastikan CoffeeBean baru ada
    if "coffee_id" in update_data:
        coffee = db.query(CoffeeBean).filter(
            CoffeeBean.id == update_data["coffee_id"]
        ).first()
        if not coffee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"CoffeeBean dengan ID {update_data['coffee_id']} tidak ditemukan"
            )

    for field, value in update_data.items():
        setattr(recipe, field, value)

    db.commit()
    db.refresh(recipe)
    return recipe


# ─────────────────────────────────────────────
# DELETE - 🔒 Membutuhkan JWT token
# ─────────────────────────────────────────────
@router.delete(
    "/{recipe_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Hapus Brew Recipe 🔒",
)
def delete_recipe(
    recipe_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Menghapus BrewRecipe. Membutuhkan autentikasi JWT.

    Returns:
        204 No Content: Berhasil dihapus.
        404 Not Found: BrewRecipe tidak ditemukan.
    """
    recipe = db.query(BrewRecipe).filter(BrewRecipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"BrewRecipe dengan ID {recipe_id} tidak ditemukan"
        )

    db.delete(recipe)
    db.commit()
