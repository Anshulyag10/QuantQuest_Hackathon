# QuantQuest Project Structure

This document describes the complete project structure.

## Directory Layout

```
QuantQuest/
│
├── src/                          # Source code
│   ├── __init__.py
│   │
│   ├── market_data/              # Market data generation
│   │   ├── __init__.py
│   │   └── data_generator.py     # Synthetic price data generator
│   │
│   ├── trading/                  # Trading engine
│   │   ├── __init__.py
│   │   ├── order.py              # Order types and execution
│   │   ├── trading_engine.py     # Core trading engine
│   │   │
│   │   └── strategies/           # Trading strategies
│   │       ├── __init__.py
│   │       ├── base_strategy.py  # Abstract base class
│   │       ├── moving_average.py # MA crossover strategy
│   │       └── momentum.py       # Momentum & mean reversion
│   │
│   ├── portfolio/                # Portfolio management
│   │   ├── __init__.py
│   │   ├── position.py           # Position tracking
│   │   └── portfolio_manager.py  # Portfolio & risk management
│   │
│   └── utils/                    # Utilities
│       ├── __init__.py
│       └── metrics.py            # Performance metrics
│
├── examples/                     # Example scripts
│   ├── __init__.py
│   ├── simple_trading.py         # Basic example
│   └── advanced_trading.py       # Advanced example
│
├── tests/                        # Unit tests
│   ├── __init__.py
│   └── test_trading_engine.py    # Test suite
│
├── main.py                       # Main application
├── requirements.txt              # Dependencies
└── README.md                     # Documentation
```

## Module Descriptions

### Market Data (`src/market_data/`)
- **data_generator.py**: Generates synthetic market data using Geometric Brownian Motion
  - `MarketDataGenerator`: Creates realistic price data
  - `MarketSimulator`: Streams data to trading engine

### Trading (`src/trading/`)
- **order.py**: Order management system
  - `Order`: Order representation
  - `OrderExecutor`: Executes orders against market
  
- **trading_engine.py**: Core trading logic
  - `TradingEngine`: Processes signals and executes trades
  
- **strategies/**: Trading strategies
  - `BaseStrategy`: Abstract base class
  - `MovingAverageStrategy`: MA crossover
  - `MomentumStrategy`: Momentum trading
  - `MeanReversionStrategy`: Mean reversion

### Portfolio (`src/portfolio/`)
- **position.py**: Position tracking
  - `Position`: Tracks individual positions
  
- **portfolio_manager.py**: Portfolio management
  - `PortfolioManager`: Manages portfolio, P&L, risk

### Utils (`src/utils/`)
- **metrics.py**: Performance metrics
  - Sharpe ratio, Sortino ratio
  - Maximum drawdown
  - Win rate, profit factor

## Key Features

1. **Market Data Generation**
   - Geometric Brownian Motion
   - Configurable drift and volatility
   - Market events simulation

2. **Trading Engine**
   - Strategy execution
   - Order management
   - Commission handling

3. **Portfolio Management**
   - Real-time P&L tracking
   - Position management
   - Exposure monitoring

4. **Strategies**
   - Moving Average Crossover
   - Momentum Trading
   - Mean Reversion
   - Extensible framework

## Usage

See README.md for usage instructions.
