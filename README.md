# btc-eth-correlation-backtest
This project explores the relationship between BTC and ETH using a small but reasonably structured Python research pipeline.
It is designed as a portfolio-quality code sample for trading / digital asset roles.

## Main ideas

- Download and clean BTC/ETH historical data from Yahoo Finance via `yfinance`
- Compute rolling correlations and basic market statistics
- Implement a simple event-driven backtest with:
  - Position sizing
  - Transaction costs
  - Multiple parameter sets (grid search)
- Compare strategy PnL against BTC, ETH and an equal-weight benchmark
- Generate performance statistics and plots for inspection

The code is intentionally compact but organised into separate modules:

- `data_loader.py` – data download and preprocessing
- `correlation_strategies.py` – signal and position generation
- `backtester.py` – generic vectorised backtest engine
- `metrics.py` – performance statistics
- `run_backtest.py` – command-line entry point

## Installation

```bash
git clone https://github.com/your-username/btc-eth-correlation-research.git
cd btc-eth-correlation-research
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Quick start

Run a default experiment from the command line:

```bash
python run_backtest.py --start 2020-01-01 --end 2024-12-31 \
    --windows 30 60 \
    --thresholds 0.6 0.7 0.8 \
    --cost_bps 5
```

This will:

- Download BTC-USD and ETH-USD data
- Run a grid of correlation-break strategies over the chosen windows and thresholds
- Save:
  - `data/btc_eth_prices.csv` – cleaned price data
  - `results/summary_stats.csv` – performance summary for each parameter set
  - `plots/equity_curves_<params>.png` – equity curves for selected runs
  - `plots/rolling_correlation.png` – rolling correlation chart

## Strategy description (high level)

The example strategy is deliberately simple and not meant for live trading.
It is meant to show how I think about structure, risk and research hygiene.

- Compute rolling Pearson correlation of BTC and ETH daily returns
- When correlation falls below a chosen threshold, treat it as a decorrelation regime
- In that regime, go long the recent underperformer and short the outperformer
- Close the trade when correlation recovers above the threshold
- Apply per-trade transaction costs in basis points on notional turnovers

Parameters explored:

- `window` – rolling correlation window length in days (e.g. 30, 60)
- `threshold` – correlation level that defines a decorrelated regime (e.g. 0.6, 0.7, 0.8)
- `cost_bps` – round-trip transaction cost assumption in basis points

## Example output (conceptual)

The script prints a small table to the console, for example:

```text
window threshold   ann_ret   ann_vol  sharpe  max_dd
30     0.60        24.3%     65.1%    0.37   -35.2%
30     0.70        18.9%     54.0%    0.35   -30.4%
60     0.60        12.1%     40.2%    0.30   -25.0%
...
```

The intention is to demonstrate:

- Clean, readable Python
- Sensible use of libraries (NumPy/Pandas/Matplotlib)
- Clear separation between data, signals, backtest engine and reporting

## Disclaimer

This project is purely educational, for interview purposes only, and is not financial advice.
