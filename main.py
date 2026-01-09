"""
QuantQuest Trading Platform - Main Application

Demonstrates the complete trading simulation system.
"""

import sys
from datetime import datetime

from src.market_data.data_generator import MarketDataGenerator
from src.trading.trading_engine import TradingEngine
from src.trading.strategies.moving_average import MovingAverageStrategy
from src.trading.strategies.momentum import MomentumStrategy, MeanReversionStrategy
from src.portfolio.portfolio_manager import PortfolioManager


def print_header():
    """Print application header."""
    print("\n" + "="*80)
    print(" " * 20 + "QUANTQUEST TRADING PLATFORM")
    print(" " * 15 + "Simulated Algorithmic Trading System")
    print("="*80 + "\n")


def run_simulation(strategy_name: str = "moving_average"):
    """
    Run a complete trading simulation.
    
    Args:
        strategy_name: Name of strategy to use
            - 'moving_average': Moving Average Crossover
            - 'momentum': Momentum Trading
            - 'mean_reversion': Mean Reversion
    """
    print_header()
    
    # Configuration
    INITIAL_CAPITAL = 100000
    SYMBOLS = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA']
    SIMULATION_DAYS = 252  # 1 year of trading
    
    print("CONFIGURATION:")
    print(f"  Initial Capital: ${INITIAL_CAPITAL:,.2f}")
    print(f"  Assets: {', '.join(SYMBOLS)}")
    print(f"  Simulation Period: {SIMULATION_DAYS} trading days (~1 year)")
    print(f"  Strategy: {strategy_name.replace('_', ' ').title()}")
    print("\n" + "-"*80 + "\n")
    
    # Step 1: Generate Market Data
    print("Step 1: Generating synthetic market data...")
    data_generator = MarketDataGenerator(
        symbols=SYMBOLS,
        drift=0.0002,  # Slight upward drift
        volatility=0.02,  # 2% daily volatility
        seed=42  # For reproducibility
    )
    
    market_data = data_generator.generate_historical_data(days=SIMULATION_DAYS)
    print(f"✓ Generated {len(market_data)} data points")
    print(f"  Date Range: {market_data['timestamp'].min()} to {market_data['timestamp'].max()}")
    
    # Step 2: Initialize Portfolio
    print("\nStep 2: Initializing portfolio...")
    portfolio = PortfolioManager(initial_capital=INITIAL_CAPITAL)
    print(f"✓ Portfolio initialized with ${INITIAL_CAPITAL:,.2f}")
    
    # Step 3: Select and Initialize Strategy
    print(f"\nStep 3: Initializing {strategy_name.replace('_', ' ').title()} strategy...")
    
    if strategy_name == "moving_average":
        strategy = MovingAverageStrategy(short_window=20, long_window=50)
        print("✓ Moving Average Strategy (20/50 periods)")
    elif strategy_name == "momentum":
        strategy = MomentumStrategy(lookback_period=20, threshold=0.02)
        print("✓ Momentum Strategy (20-period lookback, 2% threshold)")
    elif strategy_name == "mean_reversion":
        strategy = MeanReversionStrategy(lookback_period=20, std_threshold=2.0)
        print("✓ Mean Reversion Strategy (20-period, 2σ threshold)")
    else:
        print(f"Unknown strategy: {strategy_name}")
        return
    
    # Step 4: Initialize Trading Engine
    print("\nStep 4: Initializing trading engine...")
    engine = TradingEngine(
        portfolio=portfolio,
        strategy=strategy,
        commission=0.001  # 0.1% commission
    )
    print("✓ Trading engine ready")
    
    # Step 5: Run Simulation
    print("\nStep 5: Running simulation...")
    print("-"*80)
    
    metrics = engine.run(market_data, verbose=True)
    
    # Step 6: Display Results
    print("\nStep 6: Final Results")
    print("-"*80)
    
    # Get trade history
    trade_history = engine.get_trade_history()
    if not trade_history.empty:
        print(f"\nTrade History (Last 10 trades):")
        print(trade_history.tail(10).to_string(index=False))
    
    print("\n" + "="*80)
    print("SIMULATION COMPLETE")
    print("="*80 + "\n")


