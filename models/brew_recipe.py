"""
models/brew_recipe.py - Model SQLAlchemy untuk entitas BrewRecipe (Child).

BrewRecipe merepresentasikan resep penyeduhan kopi yang terkait
dengan satu CoffeeBean tertentu melalui foreign key.

Relasi: Many-to-One dengan CoffeeBean
(Banyak BrewRecipe bisa merujuk ke satu CoffeeBean)
"""

from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base


class BrewRecipe(Base):
    """
    Tabel 'brew_recipes' di database.
    
    Atribut:
        id          : Primary key, auto-increment
        coffee_id   : Foreign key ke tabel coffee_beans
        method      : Metode seduh (contoh: "V60", "Moka Pot", "French Press")
        water_ratio : Rasio air terhadap kopi (contoh: "1:15", "1:16")
        grind_size  : Ukuran gilingan (contoh: "Fine", "Medium", "Coarse")
        notes       : Catatan tambahan tentang resep
    """
    __tablename__ = "brew_recipes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Foreign Key - menghubungkan BrewRecipe ke CoffeeBean
    # ondelete="CASCADE": jika CoffeeBean dihapus di level DB, recipe juga dihapus
    coffee_id = Column(
        Integer,
        ForeignKey("coffee_beans.id", ondelete="CASCADE"),
        nullable=False
    )
    
    method = Column(String(50), nullable=False)       # Metode seduh
    water_ratio = Column(String(20), nullable=False)   # Rasio air:kopi
    grind_size = Column(String(50), nullable=False)    # Ukuran gilingan
    notes = Column(Text, nullable=True)                # Catatan (opsional)

    # --- Relasi balik ke CoffeeBean ---
    # back_populates="recipes": sinkronisasi dua arah dengan CoffeeBean.recipes
    coffee_bean = relationship("CoffeeBean", back_populates="recipes")
