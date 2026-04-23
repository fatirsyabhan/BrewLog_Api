"""
models/coffee_bean.py - Model SQLAlchemy untuk entitas CoffeeBean (Parent).

CoffeeBean merepresentasikan biji kopi dengan informasi seperti
nama, roastery, asal, dan level roasting.

Relasi: One-to-Many dengan BrewRecipe
(Satu CoffeeBean bisa memiliki banyak BrewRecipe)
"""

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database import Base


class CoffeeBean(Base):
    """
    Tabel 'coffee_beans' di database.
    
    Atribut:
        id          : Primary key, auto-increment
        name        : Nama biji kopi (contoh: "Ethiopia Yirgacheffe")
        roastery    : Nama roastery/penyangrai (contoh: "Tanamera Coffee")
        origin      : Asal negara/daerah (contoh: "Ethiopia")
        roast_level : Level roasting (contoh: "Light", "Medium", "Dark")
    """
    __tablename__ = "coffee_beans"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False, index=True)
    roastery = Column(String(100), nullable=False)
    origin = Column(String(100), nullable=False)
    roast_level = Column(String(50), nullable=False)

    # --- Relasi One-to-Many ---
    # "recipes" adalah atribut virtual (tidak ada kolom di tabel),
    # yang memungkinkan akses langsung ke semua BrewRecipe terkait.
    # 
    # back_populates="coffee_bean": membuat relasi dua arah,
    #   sehingga dari BrewRecipe juga bisa akses CoffeeBean-nya.
    #
    # cascade="all, delete-orphan": jika CoffeeBean dihapus,
    #   semua BrewRecipe terkait juga akan ikut terhapus.
    recipes = relationship(
        "BrewRecipe",
        back_populates="coffee_bean",
        cascade="all, delete-orphan"
    )
