# QuantQuest - Quick Start Guide

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Verify Installation

```bash
python -c "import numpy, pandas, matplotlib, tabulate; print('All dependencies installed!')"
```

## Running the Platform

### Option 1: Interactive Menu (Recommended)

```bash
python main.py
```

This will show you an interactive menu with options:
1. Run single strategy simulation
2. Compare multiple strategies
3. Moving Average Strategy
4. Momentum Strategy
5. Mean Reversion Strategy

### Option 2: Run Examples

#### Simple Example
```bash
python examples/simple_trading.py
```

#### Advanced Example (Multiple Assets, Custom Strategy)
```bash
python examples/advanced_trading.py
```

### Option 3: Run Tests

```bash
python tests/test_trading_engine.py
```

## Understanding the Output

### Portfolio Summary
The system displays:
- **Initial Capital**: Starting amount
- **Current Cash**: Available cash
- **Portfolio Value**: Market value of positions
- **Total Value**: Cash + Portfolio Value

### P&L Tracking
- **Realized P&L**: Profit/loss from closed trades
- **Unrealized P&L**: Profit/loss on open positions
- **Total P&L**: Realized + Unrealized

### Exposure Monitoring
- **Portfolio Exposure**: % of capital invested
- **Per-Asset Exposure**: % of portfolio per asset

### Performance Metrics
- **Total Return**: Overall return %
- **Sharpe Ratio**: Risk-adjusted return
- **Max Drawdown**: Largest peak-to-trough decline
- **Win Rate**: % of profitable trades

## Customization

### Create Your Own Strategy

```python
from src.trading.strategies.base_strategy import BaseStrategy

class MyStrategy(BaseStrategy):
    def __init__(self):
        super().__init__(lookback_period=20)
    
    def generate_signals(self, market_data):
        signals = {}
        # Your logic here
        # Return: {symbol: signal}
        # signal: 1 (buy), 0 (hold), -1 (sell)
        return signals
```

### Modify Configuration

Edit `main.py` to change:
- `INITIAL_CAPITAL`: Starting capital
- `SYMBOLS`: List of assets to trade
- `SIMULATION_DAYS`: Length of simulation
- Commission rates, strategy parameters, etc.

## Project Structure

```
QuantQuest/
├── src/
│   ├── market_data/     # Data generation
│   ├── trading/         # Trading engine & strategies
│   ├── portfolio/       # Portfolio management
│   └── utils/           # Utilities & metrics
├── examples/            # Example scripts
├── tests/               # Unit tests
├── main.py              # Main application
└── requirements.txt     # Dependencies
```

## Troubleshooting

### Import Errors
If you get import errors, ensure you're running from the project root:
```bash
cd QuantQuest
python main.py
```

### Missing Dependencies
```bash
pip install --upgrade -r requirements.txt
```

### Test Failures
Run tests to verify installation:
```bash
python tests/test_trading_engine.py
```

## Tips for Hackathon Presentation

1. **Start with Simple Example**: Show basic functionality first
2. **Demonstrate Strategy Comparison**: Run multiple strategies
3. **Highlight Key Features**:
   - Realistic market data generation
   - Multiple trading strategies
   - Real-time P&L tracking
   - Risk management
4. **Show Customization**: Create a simple custom strategy
5. **Discuss Architecture**: Clean, modular design

## Next Steps

- Experiment with different strategies
- Try different market conditions (volatility, drift)
- Add your own custom strategies
- Modify position sizing logic
- Add stop-loss/take-profit orders
- Implement backtesting validation

## Support

For questions or issues, refer to:
- README.md: Full documentation
- STRUCTURE.md: Project structure details
- Code comments: Detailed inline documentation

Good luck with your hackathon! 🚀
