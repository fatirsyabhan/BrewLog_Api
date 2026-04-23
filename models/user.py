"""
models/user.py - Model SQLAlchemy untuk entitas User.

User digunakan untuk autentikasi JWT (registrasi & login).
Password disimpan dalam bentuk hash (bukan plain text) untuk keamanan.
"""

from sqlalchemy import Column, Integer, String
from database import Base


class User(Base):
    """
    Tabel 'users' di database.
    
    Atribut:
        id              : Primary key, auto-increment
        username        : Username unik untuk login
        hashed_password : Password yang sudah di-hash menggunakan bcrypt
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
