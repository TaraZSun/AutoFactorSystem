"""常量配置文件"""
from __future__ import annotations
from pathlib import Path
# 回测时间范围
START_DATE: str = "2013-01-01"
END_DATE: str = "2023-12-31"

# 标的池（NASDAQ + 大票）
TICKERS: list[str] = [
    "AAPL", "MSFT", "AMZN", "GOOGL", "META",
    "TSLA", "NVDA", "JPM", "BAC", "WMT",
    "PG", "KO", "PEP", "IBM", "ORCL",
    "INTC", "CSCO", "NFLX", "T", "VZ",
    "DIS", "NKE", "MCD", "PFE", "JNJ",
    "MRK", "XOM", "CVX", "COP", "BA",
    "CAT", "HON", "GE", "HD", "LOW",
    "COST", "TGT", "PM", "MO", "ADBE",
    "CRM", "AVGO", "QCOM", "TXN", "AMD",
    "LLY", "UNH", "CVS", "WFC", "GS",
]

# 初始资金
INITIAL_CAPITAL: float = 100_000.0

# 一些策略默认参数也可以顺便放这儿
TOP_N: int = 10
LONG_N: int = 5
SHORT_N: int = 5
MIN_VALID_FACTORS: int = 2


# 动量因子 & 权重（默认配置）
MOMENTUM_FACTORS: list[str] = ["return_20day", "return_60day", "return_120day", "return_250day"]
MOMENTUM_WEIGHTS: dict[str, float] = {
    "return_20day": 0.4,
    "return_60day": 0.3,
    "return_120day": 0.2,
    "return_250day": 0.1,
}

# 文件路径
INPUT_FILE = Path("data/factors/stocks_with_factors.csv")
OUTPUT_DIR = Path("results/backtest")

RAW_DATA_DIR = Path("data/raw")
PROCESSED_DATA_DIR = Path("data/processed")