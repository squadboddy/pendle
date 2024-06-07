from datetime import datetime
from typing import Optional

from dune_client.query import QueryBase
from requests import get

from config.config import dune, config
from dynamic_points_price.tools import process_daily_points_data


def calculate_kelp_point_price() -> Optional[float]:
    """Calculation of kelp point price."""

    fdv = config.dynamic_points_price.kelp["fdv"]
    drop_distribution_percent = config.dynamic_points_price.kelp["drop_distribution_percent"]
    custom_multiplier = config.dynamic_points_price.kelp["custom_multiplier"]
    default_point_per_hour = config.dynamic_points_price.kelp["default_point_per_hour"]

    drop_value = fdv * (drop_distribution_percent / 100)

    season_date_end = datetime.fromisoformat(config.dynamic_points_price.kelp["season_date_end"])

    hours_before_season_ends = int((season_date_end - datetime.utcnow()).total_seconds() / 3600)

    eth_tvl = get_kelp_tvl()

    if not eth_tvl:
        print("There was some problem with getting data form kelp dashboard. Price will be taken from configuration.")
        return None

    current_total_point_amount, multiplier = get_current_miles_amount(eth_tvl, default_point_per_hour)

    if not current_total_point_amount or not multiplier:
        print("There was some problem with getting data form kelp dune. Price will be taken from configuration.")
        return None

    total_points_by_the_end_of_season = current_total_point_amount + (
        eth_tvl * multiplier * custom_multiplier * hours_before_season_ends * default_point_per_hour
    )
    usd_per_point = drop_value / total_points_by_the_end_of_season
    print("Kelp tvl in ETH", eth_tvl)
    print("Kelp average multiplier", multiplier)
    print(f"{usd_per_point:.10f}")
    return usd_per_point


def get_kelp_tvl() -> float:
    """Fetch data from official kelp dashboard."""
    try:
        response = get("https://universe.kelpdao.xyz/rseth/tvl/?lrtToken")
        response.raise_for_status()
        data = response.json()
        return data["value"]
    except Exception as e:
        print("An error occurred while getting kelp tvl")
        print(e)


def get_current_miles_amount(eth_tvl: float, default_point_per_hour: float) -> (Optional[float], Optional[float]):
    """
    Returns amount of points that all users earned during 1 day.

    Data is taken from @maybeYonas dune analytics https://dune.com/queries/3351009/5616608
    """
    try:
        query = QueryBase(
            query_id=3351009,
        )

        query_result = dune.get_latest_result(query=query)
        raws = query_result.get_rows()

        daily_points: float = process_daily_points_data(raws, "total_kelp_miles")

        multiplier = daily_points / 24 / eth_tvl / default_point_per_hour

        return raws[0]["total_kelp_miles"], multiplier
    except Exception as e:
        print("An error occurred while getting kelp dune analytics")
        print(e)
        return None, None


