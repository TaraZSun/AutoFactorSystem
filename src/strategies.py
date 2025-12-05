"""stratgies"""
import pandas as pd
import numpy as np
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def momentum_strategy(data:pd.DataFrame, factors:list, top_n:int=10)->pd.DataFrame:
    """1️⃣ 横截面动量策略（Trend / Momentum）
    思想：过去一段时间涨得多的，未来还会继续强（趋势跟随）。
    用到的因子列：return_20day, return_60day, return_120day, return_250day
    简单规则示例（等权多头）：
    对每个交易日：按 return_60day 从大到小排序所有股票，选前 N（比如 10 或 20）只股票，signal = 1，
    其他股票 signal = 0，第二天按这个持仓计算组合收益"""
    data = data.copy()
    data['momentum_score'] = data[factors].mean(axis=1)
    
    def assign_momentum_signal(group):
        group = group.sort_values(by='momentum_score', ascending=False)
        n = min(top_n, len(group))
        group['signal'] = 0.0
        group.iloc[:n, group.columns.get_loc('signal')] = 1
        return group
    data = data.groupby("date", group_keys=False).apply(assign_momentum_signal)
    data["signal"] = data.groupby("ticker")["signal"].shift(1).fillna(0)
    return data

def mean_reversion_strategy(data:pd.DataFrame, top_n:int=10)->pd.DataFrame:
    """2️⃣ 横截面反转策略（短期均值回归）
    思想：短期跌多了会反弹，短期涨多了会回吐（mean reversion）。
    用到的因子列：return_5day, return_10day
    简单规则示例：
    每天按 return_5day 从小到大排序（跌得最多在前）
    选"跌得最多"的 N 只股票做多（期待反弹）"""
    data = data.copy()
    
    def assign_mean_reversion_signal(group):
        group = group.sort_values(by='return_5day', ascending=True)
        group['signal'] = 0.0
        n = min(top_n, len(group))
        group.iloc[:n, group.columns.get_loc('signal')] = 1
        return group

    data = data.groupby('date',group_keys=False
                        ).apply(assign_mean_reversion_signal)
    data["signal"] = data.groupby("ticker")["signal"].shift(1).fillna(0)
    return data

def ma_crossover_strategy(data:pd.DataFrame)->pd.DataFrame:
    """3️⃣ 双均线趋势策略（MA Crossover）
    思想：短期均线在长期均线之上 → 上升趋势；反之下跌趋势。
    用到因子：ma_5, ma_10, ma_20, ma_60, ...
    简单规则示例：
    ma_5 > ma_20 → 做多；否则空仓。"""
    data = data.copy()
    data["signal"] =  np.where(data["ma_5"] > data["ma_20"], 1, 0)
    data["signal"] = data.groupby("ticker")["signal"].shift(1).fillna(0)
    return data

def volume_breakout_strategy(data:pd.DataFrame)->pd.DataFrame:
    """4️⃣ 成交量 + 突破策略（Volume Breakout）
    思想：
    价格突破 + 放量 → 有效突破，更大概率继续走。
    用到的因子：
    价格 vs 均线：adj_close, ma_20
    成交量放大：volume_to_ma_20（当前成交量 / 20 日均量）
    简单规则示例：
    当天满足：
    adj_close > ma_20（价格在 20 日均线上方，趋势向上）
    volume_to_ma_20 > 1.5（今天放量至少 1.5 倍）
    则 signal = 1，否则 0"""
    data = data.copy()
    data["signal"] = np.where(
        (data["adj_close"] > data["ma_20"]) & (data["volume_to_ma_20"] > 1.5),
        1,
        0
    )
    data["signal"] = data.groupby("ticker")["signal"].shift(1).fillna(0)
    return data


def rsi_strategy(data:pd.DataFrame, 
                lower_threshold:float, 
                upper_threshold:float,
                rsi_col:str)->pd.DataFrame:
    """
    5️⃣ RSI 超买超卖反转策略（RSI Reversion）
    思想：RSI 很低 = 超卖；RSI 很高 = 超买，可能出现反转。
    用到因子：rsi_5, rsi_10, rsi_20…
    简单规则示例（做多超卖反弹）：
    RSI 低 → 1（做多）
    RSI 高 → -1（做空）
    中间 → 0"""
    data = data.copy()
    data["signal"] = np.where(
        data[rsi_col] < lower_threshold,1,
        np.where(data[rsi_col]>upper_threshold,-1,0)
    )
    data["signal"] = data.groupby("ticker")["signal"].shift(1).fillna(0)
    return data
