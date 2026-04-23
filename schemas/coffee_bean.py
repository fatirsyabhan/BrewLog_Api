"""
schemas/coffee_bean.py - Pydantic Schema untuk validasi data CoffeeBean.

Pydantic schema berfungsi sebagai:
1. Validasi otomatis untuk request body (input dari client).
2. Serialisasi data untuk response (output ke client).
3. Dokumentasi otomatis di Swagger UI.

Setiap schema memiliki peran berbeda:
- Create: validasi data saat membuat resource baru
- Update: validasi data saat mengupdate (semua field opsional)
- Response: format data yang dikirim kembali ke client
"""

from pydantic import BaseModel, Field
from typing import Optional, List


class BrewRecipeNested(BaseModel):
    """Schema ringkas untuk BrewRecipe saat ditampilkan di dalam CoffeeBean."""
    id: int
    method: str
    water_ratio: str
    grind_size: str
    notes: Optional[str] = None

    # model_config menggantikan class Config di Pydantic v2
    # from_attributes=True memungkinkan Pydantic membaca data dari ORM object
    model_config = {"from_attributes": True}


class CoffeeBeanCreate(BaseModel):
    """
    Schema untuk membuat CoffeeBean baru (POST request).
    Semua field wajib diisi (tidak ada yang opsional).
    
    Field(...) artinya field ini required.
    min_length dan max_length memberikan batasan panjang string.
    """
    name: str = Field(..., min_length=1, max_length=100, examples=["Ethiopia Yirgacheffe"])
    roastery: str = Field(..., min_length=1, max_length=100, examples=["Tanamera Coffee"])
    origin: str = Field(..., min_length=1, max_length=100, examples=["Ethiopia"])
    roast_level: str = Field(..., min_length=1, max_length=50, examples=["Light"])


class CoffeeBeanUpdate(BaseModel):
    """
    Schema untuk update CoffeeBean (PUT request).
    Semua field opsional - hanya field yang dikirim yang akan diupdate.
    """
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    roastery: Optional[str] = Field(None, min_length=1, max_length=100)
    origin: Optional[str] = Field(None, min_length=1, max_length=100)
    roast_level: Optional[str] = Field(None, min_length=1, max_length=50)


class CoffeeBeanResponse(BaseModel):
    """
    Schema untuk response CoffeeBean (tanpa daftar resep).
    Digunakan saat menampilkan list atau single CoffeeBean.
    """
    id: int
    name: str
    roastery: str
    origin: str
    roast_level: str

    model_config = {"from_attributes": True}


class CoffeeBeanWithRecipes(BaseModel):
    """
    Schema untuk response CoffeeBean lengkap dengan daftar resep.
    Digunakan saat menampilkan detail CoffeeBean (GET by ID).
    """
    id: int
    name: str
    roastery: str
    origin: str
    roast_level: str
    recipes: List[BrewRecipeNested] = []

    model_config = {"from_attributes": True}
