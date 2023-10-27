from typing import Optional

from pydantic import BaseModel, ConfigDict


class ProductBase(BaseModel):
    name: str
    sku: str
    price: float
    brand: str


class ProductCreate(ProductBase):
    pass


class ProductUpdatePut(ProductBase):
    pass


class ProductUpdatePatch(ProductBase):
    name: Optional[str] = None
    sku: Optional[str] = None
    price: Optional[float] = None
    brand: Optional[str] = None


class Product(ProductBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class ProductPatchResponse(ProductUpdatePatch):
    model_config = ConfigDict(from_attributes=True)

    id: int
