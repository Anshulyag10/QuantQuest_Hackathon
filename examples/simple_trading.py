"""
Simple Trading Simulation Example

Basic example showing how to use the QuantQuest platform.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.market_data.data_generator import MarketDataGenerator
from src.trading.trading_engine import TradingEngine
from src.trading.strategies.moving_average import MovingAverageStrategy
from src.portfolio.portfolio_manager import PortfolioManager


def main():
    """Run a simple trading simulation."""
    
    print("\n" + "="*60)
    print("Simple Trading Simulation Example")
    print("="*60 + "\n")
    
    # 1. Generate market data
    print("Generating market data...")
    data_gen = MarketDataGenerator(
        symbols=['AAPL', 'GOOGL', 'MSFT'],
        seed=42
    )
    market_data = data_gen.generate_historical_data(days=100)
    print(f"Generated {len(market_data)} data points\n")
    
    # 2. Create portfolio
    print("Creating portfolio...")
    portfolio = PortfolioManager(initial_capital=50000)
    print(f"Initial capital: ${portfolio.initial_capital:,.2f}\n")
    
    # 3. Create strategy
    print("Setting up Moving Average strategy...")
    strategy = MovingAverageStrategy(short_window=10, long_window=30)
    print(f"Strategy: {strategy}\n")
    
    # 4. Create trading engine
    print("Initializing trading engine...")
    engine = TradingEngine(portfolio, strategy)
    print("Ready to trade!\n")
    
    # 5. Run simulation
    print("Running simulation...")
    print("-"*60)
    metrics = engine.run(market_data, verbose=True)
    
    print("\n" + "="*60)
    print("Simulation Complete!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
