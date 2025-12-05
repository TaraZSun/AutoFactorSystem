# AutoFactorSystem

一个用 **7 天** 搭出来的迷你量化研究框架，用来做三件事：

1. **自动获取行情数据**
2. **自动生成 & 计算一批基础因子**
3. **一键跑多策略回测，对比表现，找「看起来靠谱」的策略**

目标不是做成一个完整的工业级框架，而是验证自己对「因子 → 策略 → 回测 → 评价」这条链路的理解和动手能力。

---

## 核心思路（一句话版）

> 从固定的一篮子股票开始  
> → 下载历史数据  
> → 生成常见价格/成交量因子  
> → 套一批简单却典型的策略（动量、均值回归等）  
> → 自动回测 & 打分  
> → 为之后“自动挖掘因子 / 自动选策略”打基础。

---

## 功能概览

- 🧾 **数据层**
  - 使用 `yfinance` 下载美股日线数据（当前使用约 50 只 NASDAQ / 大票）
  - 保存单标的原始 CSV（`data/raw/`）
  - 合并为一个 **面板数据表**（`date, ticker, open, high, low, close, adj_close, volume, ...`）

- 📐 **因子层**
  - 收益类因子：`return_1day / 5 / 10 / 20 / 60 / 120 / 250`
  - 均线类：`ma_x / ema_x`
  - 波动率：`volatility_xday`
  - 成交量相关：`volume_ma_x, volume_to_ma_x`
  - 动量/超买超卖：`rsi_x`
  - 输出：`data/factors/stocks_with_factors.csv`

- 📈 **策略层（目前内置几类）**
  - 横截面动量策略（支持多头 / 多空）
  - 短期均值回归策略（跌多反弹）
  - 均线交叉趋势策略（MA Crossover）
  - 成交量突破策略（Volume Breakout）
  - RSI 反转策略（RSI Reversion）

- 🔁 **回测 & 评价**
  - 根据 `signal` 计算逐日持仓 & 策略收益
  - 支持多标的组合回测
  - 输出指标：
    - 总收益、年化收益
    - 年化波动率
    - Sharpe Ratio
    - 最大回撤
    - 胜率等
  - 保存每个策略的完整回测路径 & 指标到 `results/`

---

## 目录结构（示意）

```text
AutoFactorSystem/
├─ src/
│  ├─ download_data.py      # 下载 & 合并行情数据
│  ├─ basic_factors.py      # 计算基础因子
│  ├─ strategies.py         # 各种策略（动量/均值回归/MA等）
│  ├─ backtest.py           # 回测引擎 + 绩效评价
│  ├─ models.py             # Pydantic 模型（StrategyConfig / BacktestMetrics 等）
│  ├─ constants.py          # 常量配置（起止时间 / TICKERS / 默认参数等）
│  └─ ...
├─ data/
│  ├─ raw/                  # 每只股票的原始 CSV
│  ├─ processed/            # 合并后的面板数据
│  └─ factors/              # 带因子的面板数据
├─ results/
│  └─ backtest/             # 各策略的回测结果 & 指标
├─ requirements.txt
└─ README.md

