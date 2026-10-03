"""CRUD (Create, Read, Update, Delete) database operations."""
from typing import List, Optional
from sqlmodel import Session, select

from src.models import Product
from src.schemas import ProductCreate, ProductUpdate


def create_product(session: Session, product_in: ProductCreate) -> Product:
    """Insert a new product record into the database."""
    product_data = product_in.model_dump()
    db_product = Product(**product_data)
    session.add(db_product)
    session.commit()
    session.refresh(db_product)
    return db_product


def get_products(session: Session, skip: int = 0, limit: int = 100) -> List[Product]:
    """Retrieve multiple products with optional pagination."""
    statement = select(Product).offset(skip).limit(limit)
    return list(session.exec(statement).all())


def get_product_by_id(session: Session, product_id: int) -> Optional[Product]:
    """Fetch a single product by its primary key ID."""
    return session.get(Product, product_id)


def update_product(session: Session, db_product: Product, product_in: ProductUpdate) -> Product:
    """Update fields of an existing product record."""
    update_data = product_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_product, field, value)
    session.add(db_product)
    session.commit()
    session.refresh(db_product)
    return db_product


def delete_product(session: Session, db_product: Product) -> None:
    """Remove a product record from the database."""
    session.delete(db_product)
    session.commit()
