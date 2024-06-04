from pydantic import BaseModel, PositiveFloat


class LrtProtocol(BaseModel):
    ticker: str
    key: str
    point_price: PositiveFloat
    analise_before_date: str
    points_per_hour: PositiveFloat
    wallet_multiplier: PositiveFloat
