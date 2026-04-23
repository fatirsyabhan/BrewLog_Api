"""
schemas/brew_recipe.py - Pydantic Schema untuk validasi data BrewRecipe.

Schema ini mendefinisikan struktur data untuk request dan response
yang berkaitan dengan resep penyeduhan kopi.
"""

from pydantic import BaseModel, Field
from typing import Optional


class BrewRecipeCreate(BaseModel):
    """
    Schema untuk membuat BrewRecipe baru (POST request).
    
    coffee_id: ID CoffeeBean yang terkait (harus sudah ada di database).
    method: Metode penyeduhan kopi.
    water_ratio: Rasio air terhadap kopi (format "1:15").
    grind_size: Ukuran gilingan biji kopi.
    notes: Catatan tambahan (opsional).
    """
    coffee_id: int = Field(..., gt=0, examples=[1])
    method: str = Field(
        ..., min_length=1, max_length=50,
        examples=["V60"],
        description="Metode seduh: V60, Moka Pot, French Press, AeroPress, dll."
    )
    water_ratio: str = Field(
        ..., min_length=1, max_length=20,
        examples=["1:15"],
        description="Rasio air terhadap kopi, contoh: 1:15"
    )
    grind_size: str = Field(
        ..., min_length=1, max_length=50,
        examples=["Medium"],
        description="Ukuran gilingan: Fine, Medium-Fine, Medium, Medium-Coarse, Coarse"
    )
    notes: Optional[str] = Field(
        None, max_length=500,
        examples=["Seduh dengan air 93°C, tunggu 30 detik untuk blooming"]
    )


class BrewRecipeUpdate(BaseModel):
    """
    Schema untuk update BrewRecipe (PUT request).
    Semua field opsional.
    """
    coffee_id: Optional[int] = Field(None, gt=0)
    method: Optional[str] = Field(None, min_length=1, max_length=50)
    water_ratio: Optional[str] = Field(None, min_length=1, max_length=20)
    grind_size: Optional[str] = Field(None, min_length=1, max_length=50)
    notes: Optional[str] = Field(None, max_length=500)


class BrewRecipeResponse(BaseModel):
    """
    Schema untuk response BrewRecipe.
    Menampilkan semua atribut termasuk ID dan coffee_id.
    """
    id: int
    coffee_id: int
    method: str
    water_ratio: str
    grind_size: str
    notes: Optional[str] = None

    model_config = {"from_attributes": True}
