import pandas as pd
import numpy as np
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def calculate_basic_factors(data:pd.DataFrame)->pd.DataFrame:
    """Calculate basic financial factors for stock data."""
    # daily return 
    data["return_1day"] = data.groupby('ticker')['adj_close'].pct_change()
    
    # muilti-period returns
    for period in [5, 10, 20, 60, 120, 250]:
        data[f"return_{period}day"] = data.groupby('ticker')['adj_close'].pct_change(periods=period)

    return data

def calculate_moving_averages(data:pd.DataFrame)->pd.DataFrame:
    """Calculate moving averages for stock data."""
    for window in [5, 10, 20, 60, 120, 250]:
        # Simple Moving Average
        data[f"ma_{window}"] = data.groupby('ticker')['adj_close'].transform(lambda x: x.rolling(window=window, min_periods=1).mean())

        # Exponential Moving Average
        data[f"ema_{window}"] = data.groupby('ticker')['adj_close'].transform(lambda x: x.ewm(span=window, adjust=False).mean())
    return data

def calculate_volatility(data:pd.DataFrame)->pd.DataFrame:
    """Calculate volatility measures for stock data."""
    for window in [5, 10, 20, 60, 120, 250]:
        # Rolling Standard Deviation of Returns
        data[f"volatility_{window}day"] = data.groupby('ticker')['return_1day'].transform(lambda x: x.rolling(window=window, min_periods=1).std())
    return data

def calculate_volume_factors(data:pd.DataFrame)->pd.DataFrame:
    """Calculate volume-based factors for stock data."""
    for window in [5, 10, 20, 60, 120, 250]:
        # Moving Average of Volume
        data[f"volume_ma_{window}"] = data.groupby('ticker')['volume'].transform(lambda x: x.rolling(window=window, min_periods=1).mean())

        # Volume to Moving Average Ratio
        data[f"volume_to_ma_{window}"] = data['volume'] / data[f"volume_ma_{window}"]
    return data

def calculate_momentum_factors(data:pd.DataFrame)->pd.DataFrame:
    """Calculate momentum indicators for stock data."""
    for period in [5, 10, 20, 60, 120, 250]:
        delta = data.groupby('ticker')['adj_close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = data.groupby('ticker').apply(
            lambda x: gain[x.index].rolling(window=period, min_periods=1).mean()
        ).reset_index(level=0, drop=True)
        avg_loss = data.groupby('ticker').apply(
            lambda x:loss[x.index].rolling(window=period, min_periods=1).mean()
        ).reset_index(level=0, drop=True)
        rs = avg_gain / avg_loss
        data[f"rsi_{period}"] = 100 - (100 / (1 + rs))
    return data

def calculate_all_factors(input_file:Path, output_file:Path)->pd.DataFrame:
    """Calculate all basic financial factors for stock data."""
    data = pd.read_csv(input_file, parse_dates=['date'])
    data = calculate_basic_factors(data)
    data = calculate_moving_averages(data)
    data = calculate_volatility(data)
    data = calculate_volume_factors(data)
    data = calculate_momentum_factors(data)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    data.to_csv(output_file, index=False)
    return data

def main()->None: 
    INPUT_DIR = Path("data/processed")
    OUTPUT_DIR = Path("data/factors")
    INPUT_FILE = INPUT_DIR / "combined_stocks_data.csv" # combined_stocks_data.csv exists from download_data.py
    OUTPUT_FILE = OUTPUT_DIR / "stocks_with_factors.csv" # stocks_with_factors.csv will be created
    calculate_all_factors(INPUT_FILE, OUTPUT_FILE)

if __name__ == "__main__":
    main()