from pydantic import BaseModel, ConfigDict, computed_field
from pydantic.alias_generators import to_camel


class CamelModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class LineItem(CamelModel):
    sku: str
    unit_price: float
    qty: int


class Order(CamelModel):
    order_id: int
    customer_email: str
    line_items: list[LineItem]
    coupon_code: str | None = None

    @computed_field
    @property
    def total(self) -> float:
        return round(sum(i.unit_price * i.qty for i in self.line_items), 2)

    def to_api(self) -> dict:
        return self.model_dump(by_alias=True, exclude_none=True)
