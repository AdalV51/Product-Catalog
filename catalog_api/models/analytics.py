from pydantic import BaseModel, ConfigDict


class ProductViewCountBase(BaseModel):
    product_id: int
    count: int


class ProductViewCountCreate(ProductViewCountBase):
    pass


class ProductViewCount(ProductViewCountBase):
    model_config = ConfigDict(from_attributes=True)
