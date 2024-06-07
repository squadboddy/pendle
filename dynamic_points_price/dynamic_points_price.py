from config.config import config
from dynamic_points_price.kelp import calculate_kelp_point_price
from dynamic_points_price.renzo import calculate_renzo_point_price
from dynamic_points_price.zircuit import calculate_zircuit_point_price


def setup_calculate_points_prices():
    """Calculate and setup points prices base on chains data."""
    renzo = calculate_renzo_point_price()
    kelp = calculate_kelp_point_price()
    zircuit = calculate_zircuit_point_price()

    if config.wallets_scan_enabled:
        for protocol in config.wallet_scanner.protocols:
            if protocol.key == "renzo" and renzo:
                protocol.point_price = renzo
            if protocol.key == "kelp" and kelp:
                protocol.point_price = kelp

        if zircuit:
            config.wallet_scanner.points_price.zircuit = zircuit

    if config.pendle_profit_calculation_enabled:
        for protocol in config.pendle.lrt:
            if protocol.key == "renzo" and renzo:
                protocol.point_price = renzo
            if protocol.key == "kelp" and kelp:
                protocol.point_price = kelp

        if zircuit:
            config.pendle.base_protocols.zircuit_price = zircuit

    print("Calculated points prices successfully set to config")
