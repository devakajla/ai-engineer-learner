from pydantic import BaseModel, Field, TypeAdapter, computed_field


class Page[T](BaseModel):
    items: list[T]
    total: int = Field(ge=0)
    limit: int = Field(ge=1, le=100)
    offset: int = Field(ge=0)

    @computed_field
    @property
    def has_more(self) -> bool:
        return self.offset + len(self.items) < self.total


class Product(BaseModel):
    name: str
    price: float = Field(gt=0)


def paginate[T](items: list[T], limit: int, offset: int) -> Page[T]:
    return Page[T](items=items[offset : offset + limit], total=len(items), limit=limit, offset=offset)


_products = TypeAdapter(list[Product])


def parse_products(raw_json: str | bytes) -> list[Product]:
    return _products.validate_json(raw_json)
