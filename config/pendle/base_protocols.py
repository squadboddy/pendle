from pydantic import BaseModel, PositiveFloat


class BaseProtocols(BaseModel):
    el_price: PositiveFloat
    zircuit_price: PositiveFloat
    el_wallet_multiplier: PositiveFloat
    zircuit_wallet_multiplier: PositiveFloat
    el_points_per_hour: PositiveFloat
    zircuit_points_per_hour: PositiveFloat
