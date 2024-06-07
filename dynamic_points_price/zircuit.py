from datetime import datetime
from typing import Optional

from dune_client.query import QueryBase
from requests import get

from config.config import dune, config


def calculate_zircuit_point_price() -> Optional[float]:
    """
    Calculation of zircuit point price.

    Variables:
    **fdv** - estimation of all protocol points price.
     It's possible just to guess this value based on your own expirience.
    **drop_distribution_percent** - also possible just to guess this value based on similar protocols distribution.
    **season_date_end** - Suggested date when the season ends.
    **custom_multiplier** - current script don't know about tvl changes in future, additional multipliers etc.
    For example, you know that tomorrow unlock will start and 10 percent of tvl will be withdrawn.
     You can set this parameter to 0.9 to calculate result better.
     Required to calculate total amount of points earned by the end of the season.
    **default_point_per_hour** - constant based on protocol rules

    Methodology.
    Formula: point_price = fdv * (drop_distribution_percent / 100) / total_points_by_the_end_of_season
    Where:
    - total_points_by_the_end_of_season = current_total_point_amount + future_points
    - future_points = tvl * multiplier * custom_multiplier * hours_before_season_ends * default_point_per_hour
    - multiplier = daily_points / tvl / 24 / default_point_per_hour
    """
    fdv = config.dynamic_points_price.zircuit["fdv"]
    drop_distribution_percent = config.dynamic_points_price.zircuit["drop_distribution_percent"]
    custom_multiplier = config.dynamic_points_price.zircuit["custom_multiplier"]
    default_point_per_hour = config.dynamic_points_price.zircuit["default_point_per_hour"]

    drop_value = fdv * (drop_distribution_percent / 100)

    season_date_end = datetime.fromisoformat(config.dynamic_points_price.zircuit["season_date_end"])

    hours_before_season_ends = int((season_date_end - datetime.utcnow()).total_seconds() / 3600)

    eth_tvl = get_zircuit_tvl()

    if not eth_tvl:
        print("There was some problem with getting data form zircuit dashboard. Price will be taken from configuration.")
        return None

    current_total_point_amount, multiplier = get_current_points_amount(eth_tvl, default_point_per_hour)

    if not current_total_point_amount or not multiplier:
        print("There was some problem with getting data form zircuit dune. Price will be taken from configuration.")
        return None

    total_points_by_the_end_of_season = current_total_point_amount + (
        eth_tvl * multiplier * custom_multiplier * hours_before_season_ends * default_point_per_hour
    )
    usd_per_point = drop_value / total_points_by_the_end_of_season

    print("Zircuit tvl in ETH", eth_tvl)
    print("Zircuit average multiplier", multiplier)
    print(f"{usd_per_point:.10f}")

    return usd_per_point


def get_zircuit_tvl() -> Optional[float]:
    """Fetch data from official zircuit dashboard."""
    try:
        tvl_response = get("https://stake.zircuit.com/api/stats")
        tvl_response.raise_for_status()
        tvl_data = tvl_response.json()
        usd_tvl = float(tvl_data["totalValueLocked"])
        eth_price_response = get("https://coins.llama.fi/prices/current/coingecko:ethereum")
        eth_price_response.raise_for_status()
        eth_price_data = eth_price_response.json()
        eth_price = eth_price_data["coins"]["coingecko:ethereum"]["price"]
        return usd_tvl / eth_price
    except Exception as e:
        print("An error occurred while getting zircuit tvl")
        print(e)


def get_current_points_amount(eth_tvl: float, default_point_per_hour: float) -> (Optional[float], Optional[float]):
    """
    Returns amount of points that all users earned during 1 day.

    Data is taken from dune analytics https://dune.com/queries/3667865
    """
    try:
        query = QueryBase(
            query_id=3667865
        )
        query_result = dune.get_latest_result(query=query)
        raws = query_result.get_rows()
        multiplier = raws[1]['daily_pts'] / 24 / eth_tvl / default_point_per_hour

        return raws[0]['cum_pts'], multiplier if multiplier >= 1 else 1
    except Exception as e:
        print("An error occurred while getting kelp dune analytics")
        print(e)
        return None, None
