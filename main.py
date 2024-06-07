from pprint import pprint

from config.config import config
from pendle.pendle_handler import PendleHandler
from dynamic_points_price.dynamic_points_price import setup_calculate_points_prices
from wallet_scanner.wallet_scanner import WalletScanner


def main():
    if config.dynamic_points_price_enabled:
        setup_calculate_points_prices()

    if config.wallets_scan_enabled:
        print("Starting wallets scanning")
        for wallet in config.wallet_scanner.wallets:
            print("==========================", wallet["address"], "==========================", sep="\n")
            get_wallet_info(wallet)

        print("\n")

    if config.pendle_profit_calculation_enabled:
        calculate_pendle_pulls_profit()


def calculate_pendle_pulls_profit():
    """Calculates profit of current pendle pulls."""
    print("Starting pendle pools scanning")

    pprint(PendleHandler.calculate_pools_profits())


def get_wallet_info(wallet_info: dict):
    """Get amount of points for wallet and calculate its sum."""
    totals = []
    for protocol in config.wallet_scanner.protocols:

        print("************", protocol.key, "************", sep="\n")
        protocol_data = WalletScanner.calculate_points_value(
            wallet_info["address"],
            wallet_info["previous_points"][protocol.key],
            protocol,
        )
        totals.append(protocol_data)

    total_el = sum([protocol_amount["el"] for protocol_amount in totals])
    total_lrt = sum([protocol_amount["lrt"] for protocol_amount in totals])

    print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
    print(f"Total el value: {total_el} USD")
    print(f"Total lrt value: {total_lrt} USD")
    print(f"Total {total_el + total_lrt} USD")


if __name__ == '__main__':
    main()
