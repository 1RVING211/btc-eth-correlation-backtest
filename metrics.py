import numpy as np
import pandas as pd


def annualised_return(rets: pd.Series, periods_per_year: int = 252) -> float:
    return float((1.0 + rets.mean()) ** periods_per_year - 1.0)


def annualised_vol(rets: pd.Series, periods_per_year: int = 252) -> float:
    return float(rets.std() * np.sqrt(periods_per_year))


def sharpe_ratio(rets: pd.Series, rf: float = 0.0, periods_per_year: int = 252) -> float:
    ar = annualised_return(rets, periods_per_year)
    av = annualised_vol(rets, periods_per_year)
    if av == 0:
        return float("nan")
    excess = ar - rf
    return float(excess / av)


def max_drawdown(equity: pd.Series) -> float:
    cum_max = equity.cummax()
    dd = equity / cum_max - 1.0
    return float(dd.min())


def summarise_performance(df: pd.DataFrame, label: str) -> dict:
    rets = df[label]
    equity = (1.0 + rets).cumprod()
    return {
        "ann_ret": annualised_return(rets),
        "ann_vol": annualised_vol(rets),
        "sharpe": sharpe_ratio(rets),
        "max_dd": max_drawdown(equity),
    }
