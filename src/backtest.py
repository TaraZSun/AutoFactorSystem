from __future__ import annotations
import pandas as pd
import numpy as np
from pathlib import Path
import logging
import strategies
import models
from dotenv import load_dotenv
from typing import Callable
import os
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)
SigFuncType = Callable[[pd.DataFrame], pd.DataFrame]

load_dotenv()

INITIAL_CAPITAL = os.getenv('INITIAL_CAPITAL')


def calculate_strategy_returns(data:pd.DataFrame, initial_capital: float=float(INITIAL_CAPITAL))->pd.DataFrame:
    """Calculate strategy returns based on generated signals."""
    results =[]
    for ticker in data['ticker'].unique():
        ticker_data = data[data['ticker'] == ticker].copy()
        ticker_data = ticker_data.sort_values(by='date')
        # 持仓变化
        ticker_data["position"] = ticker_data["signal"].shift(1).fillna(0)

        # 计算策略收益=持仓变化*下一日收益
        ticker_data["strategy_return"] = ticker_data["position"] * ticker_data["return_1day"]

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

def generate_backtest_signals(data:pd.DataFrame, 
                            strategy: str, 
                            signal_func:SigFuncType,
                            save_data_path:Path=(Path("results/backtest/signals.csv")),
                            signal_kwargs:dict={},
                            )->models.StrategyRunResult:
    """Generate backtest signals using the specified strategy function and calculate performance metrics."""
    config = models.StrategyConfig(name=strategy, parameters=signal_kwargs)
    df = data.copy()
    df = signal_func(df, **signal_kwargs)
    df = calculate_strategy_returns(df)
    metrics_dict = calculate_performance_metrics(df)
    backtest_metrics = models.BacktestMetrics(**metrics_dict)
    run_result = models.StrategyRunResult(strategy_config=config, backtest_result=backtest_metrics)
    logger.info(f"Backtest Results for strategy {strategy}:\n{run_result.model_dump_json(indent=4)}")
    save_data_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(save_data_path, index=False)
    return models.StrategyRunResult(strategy_config=config, backtest_result=backtest_metrics)

def main()->None:
    INPUT_FILE = Path("data/factors/stocks_with_factors.csv")
    OUTPUT_DIR = Path("results/backtest")
    data = pd.read_csv(INPUT_FILE, parse_dates=['date'])
    strategy_map = [
        ("Momentum Strategy", strategies.momentum_strategy, {"factors": ["return_20day", "return_60day", "return_120day", "return_250day"], "top_n": 10}),
        ("Mean Reversion Strategy", strategies.mean_reversion_strategy, {"top_n": 10}),
        ("MA Crossover Strategy", strategies.ma_crossover_strategy, {}),
        ("Volume Breakout Strategy", strategies.volume_breakout_strategy, {}),
        ("RSI Strategy", strategies.rsi_strategy, {"lower_threshold": 30, "upper_threshold": 70}),
    ]
    for name, strategy_fun, kwargs in strategy_map:
        logger.info(f"Generating backtest signals for {name}...")
        save_path = OUTPUT_DIR / f"{name.replace(' ', '_').lower()}_signals.csv"
        generate_backtest_signals(data, strategy=name, signal_func=strategy_fun, save_data_path=save_path, signal_kwargs=kwargs)

if __name__ == "__main__":
    main()
