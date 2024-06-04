from pydantic import BaseModel, NonNegativeFloat, HttpUrl


class Protocol(BaseModel):
    """Data required for protocol parsing."""

    key: str
    point_price: NonNegativeFloat
    points_url: HttpUrl
    el_points_location: str
    protocol_points_location: str
