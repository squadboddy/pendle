from datetime import datetime


def process_daily_points_data(points_farmed_initial_list: list[dict], key: str) -> float:
    # Convert date strings to datetime objects and filter unique dates using a dictionary
    unique_dicts = {}
    for d in points_farmed_initial_list:
        # Parse the date string to datetime object
        date = datetime.fromisoformat(d['date'].replace(' UTC', ''))
        if date not in unique_dicts:
            unique_dicts[date] = d

    # Sort the dictionaries by date in descending order
    sorted_dicts = sorted(
        unique_dicts.values(), key=lambda x: datetime.fromisoformat(x['date'].replace(' UTC', '')),
        reverse=True
    )

    previous_week_points_earned = sorted_dicts[1][key] - sorted_dicts[2][key]
    return previous_week_points_earned / 7
