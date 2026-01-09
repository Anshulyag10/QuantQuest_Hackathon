# QuantQuest - Simulated Trading Platform

A fully self-contained Python-based trading simulation system demonstrating algorithmic trading, data handling, and performance tracking.

## Features

### 1. Market Data Generation
- Synthetic price data generator with realistic market behavior
- Random walk model with configurable drift and volatility
- Support for multiple assets
- Streaming and batch data feeding

### 2. Trading Engine
- Strategy execution engine with buy/sell order processing
- Multiple built-in strategies:
  - Moving Average Crossover
  - Momentum Trading
- Accurate trade execution in simulated environment
- Real-time order management

### 3. Portfolio & Risk Tracking
- **Unrealized P&L**: Profit/loss on open positions
- **Realized P&L**: Profit/loss from closed trades
- **Portfolio Exposure**: Per-asset and total exposure tracking
- Real-time position monitoring

## Installation

```bash
# Install required dependencies
pip install -r requirements.txt
```

## Quick Start

```bash
# Run the main trading simulation
python main.py
```

## Project Structure

```
QuantQuest/
├── src/
│   ├── market_data/        # Market data generation
│   ├── trading/            # Trading engine and strategies
│   ├── portfolio/          # Portfolio and risk management
│   └── utils/              # Utility functions
├── examples/               # Example scripts
├── tests/                  # Unit tests
├── main.py                 # Main application
├── requirements.txt        # Dependencies
└── README.md              # Documentation
```

## Usage Examples

### Basic Trading Simulation

```python
from src.market_data.data_generator import MarketDataGenerator
from src.trading.trading_engine import TradingEngine
from src.trading.strategies.moving_average import MovingAverageStrategy
from src.portfolio.portfolio_manager import PortfolioManager

# Initialize components
data_gen = MarketDataGenerator(symbols=['AAPL', 'GOOGL', 'MSFT'])
portfolio = PortfolioManager(initial_capital=100000)
strategy = MovingAverageStrategy(short_window=20, long_window=50)
engine = TradingEngine(portfolio, strategy)

# Generate market data
market_data = data_gen.generate_historical_data(days=252)

# Run simulation
engine.run(market_data)

# View results
portfolio.print_summary()
```

### Custom Strategy

```python
from src.trading.strategies.base_strategy import BaseStrategy

class CustomStrategy(BaseStrategy):
    def generate_signals(self, market_data):
        # Implement your trading logic
        signals = {}
        # ... your code here
        return signals
```

## Strategy Types

### Moving Average Crossover
- Generates buy signals when short MA crosses above long MA
- Generates sell signals when short MA crosses below long MA

### Momentum Strategy
- Buys assets with positive momentum
- Sells assets with negative momentum
- Configurable lookback period

## Performance Metrics

The platform tracks:
- Total Return
- Sharpe Ratio
- Maximum Drawdown
- Win Rate
- Average Profit per Trade
- Total Number of Trades

## Development

### Running Tests

```bash
python -m pytest tests/
```

### Adding New Strategies

1. Create a new file in `src/trading/strategies/`
2. Inherit from `BaseStrategy`
3. Implement `generate_signals()` method

## License

MIT License - Created for QuantQuest Hackathon

## Authors

Hackathon Submission - 2026
