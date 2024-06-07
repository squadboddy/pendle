import json

from pydantic import BaseModel
from dune_client.client import DuneClient

from config.pendle.pendle import Pendle
from config.dynamic_points_price.dynamic_points_price import DynamicPointsPrice
from config.wallet_scanner.wallet_scanner import WalletScanner


class Config(BaseModel):
    """Base configuration for LRT calculations."""
    wallets_scan_enabled: bool
    wallet_scanner: WalletScanner
    pendle_profit_calculation_enabled: bool
    pendle: Pendle
    dynamic_points_price_enabled: bool
    dynamic_points_price: DynamicPointsPrice
    dun_api_token: str


def __setup_config() -> Config:
    """Private function for internal usage."""

    with open('config.json', 'r') as f:
        config_data = json.load(f)
    return Config(**config_data)


config = __setup_config()

dune = DuneClient(
    api_key=config.dun_api_token,
    base_url="https://api.dune.com",
    request_timeout=300  # request will time out after 300 seconds
)
