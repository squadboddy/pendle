from typing import Optional

from requests import get
from datetime import datetime

from dune_client.query import QueryBase

from config.config import dune, config
from dynamic_points_price.tools import process_daily_points_data


def calculate_renzo_point_price() -> Optional[float]:
    """
    Calculation of renzo point price.

    Renzo provides the largest amount of necessary data, so its calculation is the clearest.

    Variables:
    **airdrop_tokens_amount** - number of tokens provided for airdrop.
     For example, for season 2, it's 500m (5% of 10b total suply. Information from tokenomics)
    **previous_season_points** - number of points earned in previous seasons.
     For example, for season 1 it's 1,68b. (700m tokens were distributed. Conversion rate was 2.4 points for 1 token.
      To get result we need to multiply 700m * 2.4).
    **season_date_end** - Date when the season ends.
    **custom_multiplier** - current script don't know about tvl changes in future, additional multipliers etc.
    For example, you know that tomorrow unlock will start and 10 percent of tvl will be withdrawn.
     You can set this parameter to 0.9 to calculate result better.
     Required to calculate total amount of points earned by the end of the season.
    **default_point_per_hour** - constant based on protocol rules


    Methodology.
    Formula: point_price = token_price * tokens_per_point
    * tokens_per_point = airdrop_tokens_amount / second_season_points
    * second_season_points = total_points_by_the_end_of_season - previous_season_points
    * total_points_by_the_end_of_season = current_point_amount + (
        eth_tvl * multiplier * custom_multiplier * hours_before_season_ends
    )

    - eth_tvl - amount of ETHs which earn points
    - multiplier - all protocols give different multiplier for points farming and have weight.
    - custom_multiplier (described in Variables section)

    To calculate it i use the following formula:
    multiplier = daily_points / 24 / tvl_eth
        where daily_points = (previous_week_points_earned - week_before_previous_points_earned) / 7
    """
    airdrop_tokens_amount = config.dynamic_points_price.renzo["airdrop_tokens_amount"]
    previous_season_points = config.dynamic_points_price.renzo["previous_season_points"]
    custom_multiplier = config.dynamic_points_price.renzo["custom_multiplier"]
    default_point_per_hour = config.dynamic_points_price.renzo["default_point_per_hour"]

    season_date_end = datetime.fromisoformat(config.dynamic_points_price.renzo["season_date_end"])

    hours_before_season_ends = int((season_date_end - datetime.utcnow()).total_seconds() / 3600)

    eth_tvl, current_total_point_amount = get_renzo_stats()
    token_price = get_rez_token_price()

    if not eth_tvl or not current_total_point_amount or not token_price:
        print("There was some problem with getting data form renzo dashboard. Price will be taken from configuration.")
        return None

    multiplier = get_renzo_farming_multiplier(eth_tvl)

    if not multiplier:
        print("There was some problem with getting data from renzo dune. Price will be taken from configuration.")
        return None

    total_points_by_the_end_of_season = current_total_point_amount + (
        eth_tvl * multiplier * custom_multiplier * hours_before_season_ends * default_point_per_hour
    )

    current_season_points = total_points_by_the_end_of_season - previous_season_points
    tokens_per_point = airdrop_tokens_amount / current_season_points
    point_price = token_price * tokens_per_point
    print("Renzo tvl in ETH", eth_tvl)
    print("Renzo average multiplier", multiplier)
    print("Renzo price", point_price)
    return point_price


def get_renzo_stats() -> (float, float):
    """Fetch data from official renzo dashboard."""
    try:
        response = get("https://app.renzoprotocol.com/api/stats")
        response.raise_for_status()
        data = response.json()
        return data["data"]["restakedTVL"]["data"]["eth"], data["data"]["totalRenzoPoints"]["data"]["points"]

    except Exception as e:
        print(f"An error occured while fetching renzo stats from official dashboard")
        print(e)


def get_renzo_farming_multiplier(eth_tvl: float) -> float:
    """
    Calculate average multiplier.

    Methodology:
    1. Fetch average daily points from previous week
    2. Divide them to tvl and amount of hours in 1 day
    """
    daily_points: float = get_renzo_daily_points()
    return daily_points / 24 / eth_tvl


def get_renzo_daily_points() -> float:
    """
    Returns amount of points that all users earned during 1 day.

    Data is taken from @maybeYonas dune analytics https://dune.com/queries/3350461/5615489
    """
    try:

        query = QueryBase(
            query_id=3350461,
        )

        query_result = dune.get_latest_result(query=query)

        points_farmed_initial_list = query_result.get_rows()
        return process_daily_points_data(points_farmed_initial_list, "total_renzo_points")

    except Exception as e:
        print(f"An error occurred while calculation daily points farm amount")
        print(e)
        return 0


def get_rez_token_price() -> Optional[float]:
    """Fetch current REZ price from coingecko."""
    try:
        response = get("https://coins.llama.fi/prices/current/coingecko:renzo,coingecko:eigenlayer")
        response.raise_for_status()
        data = response.json()
        return data["coins"]["coingecko:renzo"]["price"]

    except Exception as e:
        print(f"An error occurred while fetching rez token price from coingecko")
        print(e)
