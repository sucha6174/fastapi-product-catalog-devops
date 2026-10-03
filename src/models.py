"""SQLModel database models for Product Catalog."""
from typing import Optional
from sqlmodel import Field, SQLModel


class Product(SQLModel, table=True):
    """Database table schema for Product records."""

    __tablename__ = "products"

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    name: str = Field(index=True, nullable=False, max_length=255)
    description: str = Field(nullable=False)
    price: float = Field(nullable=False)
    stock: int = Field(nullable=False)
