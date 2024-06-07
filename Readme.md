# Script Overview

This script has two main functionalities:
1. Scanning wallets for already earned points and calculating their USD equivalent.
2. Calculating profits for current Pendle pools.
3. Calculating points price base on chain analytics

## Setup

1. Install Python 3.8 or higher.
2. Create a virtual environment (optional).
3. Install required dependencies.
4. Run the script with `python main.py`.

## Configuration

Configuration adjustments should only be made in the `config.json` file. This script offers flexible configurations to cater to various needs.

### Wallet Scanner Configuration

1. **wallets_scan_enabled**: Set to `true` to activate the wallet scanning feature.
2. **wallets_scanner.protocols**: Only the `point_price` value should be changed. This value represents the estimated value of one point for each protocol. Other values are system-generated and should only be modified if the protocol changes its API.
3. **wallets_scanner.points_price**: Adjust the price for the EL and Zircuit protocols to reflect current values.
4. **wallets_scanner.wallets**: Configure any number of wallets.
   - `address`: Specify the wallet address in the standard format.
   - `previous_points`: Add points earned in previous seasons to prevent double counting. For example, if 1 million points were earned in the first season and the current amount is 100 million, subtract the 1 million to calculate the value for the 99 million earned in the current season.

### Pendle Profits Calculation Configuration

1. **pendle_profit_calculation_enabled**: Set to `true` to enable profit calculations for Pendle pools.
2. **pendle.chains**: Specifies the blockchain chains to be scanned. Default settings include Arbitrum and Main Ethereum chains. Additional chains can be added by finding their `id` on a site like `https://chainlist.org` and adding a `name` for easy identification.
3. **pendle.amount_to_invest**: Specify the USD amount to invest in Pendle YT.
4. **pendle.filter_negative_profit**: Filters out pools with negative profit by default.
5. **pendle.lrt**: Configure as needed. Each entry should include:
   - `ticker`: Filters pools as specified on the Pendle site.
   - `key`: Identifies the Pendle pool multiplier.
   - `point_price`: Predicted price per point for the protocol.
   - `analise_before_date`: Sets the expiration date for pool analysis.
   - `points_per_hour`: Base rate of point accumulation per ETH without multipliers.
   - `wallet_multiplier`: Specific bonuses for each wallet, if applicable.
6. **pendle.yt_price_location**: Location for parsing YT price data, do not change unless API updates occur.
7. **pendle.base_protocols**: Similar to the wallet scanner, configure for each protocol as needed.
   - Adjust prices, multipliers, and point rates according to protocol rules and updates.

### Dynamic points price calculation

## Prerequisites:
- To use this module you need to set your `dune_api_token` to config file.
- To register this token you need to sign up/ in to `https://dune.com`. 
- Then open profile setting (`https://dune.com/settings/api`) -> "create new api key"

## Configuration
1. **dynamic_points_price_enabled**: Set to `false` to disable points price calculation based on chain analytics. If module is turn on, got prices will overwrite config point prices. If you want to use just some of them. You can run this module, take the required prices, add them to other parts of config. Then disable module and run other functionalities again.
2. **dynamic_points_price.renzo**: 
- `airdrop_tokens_amount`: setup amount of tokens which will be distributed at the end of the season. By default, the amount for second season set.
- `previous_season_points`: setup amount of tokens which was distributed at the end of the previous season. By default, the amount by the start of second season set.
- `custom_multiplier`: you can set specific multiplier if you think that tvl will grow, additional multiplier will be added or something like this.
- `default_point_per_hour`: Base rate of point accumulation per ETH without multipliers.
- `season_date_end`: Sets the predicted end date of the season.
3. **dynamic_points_price.kelp**:
- `fdv`: Estimated value of protocol in TGE. It's just a prediction based on your own calculation and experience.
- `drop_distribution_percent`: Estimated drop percent from FDV. It's only just a prediction based on similar protocols TGE.
- `custom_multiplier`: you can set specific multiplier if you think that tvl will grow, additional multiplier will be added or something like this.
- `default_point_per_hour`: Base rate of point accumulation per ETH without multipliers.
- `season_date_end`: Sets the predicted end date of the season.
4. **dynamic_points_price.zircuit**:
- `fdv`: Estimated value of protocol in TGE. It's just a prediction based on your own calculation and experience.
- `drop_distribution_percent`: Estimated drop percent from FDV. It's only just a prediction based on similar protocols TGE.
- `custom_multiplier`: you can set specific multiplier if you think that tvl will grow, additional multiplier will be added or something like this.
- `default_point_per_hour`: Base rate of point accumulation per ETH without multipliers.
- `season_date_end`: Sets the predicted end date of the season.

## Methodology
- renzo: described in `dynamic_points_price/renzo.py` file
- kelp: described in `dynamic_points_price/kelp.py` file
- zircuit: described in `dynamic_points_price/zircuit.py` file
