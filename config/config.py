import json

from pydantic import BaseModel

from config.pendle.pendle import Pendle
from config.wallet_scanner.wallet_scanner import WalletScanner


class Config(BaseModel):
    """Base configuration for LRT calculations."""
    wallets_scan_enabled: bool
    wallet_scanner: WalletScanner
    pendle_profit_calculation_enabled: bool
    pendle: Pendle


def __setup_config() -> Config:
    """Private function for internal usage."""

    with open('config.json', 'r') as f:
        config_data = json.load(f)
    return Config(**config_data)


config = __setup_config()
