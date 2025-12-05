"""Script to download historical stock data for specified tickers"""
import yfinance
import logging
from dotenv import load_dotenv
import os
import pandas as pd
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


load_dotenv()

# Configuration
START_DATE = os.getenv('START_DATE')
END_DATE = os.getenv('END_DATE')
TICKERS = os.getenv('TICKERS').split(',')
RAW_DATA_DIR = Path("data/raw")
PROCESSED_DATA_DIR = Path("data/processed")

def download_stock_data(ticker:str, start_date:str, end_date:str)->pd.DataFrame:
    """Download historical stock data for a given ticker and date range."""
   
    stock = yfinance.Ticker(ticker)
    data = stock.history(start=start_date, end=end_date, auto_adjust=False)
    if data.empty:
        logger.warning(f"No data found for ticker {ticker}")
        return None
    required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
    missing_cols = [col for col in required_columns if col not in data.columns]
    if missing_cols:
        logger.error(f"Missing columns {missing_cols} in data for {ticker}")
        return None
    null_pct=data[required_columns].isnull().sum()/len(data) * 100
    if (null_pct>0).any():
        logger.warning(f"Data for {ticker} contains null values:\n{null_pct}")
    return data


def save_to_csv(data:pd.DataFrame, ticker:str,output_dir:Path)->None:
    """Save the stock data to a CSV file."""
    output_dir.mkdir(parents=True,exist_ok=True)
    filename = output_dir / f"{ticker}.csv"
    data.to_csv(filename)
    logger.info(f"Saved data for {ticker} to {filename}")

def concat_dataframes(input_dir:Path, output_dir:Path)->pd.DataFrame:
    """Concatenate a list of DataFrames into a single DataFrame."""
    all_files = list(input_dir.glob("*.csv"))

    data_frames = []
    for file in all_files:
        df = pd.read_csv(file, parse_dates=['Date'], index_col='Date')
        df['ticker'] = file.stem
        if df.empty:
            logger.warning(f"No data in file {file}")
            continue
        data_frames.append(df)
    combined_df = pd.concat(data_frames).rename_axis('date')

    combined_df = combined_df.rename(columns={
        "Open": "open",
        "High": "high",
        "Low": "low",
        "Close": "close",
        "Adj Close": "adj_close", 
        "Volume": "volume",
        "Dividends": "dividends",
        "Stock Splits": "stock_splits",
    })
   
    combined_df = combined_df.reset_index().sort_values(["ticker", "date"])

    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "combined_stocks_data.csv"
    combined_df.to_csv(output_file, index=False)
    logger.info(f"Combined data saved to {output_file}")
    return combined_df

def main()->None:
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

    for ticker in TICKERS:
        try:
            data = download_stock_data(ticker, START_DATE, END_DATE)
            if data is None or data.empty:
                continue
            save_to_csv(data=data, ticker=ticker, output_dir=RAW_DATA_DIR)
        except Exception as e:
            logger.error(f"Error downloading data for {ticker}: {e}")
            continue

    concat_dataframes(input_dir=RAW_DATA_DIR, output_dir=PROCESSED_DATA_DIR)

if __name__ == "__main__":
    main()