def run_strategy_comparison():
    """Run and compare multiple strategies."""
    print_header()
    print("STRATEGY COMPARISON MODE\n")
    print("Running simulations with different strategies...\n")
    
    strategies = [
        ("moving_average", MovingAverageStrategy(short_window=20, long_window=50)),
        ("momentum", MomentumStrategy(lookback_period=20, threshold=0.02)),
        ("mean_reversion", MeanReversionStrategy(lookback_period=20, std_threshold=2.0))
    ]
    
    INITIAL_CAPITAL = 100000
    SYMBOLS = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA']
    SIMULATION_DAYS = 252
    
    # Generate market data (same for all strategies)
    print("Generating market data...")
    data_generator = MarketDataGenerator(
        symbols=SYMBOLS,
        drift=0.0002,
        volatility=0.02,
        seed=42
    )
    market_data = data_generator.generate_historical_data(days=SIMULATION_DAYS)
    print(f"✓ Generated {len(market_data)} data points\n")
    
    results = []
    
    for strategy_name, strategy in strategies:
        print(f"\n{'='*80}")
        print(f"Testing: {strategy_name.replace('_', ' ').title()}")
        print(f"{'='*80}\n")
        
        # Create fresh portfolio for each strategy
        portfolio = PortfolioManager(initial_capital=INITIAL_CAPITAL)
        
        # Create trading engine
        engine = TradingEngine(
            portfolio=portfolio,
            strategy=strategy,
            commission=0.001
        )
        
        # Run simulation
        metrics = engine.run(market_data, verbose=False)
        
        # Store results
        results.append({
            'strategy': strategy_name.replace('_', ' ').title(),
            'final_value': metrics['final_value'],
            'total_return': metrics['total_return'],
            'sharpe_ratio': metrics['sharpe_ratio'],
            'max_drawdown': metrics['max_drawdown'],
            'num_trades': metrics['num_trades']
        })
        
        print(f"\n{strategy_name.replace('_', ' ').title()} Results:")
        print(f"  Final Value: ${metrics['final_value']:,.2f}")
        print(f"  Total Return: {metrics['total_return']*100:.2f}%")
        print(f"  Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
        print(f"  Max Drawdown: {metrics['max_drawdown']*100:.2f}%")
        print(f"  Number of Trades: {metrics['num_trades']}")
    
    # Print comparison
    print(f"\n\n{'='*80}")
    print("STRATEGY COMPARISON SUMMARY")
    print(f"{'='*80}\n")
    
    # Sort by total return
    results.sort(key=lambda x: x['total_return'], reverse=True)
    
    print(f"{'Strategy':<20} {'Final Value':<15} {'Return':<12} {'Sharpe':<10} {'Drawdown':<12} {'Trades':<10}")
    print("-"*80)
    
    for result in results:
        print(
            f"{result['strategy']:<20} "
            f"${result['final_value']:>13,.2f} "
            f"{result['total_return']*100:>10.2f}% "
            f"{result['sharpe_ratio']:>8.2f} "
            f"{result['max_drawdown']*100:>10.2f}% "
            f"{result['num_trades']:>8}"
        )
    
    print("\n" + "="*80 + "\n")


def main():
    """Main entry point."""
    print("\nQuantQuest Trading Platform")
    print("Choose simulation mode:\n")
    print("1. Run single strategy simulation")
    print("2. Compare multiple strategies")
    print("3. Moving Average Strategy")
    print("4. Momentum Strategy")
    print("5. Mean Reversion Strategy")
    print("0. Exit\n")
    
    choice = input("Enter your choice (0-5): ").strip()
    
    if choice == "1":
        print("\nAvailable strategies:")
        print("  1. moving_average")
        print("  2. momentum")
        print("  3. mean_reversion")
        strategy = input("\nEnter strategy name: ").strip()
        run_simulation(strategy)
    
    elif choice == "2":
        run_strategy_comparison()
    
    elif choice == "3":
        run_simulation("moving_average")
    
    elif choice == "4":
        run_simulation("momentum")
    
    elif choice == "5":
        run_simulation("mean_reversion")
    
    elif choice == "0":
        print("Exiting...")
        sys.exit(0)
    
    else:
        print("Invalid choice. Running default (Moving Average)...")
        run_simulation("moving_average")


if __name__ == "__main__":
    main()
