from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class CorrelationBreakConfig:
    window: int
    threshold: float


def compute_returns(prices: pd.DataFrame) -> pd.DataFrame:
    rets = prices.pct_change().dropna()
    return rets


def rolling_correlation(rets: pd.DataFrame, window: int) -> pd.Series:
    return rets["BTC"].rolling(window).corr(rets["ETH"])


def generate_correlation_break_signals(
    rets: pd.DataFrame, corr: pd.Series, cfg: CorrelationBreakConfig
) -> pd.DataFrame:
    """Generate long/short signals based on correlation regimes."""
    aligned_corr = corr.reindex(rets.index).fillna(method="bfill").fillna(method="ffill")

    z_btc = (rets["BTC"] - rets["BTC"].mean()) / rets["BTC"].std()
    z_eth = (rets["ETH"] - rets["ETH"].mean()) / rets["ETH"].std()

    long_eth = (aligned_corr < cfg.threshold) & (z_eth < z_btc)
    long_btc = (aligned_corr < cfg.threshold) & (z_btc < z_eth)

    pos_btc = np.where(long_btc, 1.0, np.where(long_eth, -1.0, 0.0))
    pos_eth = np.where(long_eth, 1.0, np.where(long_btc, -1.0, 0.0))

    signals = pd.DataFrame(index=rets.index)
    signals["corr"] = aligned_corr
    signals["pos_btc"] = pos_btc
    signals["pos_eth"] = pos_eth
    return signals
