"""Models for trading strategy configurations and backtest results."""
from __future__ import annotations  
from pydantic import BaseModel, Field


class StrategyConfig(BaseModel):
    """Configuration model for a trading strategy."""
    strategy_name: str = Field(..., description="Name of the trading strategy")
    parameters: dict[str, float] = Field(..., description="Parameters for the trading strategy")

class BacktestMetrics(BaseModel):
    """Model to store backtest results."""
    total_return: float = Field(..., description="Total return of the strategy")
    annualized_return: float = Field(..., description="Annualized return of the strategy")
    annualized_volatility: float = Field(..., description="Annualized volatility of the strategy")
    sharpe_ratio: float = Field(..., description="Sharpe ratio of the strategy")
    max_drawdown: float = Field(..., description="Maximum drawdown of the strategy")
    win_rate: float = Field(..., description="Win rate of the strategy")
    n_days: int = Field(..., description="Number of trading days in the backtest")

class StrategyRunResult(BaseModel):
    """Model to encapsulate the results of a strategy run."""
    strategy_config: StrategyConfig = Field(..., description="Configuration of the trading strategy")
    backtest_result: BacktestMetrics = Field(..., description="Results of the backtest")
