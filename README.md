# QuantQuest - Algorithmic Trading Simulation Platform

A comprehensive Python-based simulated trading platform demonstrating algorithmic trading concepts, real-time data handling, and portfolio risk tracking.

```
    ╔══════════════════════════════════════════════════════════════════════════════╗
    ║                                                                              ║
    ║     ██████╗ ██╗   ██╗ █████╗ ███╗   ██╗████████╗ ██████╗ ██╗   ██╗███████╗  ║
    ║    ██╔═══██╗██║   ██║██╔══██╗████╗  ██║╚══██╔══╝██╔═══██╗██║   ██║██╔════╝  ║
    ║    ██║   ██║██║   ██║███████║██╔██╗ ██║   ██║   ██║   ██║██║   ██║█████╗    ║
    ║    ██║▄▄ ██║██║   ██║██╔══██║██║╚██╗██║   ██║   ██║▄▄ ██║██║   ██║██╔══╝    ║
    ║    ╚██████╔╝╚██████╔╝██║  ██║██║ ╚████║   ██║   ╚██████╔╝╚██████╔╝███████╗  ║
    ║     ╚══▀▀═╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝    ╚══▀▀═╝  ╚═════╝ ╚══════╝  ║
    ║                                                                              ║
    ║                    ALGORITHMIC TRADING SIMULATION PLATFORM                   ║
    ║                                                                              ║
    ╚══════════════════════════════════════════════════════════════════════════════╝
```

## 🎯 Problem Statement

Build a Python-based simulated trading platform that demonstrates understanding of:
- **Algorithmic Trading** - Strategy implementation and execution
- **Data Handling** - Synthetic market data generation
- **Performance Tracking** - P&L and risk monitoring

## ✨ Features

### 1. Market Data Generation
- **Geometric Brownian Motion (GBM)** - Industry-standard random walk model
- **Jump Diffusion (Merton Model)** - Sudden price movements/gaps
- **Volatility Clustering (GARCH-like)** - Realistic volatility patterns
- **Correlated Asset Simulation** - Multi-asset portfolio modeling
- **Streaming Data** - Real-time tick-by-tick generation

### 2. Trading Engine
- **Multiple Trading Strategies**:
  - Moving Average Crossover (Golden Cross/Death Cross)
  - Momentum Trading
  - Mean Reversion
- **Order Execution** - Market and limit orders with commission
- **Position Sizing** - Configurable risk management
- **Trade Logging** - Complete audit trail

### 3. Portfolio & Risk Tracking
- **Unrealized P&L** - Real-time mark-to-market on open positions
- **Realized P&L** - Profit/loss from closed trades
- **Per-Asset Exposure** - Individual position weights
- **Total Portfolio Exposure** - Capital utilization metrics
- **Drawdown Tracking** - High water mark monitoring

## 📁 Project Structure

```
QuantQuest/
├── main.py                     # Main application entry point
├── requirements.txt            # Python dependencies
├── src/
│   ├── market_data/
│   │   └── data_generator.py   # GBM, Jump Diffusion, GARCH, Streaming
│   ├── trading/
│   │   ├── trading_engine.py   # Core execution engine
│   │   ├── order.py            # Order types and execution
│   │   └── strategies/
│   │       ├── base_strategy.py
│   │       ├── moving_average.py
│   │       └── momentum.py
│   ├── portfolio/
│   │   ├── portfolio_manager.py # P&L and exposure tracking
│   │   └── position.py         # Position management
│   └── utils/
│       └── metrics.py          # Performance metrics
├── examples/
│   ├── simple_trading.py       # Basic usage example
│   └── advanced_trading.py     # Advanced features demo
└── tests/
    └── test_trading_engine.py  # Unit tests
```

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/QuantQuest.git
cd QuantQuest

# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (Linux/Mac)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Platform

```bash
# Interactive menu
python main.py

# Direct strategy execution
python main.py ma              # Moving Average strategy
python main.py momentum        # Momentum strategy
python main.py mr              # Mean Reversion strategy
python main.py compare         # Compare all strategies
python main.py stream          # Streaming data demo
python main.py features        # View all features

# Run simple example
python examples/simple_trading.py
```

## 📊 Sample Output

