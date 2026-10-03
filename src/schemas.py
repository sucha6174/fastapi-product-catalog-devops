"""Pydantic validation schemas for API request and response bodies."""
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class ProductBase(BaseModel):
    """Common attributes shared across product schemas."""

    name: str = Field(..., min_length=1, max_length=255, description="Name of the product")
    description: str = Field(..., min_length=1, description="Detailed product description")
    price: float = Field(..., gt=0, description="Product price (must be greater than 0)")
    stock: int = Field(..., ge=0, description="Product inventory stock (must be non-negative)")


class ProductCreate(ProductBase):
    """Request payload schema for creating a product (POST /products)."""

    pass


class ProductUpdate(BaseModel):
    """Request payload schema for updating an existing product (PUT /products/{id})."""

    name: Optional[str] = Field(default=None, min_length=1, max_length=255, description="Updated name")
    description: Optional[str] = Field(default=None, min_length=1, description="Updated description")
    price: Optional[float] = Field(default=None, gt=0, description="Updated price (must be greater than 0)")
    stock: Optional[int] = Field(default=None, ge=0, description="Updated stock (must be non-negative)")


class ProductResponse(ProductBase):
    """Response payload schema returning product details with primary key id."""

    id: int = Field(..., description="Unique product database identifier")

    model_config = ConfigDict(from_attributes=True)
