from dataclasses import dataclass

import pandas as pd


@dataclass
class BacktestParams:
    initial_capital: float = 100_000.0
    trading_cost_bps: float = 5.0


def apply_transaction_costs(
    positions: pd.DataFrame, prices: pd.DataFrame, cost_bps: float
) -> pd.Series:
    """Approximate transaction costs based on position changes and asset prices."""
    pos_change = positions.diff().fillna(0.0)
    notional_turnover = (pos_change.abs() * prices).sum(axis=1)
    daily_cost = notional_turnover * (cost_bps / 10_000.0)
    return daily_cost


def run_two_asset_long_short_backtest(
    rets: pd.DataFrame,
    prices: pd.DataFrame,
    positions: pd.DataFrame,
    params: BacktestParams,
) -> pd.DataFrame:
    """Vectorised backtest for a BTC/ETH long-short strategy."""
    strat_ret_gross = 0.5 * (
        positions["pos_btc"] * rets["BTC"] + positions["pos_eth"] * rets["ETH"]
    )

    daily_cost = apply_transaction_costs(
        positions[["pos_btc", "pos_eth"]],
        prices[["BTC", "ETH"]],
        params.trading_cost_bps,
    )
    capital = params.initial_capital
    cost_ret = daily_cost / capital

    strat_ret_net = strat_ret_gross - cost_ret

    out = pd.DataFrame(index=rets.index)
    out["strat_ret_net"] = strat_ret_net
    out["btc_ret"] = rets["BTC"]
    out["eth_ret"] = rets["ETH"]
    out["strat_equity"] = (1.0 + strat_ret_net).cumprod()
    out["btc_equity"] = (1.0 + out["btc_ret"]).cumprod()
    out["eth_equity"] = (1.0 + out["eth_ret"]).cumprod()
    out["positions_btc"] = positions["pos_btc"]
    out["positions_eth"] = positions["pos_eth"]
    return out
