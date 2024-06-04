from pydantic import BaseModel, NonNegativeFloat


class PointsPrice(BaseModel):
    """Use for points that represented as separate protocol."""

    el: NonNegativeFloat
    zircuit: NonNegativeFloat
