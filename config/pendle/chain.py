from pydantic import BaseModel, PositiveInt


class Chain(BaseModel):
    name: str
    id: PositiveInt
