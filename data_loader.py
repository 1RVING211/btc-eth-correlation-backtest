import os
from typing import List

import pandas as pd
import yfinance as yf


def download_prices(tickers: List[str], start: str, end: str) -> pd.DataFrame:
    """Download adjusted close prices for the given tickers and date range."""
    data = yf.download(tickers, start=start, end=end)["Adj Close"]
    if isinstance(data, pd.Series):
        data = data.to_frame()
    data = data.dropna()
    data.columns = [t.split("-")[0] for t in data.columns]
    return data


def ensure_data(start: str, end: str, data_dir: str = "data") -> pd.DataFrame:
    """Download BTC/ETH data if not cached, then return as DataFrame."""
    os.makedirs(data_dir, exist_ok=True)
    path = os.path.join(data_dir, "btc_eth_prices.csv")
    if os.path.exists(path):
        prices = pd.read_csv(path, index_col=0, parse_dates=True)
    else:
        prices = download_prices(["BTC-USD", "ETH-USD"], start=start, end=end)
        prices.to_csv(path)
    return prices
