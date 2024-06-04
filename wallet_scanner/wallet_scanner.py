from requests import Response, get

from config.config import config
from config.wallet_scanner.protocol import Protocol
from tools.tools import get_nested_value


class WalletScanner:

    @classmethod
    def calculate_points_value(
        cls,
        wallet: str,
        previous_points: dict,
        protocol: Protocol,
    ) -> dict:
        points = cls.extract_current_point_amount(wallet, protocol)
        el_points = points["el"]
        current_points = points["current"]
        el_points_current_season = el_points - previous_points.get("previous_season_el_points_amount", 0)
        total_el_price_in_current_season = el_points_current_season * config.wallet_scanner.points_price.el

        current_points_current_season = current_points - previous_points.get("previous_season_points_amount", 0)
        total_protocol_price_in_current_season = current_points_current_season * protocol.point_price

        print(f"El: \nTotal points: {el_points} \nCurrent season points: {el_points_current_season}")
        print(f"Current season el points price: {total_el_price_in_current_season}")

        print(f"Total protocol points: {current_points} \nCurrent season points: {current_points_current_season}")
        print(f"Current season points price: {total_protocol_price_in_current_season}")
        print("\n")
        return {
            "el": total_el_price_in_current_season,
            "lrt": total_protocol_price_in_current_season
        }

    @classmethod
    def extract_current_point_amount(cls, wallet: str, protocol: Protocol) -> dict:
        try:
            # fetch data from api
            response: Response = get(f"{protocol.points_url}/{wallet}")
            response.raise_for_status()
        except Exception as e:
            print(f"Failed to extract points from {protocol.points_url}")
            print(e)
            return {
                "el": 0,
                "current": 0
            }

        try:
            # parse data
            data = response.json()
            return {
                "el": float(get_nested_value(data, protocol.el_points_location) or 0),
                "current": float(get_nested_value(data, protocol.protocol_points_location) or 0),
            }
        except Exception as e:
            print("Error parsing renzo points", e)
            return {
                "el": 0,
                "current": 0
            }

