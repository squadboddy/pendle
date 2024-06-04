# Script Overview

This script has two main functionalities:
1. Scanning wallets for already earned points and calculating their USD equivalent.
2. Calculating profits for current Pendle pools.

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