```
======================================================================
                          TRADING SIMULATION
======================================================================

  Initial Capital:  $     100,000.00
  Strategy:         MovingAverageStrategy
  Position Size:                20%
  Commission:                 0.10%

======================================================================

  Day   50 │ Value: $  100,245.33 │ P&L: $   +245.33 (+0.25%) │ Exposure: 40.2% │ Positions: 2
           └─ BUY  45 AAPL @ $178.23
  Day  100 │ Value: $  101,892.18 │ P&L: $ +1,892.18 (+1.89%) │ Exposure: 60.1% │ Positions: 3
           └─ SELL 32 MSFT @ $412.56

================================================================================
                               PORTFOLIO SUMMARY
================================================================================

  ACCOUNT OVERVIEW
  --------------------------------------------------
    Initial Capital:        $     100,000.00
    Current Cash:           $      39,823.45
    Positions Value:        $      62,068.73
    Total Value:            $     101,892.18
    Total Return:                     +1.89%

  PROFIT & LOSS
  --------------------------------------------------
    Realized P&L:           $       +892.45
    Unrealized P&L:         $       +999.73
    Total P&L:              $     +1,892.18

  OPEN POSITIONS
  ----------------------------------------------------------------------------
  Symbol    Qty    Entry    Current      Value        P&L    Return    Exposure
  AAPL       45  $178.23    $182.45  $ 8,210.25  $ +189.90    +2.37%      8.1%
  GOOGL      28  $142.67    $148.23  $ 4,150.44  $ +155.68    +3.89%      4.1%
  ...

======================================================================
                         PERFORMANCE METRICS
======================================================================

  RETURNS
    Total Return:              +1.89%
    Total P&L:             $   +1,892.18

  RISK METRICS
    Sharpe Ratio:                1.24
    Sortino Ratio:               1.56
    Max Drawdown:               -0.85%

  TRADE STATISTICS
    Total Trades:                  18
    Win Rate:                   61.1%
    Profit Factor:               2.34
```

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=src
```

## 📈 Performance Metrics

The platform calculates comprehensive performance metrics:

| Metric | Description |
|--------|-------------|
| **Total Return** | Overall portfolio return percentage |
| **Sharpe Ratio** | Risk-adjusted return (annualized) |
| **Sortino Ratio** | Downside risk-adjusted return |
| **Calmar Ratio** | Return / Max Drawdown |
| **Max Drawdown** | Largest peak-to-trough decline |
| **Win Rate** | Percentage of profitable trades |
| **Profit Factor** | Gross profit / Gross loss |

## 🔧 Configuration

### Trading Engine Parameters

```python
engine = TradingEngine(
    portfolio=portfolio,
    strategy=strategy,
    commission=0.001,          # 0.1% per trade
    position_size_pct=0.2,     # 20% max per position
    max_positions=5            # Maximum concurrent positions
)
```

### Data Generator Parameters

```python
data_gen = MarketDataGenerator(
    symbols=['AAPL', 'GOOGL', 'MSFT'],
    drift=0.0002,              # Daily drift (annualized ~5%)
    volatility=0.02,           # Daily volatility (~32% annual)
    seed=42                    # Reproducibility
)

# Generate with advanced features
market_data = data_gen.generate_historical_data(
    days=252,                  # 1 year of trading
    include_jumps=True,        # Jump diffusion
    volatility_clustering=True # GARCH-like behavior
)
```

## 📚 Core Requirements Addressed

| Requirement | Implementation |
|-------------|----------------|
| Market Data Generation | GBM random walk with jump diffusion and GARCH volatility |
| Streaming/Batch Data | Both modes supported via `stream_prices()` and `generate_historical_data()` |
| Trading Engine | Strategy execution with order management and commission |
| Trade Execution | Accurate portfolio updates with position tracking |
| Unrealized P&L | Real-time calculation for open positions |
| Realized P&L | Tracked on position close |
| Portfolio Exposure | Per-asset and total exposure monitoring |

## 🛠️ Technologies

- **Python 3.10+**
- **NumPy** - Numerical computations
- **Pandas** - Data manipulation
- **Matplotlib** - Visualization
- **Tabulate** - Formatted output

## 📄 License

MIT License - see LICENSE file for details.

---

Built with ❤️ for algorithmic trading enthusiasts
