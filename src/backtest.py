import pandas as pd
import numpy as np
from pathlib import Path
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def generate_backtest_signals(data:pd.DataFrame)->pd.DataFrame:
    """Generate simple backtest signals based on moving averages. 简单策略，MA交叉，生成买卖信号， 当价格>MA20时买入，反之卖出"""
    data = data.copy()
    data["signal"] =  np.where(data["adj_close"] > data["ma_20"], 1, 0)
    return data

def calculate_strategy_returns(data:pd.DataFrame, initial_capital: float=10000)->pd.DataFrame:
    """Calculate strategy returns based on generated signals."""
    results =[]
    for ticker in data['ticker'].unique():
        ticker_data = data[data['ticker'] == ticker].copy()
        # 持仓变化
        ticker_data["position_change"] = ticker_data["signal"].shift(1).fillna(0)

        # 计算策略收益=持仓变化*下一日收益
        ticker_data["strategy_return"] = ticker_data["position_change"] * ticker_data["return_1day"]

        # 计算累计收益
        ticker_data["cumulative_strategy_return"] = (1 + ticker_data["strategy_return"].fillna(0)).cumprod()
        ticker_data["equity_curve"] = initial_capital * ticker_data["cumulative_strategy_return"]

        results.append(ticker_data)
    results_df = pd.concat(results,ignore_index=True)
    return results_df

def calculate_performance_metrics(data:pd.DataFrame)->dict:
    """Calculate performance metrics for the backtest."""
    daily_returns = data.groupby('date')['strategy_return'].mean().sort_index().dropna()
    total_return  = (1+daily_returns).prod() -1
    # Annualized Return (Assuming 252 trading days)
    n_days = daily_returns.shape[0]
    annualized_return = (1 + total_return) ** (252 / n_days) - 1
    # Annualized Volatility
    annualized_volatility = daily_returns.std() * np.sqrt(252)
    # Sharpe Ratio (Assuming risk-free rate is 0)
    sharpe_ratio = annualized_return / annualized_volatility if annualized_volatility !=0 else np.nan
    # Max Drawdown
    equity_curve = (1 + daily_returns).cumprod()
    running_max = equity_curve.cummax()
    drawdown = (equity_curve - running_max) / running_max
    max_drawdown = drawdown.min()
    # Win Rate
    win_rate = (daily_returns > 0).sum() / len(daily_returns)
    return {
        "total_return": total_return,
        "annualized_return": annualized_return,
        "annualized_volatility": annualized_volatility,
        "sharpe_ratio": sharpe_ratio,
        "max_drawdown": max_drawdown,
        "win_rate": win_rate,
        "n_days": n_days
    }

def run_backtest(input_file:Path, strategy_fun=generate_backtest_signals)->dict[pd.DataFrame, dict[str, float]]:
    data = pd.read_csv(input_file, parse_dates=['date'])


    logger.info("Generateing backtest signals")
    data = strategy_fun(data)

    logger.info("Calculating strategy returns")
    data = calculate_strategy_returns(data)

    logger.info("Calculating performance metrics")
    metrics = calculate_performance_metrics(data)

    return {"data": data, "metrics": metrics}

def main()->None:
    PROCESSED_DATA_DIR = Path("data/factors")
    BACKTEST_RESULTS_DIR = Path("results/backtest")
    BACKTEST_RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    input_file = PROCESSED_DATA_DIR / "stocks_with_factors.csv"
    results = run_backtest(input_file)

    output_data_file = BACKTEST_RESULTS_DIR / "backtest_results.csv"
    results["data"].to_csv(output_data_file, index=False)
    logger.info(f"Backtest results saved to {output_data_file}")

    metrics_file = BACKTEST_RESULTS_DIR / "backtest_metrics.txt"
    with open(metrics_file, "w") as f:
        for key, value in results["metrics"].items():
            f.write(f"{key}: {value}\n")

if __name__ == "__main__":
    main()
