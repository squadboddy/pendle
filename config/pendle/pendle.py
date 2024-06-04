from pydantic import BaseModel, PositiveInt

from config.pendle.base_protocols import BaseProtocols
from config.pendle.chain import Chain
from config.pendle.lrt_protocol import LrtProtocol


class Pendle(BaseModel):
    chains: list[Chain]
    amount_to_invest: PositiveInt
    filter_negative_profit: bool
    yt_price_location: str
    base_protocols: BaseProtocols
    lrt: list[LrtProtocol]
