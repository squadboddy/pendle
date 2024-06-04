from pydantic import BaseModel

from config.wallet_scanner.points_price import PointsPrice
from config.wallet_scanner.protocol import Protocol


class WalletScanner(BaseModel):
    protocols: list[Protocol]
    points_price: PointsPrice
    wallets: list[dict]
