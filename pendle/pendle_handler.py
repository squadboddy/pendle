from requests import get, post
from datetime import datetime

from config.config import config
from config.pendle.chain import Chain
from config.pendle.lrt_protocol import LrtProtocol
from tools.tools import get_nested_value


class PendleHandler:
    @classmethod
    def get_pools_by_ticker(cls, chain_id: int, ticker: str):
        """
        Find pools in specific chain filtered by ticker.

        Ticker should be a core token like eeth for Ether.fi
        """
        try:
            params = {
                "order_by": "expiry:1",
                "skip": 0,
                "limit": 100,
                "is_expired": False,
                "is_active": True,
                "categoryId": "lrt",
                "q": ticker
            }

            response = get(f"https://api-v2.pendle.finance/core/v1/{chain_id}/markets", params=params)
            response.raise_for_status()
            data = response.json()
            return data
        except Exception as e:
            print(f"An error occurred while fetching pools for chain_id: {chain_id} and ticker: {ticker}")
            print(e)

    @classmethod
    def filter_pools_by_date(cls, pools: list[dict], filter_date: str):
        """Find only pools that finished before specified date."""
        last_day_to_search = datetime.fromisoformat(filter_date.replace("z", ""))

        return [
            pool for pool in pools if datetime.fromisoformat(pool["expiry"].replace('Z', '')) <= last_day_to_search
        ]

    @classmethod
    def __get_chain_pools_profits(cls, chain: Chain):
        all_protocols_profits = []
        for protocol in config.pendle.lrt:
            all_protocols_profits.extend(cls.__get_protocol_pools_profits(chain, protocol))
        return all_protocols_profits

    @classmethod
    def __get_protocol_pools_profits(cls, chain: Chain, protocol: LrtProtocol):
        # find all pools for chosen chain and protocol
        pools = cls.get_pools_by_ticker(chain.id, protocol.ticker)

        if not pools:
            print(f"No pools found for {chain.name} protocol ticker {protocol.ticker}")
            return []

        # match pools that ends before spicified date
        filtered_pools = cls.filter_pools_by_date(pools["results"], protocol.analise_before_date)

        # chose pools inner id
        filtered_pools_addresses = [pool["address"] for pool in filtered_pools]
        # get multipliers for chosen pools
        pools_multipliers = cls.__get_pool_multipliers(chain.id, [pool["address"] for pool in filtered_pools])
        # convert multiplier for inner format
        converted_pools_multipliers = cls.__convert_multipliers(pools_multipliers, filtered_pools_addresses) \
            if pools_multipliers else {}

        pools_profit = []
        # calculate pools profit. Include all points which will be earned until pool expiration
        # and convert points to usd according to estimated price
        for pool in filtered_pools:
            pool_multipliers = converted_pools_multipliers.get(pool["address"], {})

            # skip pools without multiplier.
            if not pool_multipliers:
                continue

            pool_profit = cls.__get_pool_profit(chain, pool, pool_multipliers, protocol)
            pools_profit.append(pool_profit)

        return pools_profit

    @classmethod
    def calculate_pools_profits(cls) -> list[dict]:
        all_chain_profits = []
        for chain in config.pendle.chains:
            all_chain_profits.extend(cls.__get_chain_pools_profits(chain))
        # filter pools with negative profit
        if config.pendle.filter_negative_profit:
            all_chain_profits = [profit for profit in all_chain_profits if profit.get("value_delta", -1) >= 0]

        return sorted(all_chain_profits, key=lambda x: x.get('value_delta', 0), reverse=True)

    @classmethod
    def __get_pool_profit(cls, chain: Chain, pool: dict, pool_multipliers: dict, protocol: LrtProtocol):
        """Calculate amount of points and its estimated value in usd."""
        # take yt price
        yt_price = get_nested_value(pool, config.pendle.yt_price_location)
        # calculate possible amount of yt possible to buy for invested amount of usd
        yt_amount = config.pendle.amount_to_invest / yt_price
        pool_expiry_date = datetime.fromisoformat(pool["expiry"].replace('Z', ''))

        hours_before_expiry = int((pool_expiry_date - datetime.utcnow()).total_seconds() / 3600)

        # should be always skipped cause pool usually filters earlier
        if hours_before_expiry < 0:
            return {}

        predicted_protocol_points = (
            yt_amount
            * protocol.points_per_hour
            * hours_before_expiry
            * pool_multipliers.get(protocol.key, 0)
            * protocol.wallet_multiplier
        )
        predicted_el_points = (
            yt_amount
            * config.pendle.base_protocols.el_points_per_hour
            * hours_before_expiry
            * pool_multipliers.get("el", 0)
            * config.pendle.base_protocols.el_wallet_multiplier
        )
        predicted_zircuit_points = (
            yt_amount
            * config.pendle.base_protocols.zircuit_points_per_hour
            * hours_before_expiry
            * pool_multipliers.get("zircuit", 0)
            * config.pendle.base_protocols.zircuit_wallet_multiplier
        )

        predicted_protocol_points_price = (
            predicted_protocol_points
            * protocol.point_price
        )
        predicted_el_points_price = (
            predicted_el_points
            * config.pendle.base_protocols.el_price
        )
        predicted_zircuit_points_price = (
            predicted_zircuit_points
            * config.pendle.base_protocols.zircuit_price
        )

        all_points_price = (
            predicted_protocol_points_price
            + predicted_el_points_price
            + predicted_zircuit_points_price
        )
        value_delta = (
            all_points_price - config.pendle.amount_to_invest
        )
        percent_delta = (value_delta / config.pendle.amount_to_invest) * 100
        return {
            "chain_name": chain.name,
            "pool_name": f"{pool['proName']} - {pool['expiry']}",
            "protocol_points": predicted_protocol_points,
            "el_points": predicted_el_points,
            "zircuit_points": predicted_zircuit_points,
            "all_points_price": all_points_price,
            "value_delta": value_delta,
            "percent_delta": percent_delta,
        }

    @classmethod
    def __convert_multipliers(cls, multipliers: dict, addresses: list[str]):
        """Convert multiplier to inner format."""
        converted_multipliers = {address: {} for address in addresses}

        for key, multiplier in multipliers.get("results", []).items():
            for address in addresses:
                if address not in key:
                    continue

                converted_multipliers[address] = cls.__parse_multiplier(multiplier.get("points", []))

        return converted_multipliers

    @classmethod
    def __parse_multiplier(cls, points: list[dict]):
        parsed_multiplier = {}
        for point in points:
            if point.get("key", "").lower() == "ether.fi":
                parsed_multiplier["ether_fi"] = point["value"]
            elif point.get("key", "").lower() == "eigenlayer":
                parsed_multiplier["el"] = point["value"]
            elif point.get("key", "").lower() == "zircuit":
                parsed_multiplier["zircuit"] = point["value"]
            elif point.get("key", "").lower() == "kelp":
                parsed_multiplier["kelp"] = point["value"]
            elif point.get("key", "").lower() == "renzo":
                parsed_multiplier["renzo"] = point["value"]

        return parsed_multiplier

    @classmethod
    def __get_pool_multipliers(cls, chain_id: int, addresses: list[str]) -> dict:
        """Request pools multipliers."""
        try:
            keys = [f"InformationalMessages.lrtMetadata.chain{chain_id}.market{address}" for address in addresses]

            data = {"keys": keys}
            response = post("https://api-v2.pendle.finance/core/v2/metadata", json=data)
            response.raise_for_status()
            data = response.json()
            return data
        except Exception as e:
            print(f"An error occurred while getting pools multiplier with chain {chain_id}, addresses {addresses}")
            print(e)
            return {}


