"""
schemas/user.py - Pydantic Schema untuk autentikasi User.

Schema ini digunakan untuk validasi data registrasi, login,
dan format JWT token response.
"""

from pydantic import BaseModel, Field
from typing import Optional


class UserCreate(BaseModel):
    """
    Schema untuk registrasi user baru.
    Username minimal 3 karakter, password minimal 6 karakter.
    """
    username: str = Field(
        ..., min_length=3, max_length=50,
        examples=["brewmaster"],
        description="Username unik untuk login"
    )
    password: str = Field(
        ..., min_length=6, max_length=100,
        examples=["kopi123"],
        description="Password minimal 6 karakter"
    )


class UserResponse(BaseModel):
    """Schema response setelah registrasi berhasil."""
    id: int
    username: str

    model_config = {"from_attributes": True}


class Token(BaseModel):
    """
    Schema response JWT token setelah login berhasil.
    
    access_token: JWT token string yang digunakan untuk autentikasi.
    token_type: Tipe token, selalu "bearer".
    """
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """
    Schema internal untuk data yang tersimpan di dalam JWT token.
    Digunakan saat decode token untuk mendapatkan username.
    """
    username: Optional[str] = None
