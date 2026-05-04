import argparse
import os

import matplotlib.pyplot as plt
import pandas as pd

from data_loader import ensure_data
from correlation_strategies import (
    CorrelationBreakConfig,
    compute_returns,
    generate_correlation_break_signals,
    rolling_correlation,
)
from backtester import BacktestParams, run_two_asset_long_short_backtest
from metrics import summarise_performance


def run_single_experiment(
    start: str, end: str, window: int, threshold: float, cost_bps: float
) -> pd.DataFrame:
    prices = ensure_data(start=start, end=end)
    rets = compute_returns(prices)

    corr = rolling_correlation(rets, window=window)
    cfg = CorrelationBreakConfig(window=window, threshold=threshold)
    signals = generate_correlation_break_signals(rets, corr, cfg)

    params = BacktestParams(trading_cost_bps=cost_bps)
    results = run_two_asset_long_short_backtest(
        rets, prices.loc[rets.index], signals, params
    )
    results["corr"] = corr.reindex(results.index).fillna(method="bfill").fillna(method="ffill")
    return results


def plot_equity_curves(results: pd.DataFrame, window: int, threshold: float, out_dir: str) -> None:
    os.makedirs(out_dir, exist_ok=True)
    plt.figure(figsize=(10, 6))
    plt.plot(results.index, results["btc_equity"], label="BTC buy & hold")
    plt.plot(results.index, results["eth_equity"], label="ETH buy & hold")
    plt.plot(results.index, results["strat_equity"], label="Correlation strategy")
    plt.legend()
    plt.title(f"BTC/ETH Strategy vs Buy & Hold (window={window}, threshold={threshold})")
    plt.xlabel("Date")
    plt.ylabel("Cumulative equity (normalised)")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    fname = os.path.join(out_dir, f"equity_curves_w{window}_t{threshold}.png")
    plt.savefig(fname)
    plt.close()


def plot_rolling_correlation(results: pd.DataFrame, window: int, threshold: float, out_dir: str) -> None:
    os.makedirs(out_dir, exist_ok=True)
    plt.figure(figsize=(10, 4))
    plt.plot(results.index, results["corr"], label=f"Rolling corr ({window} days)")
    plt.axhline(threshold, color="red", linestyle="--", label="Threshold")
    plt.legend()
    plt.title("BTC/ETH Rolling Correlation")
    plt.xlabel("Date")
    plt.ylabel("Correlation")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    fname = os.path.join(out_dir, f"rolling_corr_w{window}_t{threshold}.png")
    plt.savefig(fname)
    plt.close()


def main():
    parser = argparse.ArgumentParser(description="BTC/ETH Correlation Research Backtest")
    parser.add_argument("--start", type=str, required=True, help="Start date YYYY-MM-DD")
    parser.add_argument("--end", type=str, required=True, help="End date YYYY-MM-DD")
    parser.add_argument("--windows", type=int, nargs="+", default=[30, 60], help="Rolling correlation windows")
    parser.add_argument(
        "--thresholds",
        type=float,
        nargs="+",
        default=[0.6, 0.7, 0.8],
        help="Correlation thresholds",
    )
    parser.add_argument("--cost_bps", type=float, default=5.0, help="Round-trip transaction cost in bps")

    args = parser.parse_args()

    rows = []
    for window in args.windows:
        for thr in args.thresholds:
            print(f"Running window={window}, threshold={thr}...")
            results = run_single_experiment(args.start, args.end, window, thr, args.cost_bps)

            strat_stats = summarise_performance(results[["strat_ret_net"]], "strat_ret_net")
            btc_stats = summarise_performance(results[["btc_ret"]], "btc_ret")
            eth_stats = summarise_performance(results[["eth_ret"]], "eth_ret")

            rows.append({
                "window": window,
                "threshold": thr,
                "label": "strategy",
                **strat_stats,
            })
            rows.append({
                "window": window,
                "threshold": thr,
                "label": "BTC",
                **btc_stats,
            })
            rows.append({
                "window": window,
                "threshold": thr,
                "label": "ETH",
                **eth_stats,
            })

            plot_equity_curves(results, window, thr, out_dir="plots")
            plot_rolling_correlation(results, window, thr, out_dir="plots")

    summary = pd.DataFrame(rows)
    os.makedirs("results", exist_ok=True)
    summary.to_csv("results/summary_stats.csv", index=False)
    print("\nSummary stats (first few rows):")
    print(summary.head())


if __name__ == "__main__":
    main()
