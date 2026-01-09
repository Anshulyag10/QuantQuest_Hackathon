"""
QuantQuest Trading Platform - Main Application

A comprehensive simulated trading platform demonstrating:
1. Synthetic market data generation (Random Walk, Jump Diffusion, GARCH)
2. Strategy execution engine with multiple trading strategies
3. Real-time P&L tracking (Realized + Unrealized)
4. Portfolio exposure monitoring
"""

import sys
from datetime import datetime

from src.market_data.data_generator import MarketDataGenerator
from src.trading.trading_engine import TradingEngine
from src.trading.strategies.moving_average import MovingAverageStrategy
from src.trading.strategies.momentum import MomentumStrategy, MeanReversionStrategy
from src.portfolio.portfolio_manager import PortfolioManager


def print_banner():
    """Print application banner."""
    banner = """
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
    """
    print(banner)


def print_section(title: str, width: int = 80):
    """Print a section header."""
    print(f"\n{'═'*width}")
    print(f"{title:^{width}}")
    print(f"{'═'*width}\n")


def run_simulation(strategy_name: str = "moving_average", verbose: bool = True):
    """
    Run a complete trading simulation.
    
    Args:
        strategy_name: Name of strategy to use
        verbose: Print detailed output
    """
    print_banner()
    
    # Configuration
    INITIAL_CAPITAL = 100000
    SYMBOLS = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA']
    SIMULATION_DAYS = 252  # 1 year of trading
    
    print_section("SIMULATION CONFIGURATION")
    print(f"  {'Initial Capital:':<25} ${INITIAL_CAPITAL:>15,.2f}")
    print(f"  {'Trading Assets:':<25} {', '.join(SYMBOLS)}")
    print(f"  {'Simulation Period:':<25} {SIMULATION_DAYS} days (~1 year)")
    print(f"  {'Strategy:':<25} {strategy_name.replace('_', ' ').title()}")
    
    # Step 1: Generate Market Data
    print_section("STEP 1: MARKET DATA GENERATION")
    print("  Generating synthetic market data using:")
    print("    • Geometric Brownian Motion (Random Walk)")
    print("    • GARCH-like Volatility Clustering")
    print("    • Jump Diffusion for realistic price gaps")
    print()
    
    data_generator = MarketDataGenerator(
        symbols=SYMBOLS,
        drift=0.0002,      # Slight upward drift (5% annual)
        volatility=0.02,   # 2% daily volatility (~32% annual)
        seed=42            # For reproducibility
    )
    
    market_data = data_generator.generate_historical_data(
        days=SIMULATION_DAYS,
        include_jumps=True,
        volatility_clustering=True
    )
    
    print(f"  ✓ Generated {len(market_data):,} data points")
    print(f"  ✓ Date Range: {market_data['timestamp'].min().strftime('%Y-%m-%d')} to "
          f"{market_data['timestamp'].max().strftime('%Y-%m-%d')}")
    
    # Show sample prices
    print("\n  Sample Initial Prices:")
    first_day = market_data[market_data['timestamp'] == market_data['timestamp'].min()]
    for _, row in first_day.iterrows():
        print(f"    {row['symbol']}: ${row['close']:.2f}")
    
    # Step 2: Initialize Portfolio
    print_section("STEP 2: PORTFOLIO INITIALIZATION")
    portfolio = PortfolioManager(initial_capital=INITIAL_CAPITAL)
    print(f"  ✓ Portfolio created with ${INITIAL_CAPITAL:,.2f} initial capital")
    print(f"  ✓ Ready to track:")
    print(f"      • Realized P&L (from closed trades)")
    print(f"      • Unrealized P&L (open positions)")
    print(f"      • Portfolio exposure (per asset and total)")
    
    # Step 3: Select and Initialize Strategy
    print_section("STEP 3: STRATEGY SELECTION")
    
    if strategy_name == "moving_average":
        strategy = MovingAverageStrategy(short_window=20, long_window=50)
        print("  Strategy: Moving Average Crossover")
        print("    • Buy when 20-day MA crosses above 50-day MA (Golden Cross)")
        print("    • Sell when 20-day MA crosses below 50-day MA (Death Cross)")
        print(f"    • Lookback period: {strategy.lookback_period} days")
    
    elif strategy_name == "momentum":
        strategy = MomentumStrategy(lookback_period=20, threshold=0.02)
        print("  Strategy: Momentum Trading")
        print("    • Buy when price momentum exceeds +2% over 20 days")
        print("    • Sell when price momentum falls below -2%")
        print(f"    • Lookback period: {strategy.lookback_period} days")
    
    elif strategy_name == "mean_reversion":
        strategy = MeanReversionStrategy(lookback_period=20, std_threshold=2.0)
        print("  Strategy: Mean Reversion")
        print("    • Buy when price falls 2σ below 20-day mean")
        print("    • Sell when price rises 2σ above 20-day mean")
        print(f"    • Lookback period: {strategy.lookback_period} days")
    
    else:
        print(f"  Unknown strategy: {strategy_name}, using Moving Average")
        strategy = MovingAverageStrategy(short_window=20, long_window=50)
    
    # Step 4: Initialize Trading Engine
    print_section("STEP 4: TRADING ENGINE")
    engine = TradingEngine(
        portfolio=portfolio,
        strategy=strategy,
        commission=0.001,          # 0.1% commission per trade
        position_size_pct=0.2,     # Max 20% of capital per position
        max_positions=5            # Max 5 concurrent positions
    )
    
    print(f"  ✓ Trading engine initialized")
    print(f"  ✓ Commission rate: 0.1%")
    print(f"  ✓ Position sizing: 20% max per trade")
    print(f"  ✓ Max concurrent positions: 5")
    
    # Step 5: Run Simulation
    print_section("STEP 5: RUNNING SIMULATION")
    print("  Processing market data and executing trades...\n")
    
    metrics = engine.run(market_data, verbose=verbose, print_interval=50)
    
    # Step 6: Final Results
    print_section("SIMULATION COMPLETE")
    
    # Get trade history
    trade_history = engine.get_trade_history()
    if not trade_history.empty:
        print("  Recent Trade Activity:")
        print("  " + "-"*70)
        recent = trade_history.tail(5)
        for _, trade in recent.iterrows():
            action = "BUY " if trade['side'] == 'buy' else "SELL"
            print(f"    {action} {trade['quantity']:>4} {trade['symbol']:<5} @ ${trade['price']:>8.2f}")
    
    return metrics


def run_strategy_comparison():
    """Run and compare multiple strategies on the same market data."""
    print_banner()
    print_section("STRATEGY COMPARISON MODE")
    
    print("  Comparing different trading strategies on identical market conditions")
    print("  This demonstrates how strategy selection impacts performance.\n")
    
    strategies = [
        ("Moving Average", MovingAverageStrategy(short_window=20, long_window=50)),
        ("Momentum", MomentumStrategy(lookback_period=20, threshold=0.02)),
        ("Mean Reversion", MeanReversionStrategy(lookback_period=20, std_threshold=2.0)),
    ]
    
    INITIAL_CAPITAL = 100000
    SYMBOLS = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA']
    SIMULATION_DAYS = 252
    
    # Generate market data once (same for all strategies)
    print("  Generating market data...")
    data_generator = MarketDataGenerator(
        symbols=SYMBOLS,
        drift=0.0002,
        volatility=0.02,
        seed=42
    )
    market_data = data_generator.generate_historical_data(
        days=SIMULATION_DAYS,
        include_jumps=True,
        volatility_clustering=True
    )
    print(f"  ✓ Generated {len(market_data):,} data points\n")
    
    results = []
    
    for strategy_name, strategy in strategies:
        print(f"\n  Testing: {strategy_name}")
        print("  " + "-"*50)
        
        # Create fresh portfolio for each strategy
        portfolio = PortfolioManager(initial_capital=INITIAL_CAPITAL)
        
        # Create trading engine
        engine = TradingEngine(
            portfolio=portfolio,
            strategy=strategy,
            commission=0.001,
            position_size_pct=0.2,
            max_positions=5
        )
        
        # Run simulation (quiet mode)
        metrics = engine.run(market_data, verbose=False)
        
        # Store results
        results.append({
            'strategy': strategy_name,
            'final_value': metrics['final_value'],
            'total_return': metrics['total_return'],
            'sharpe_ratio': metrics['sharpe_ratio'],
            'max_drawdown': metrics['max_drawdown'],
            'num_trades': metrics['num_trades'],
            'win_rate': metrics.get('win_rate', 0),
            'profit_factor': metrics.get('profit_factor', 0)
        })
        
        # Quick summary
        print(f"    Final Value:   ${metrics['final_value']:>12,.2f}")
        print(f"    Total Return:  {metrics['total_return']*100:>+12.2f}%")
        print(f"    Sharpe Ratio:  {metrics['sharpe_ratio']:>12.2f}")
        print(f"    Max Drawdown:  {metrics['max_drawdown']*100:>12.2f}%")
        print(f"    Trades:        {metrics['num_trades']:>12}")
    
    # Print comparison table
    print_section("STRATEGY COMPARISON RESULTS")
    
    # Sort by total return
    results.sort(key=lambda x: x['total_return'], reverse=True)
    
    # Header
    print(f"  {'Strategy':<18} {'Return':>10} {'Sharpe':>10} {'Drawdown':>12} {'Win Rate':>10} {'Trades':>8}")
    print("  " + "-"*70)
    
    for i, result in enumerate(results):
        rank = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else "  "
        print(
            f"  {rank}{result['strategy']:<16} "
            f"{result['total_return']*100:>+9.2f}% "
            f"{result['sharpe_ratio']:>10.2f} "
            f"{result['max_drawdown']*100:>11.2f}% "
            f"{result['win_rate']*100:>9.1f}% "
            f"{result['num_trades']:>8}"
        )
    
    print("\n  Winner: " + results[0]['strategy'])
    print(f"  Best Return: {results[0]['total_return']*100:+.2f}%")
    print()


def run_streaming_demo():
    """Demonstrate real-time streaming data capabilities."""
    print_banner()
    print_section("STREAMING DATA DEMONSTRATION")
    
    print("  This demo shows the platform's streaming data capabilities.")
    print("  Market data is generated tick-by-tick in real-time.\n")
    
    SYMBOLS = ['AAPL', 'GOOGL', 'MSFT']
    NUM_TICKS = 500
    
    # Create data generator
    data_generator = MarketDataGenerator(
        symbols=SYMBOLS,
        drift=0.0001,
        volatility=0.015,
        seed=None  # Random for variety
    )
    
    # Create portfolio and engine
    portfolio = PortfolioManager(initial_capital=50000)
    strategy = MovingAverageStrategy(short_window=10, long_window=30)
    engine = TradingEngine(
        portfolio=portfolio,
        strategy=strategy,
        commission=0.001
    )
    
    print(f"  Streaming {NUM_TICKS} ticks of market data...")
    print("  " + "-"*50)
    
    # Track prices for display
    tick_count = 0
    price_history = {s: [] for s in SYMBOLS}
    
    for prices in data_generator.stream_prices(num_ticks=NUM_TICKS):
        tick_count += 1
        
        # Track prices
        for symbol, price in prices.items():
            price_history[symbol].append(price)
        
        # Update portfolio
        portfolio.update_prices(prices)
        
        # Show periodic updates
        if tick_count % 100 == 0:
            print(f"\n  Tick {tick_count}:")
            for symbol in SYMBOLS:
                current = prices[symbol]
                start = price_history[symbol][0]
                change = ((current - start) / start) * 100
                print(f"    {symbol}: ${current:.2f} ({change:+.2f}%)")
            
            print(f"    Portfolio: ${portfolio.get_total_value():,.2f}")
    
    print("\n  " + "-"*50)
    print(f"  ✓ Processed {NUM_TICKS} streaming ticks")
    print(f"  ✓ Final Portfolio Value: ${portfolio.get_total_value():,.2f}")


def show_features():
    """Display platform features and capabilities."""
    print_banner()
    print_section("PLATFORM FEATURES")
    
    features = """
    MARKET DATA GENERATION
    ══════════════════════
    • Geometric Brownian Motion (Random Walk)
    • Jump Diffusion (Merton Model) for sudden price moves
    • GARCH-like Volatility Clustering
    • Correlated multi-asset simulation
    • Real-time streaming data generation
    • Configurable drift, volatility, and jump parameters

    TRADING ENGINE
    ══════════════
    • Multiple strategy support (Moving Average, Momentum, Mean Reversion)
    • Market order execution with realistic commission
    • Position sizing controls (% of capital, max positions)
    • Real-time signal processing
    • Order history and trade logging

    PORTFOLIO & RISK TRACKING
    ═════════════════════════
    • Real-time Unrealized P&L (open positions)
    • Realized P&L (closed trades)
    • Per-asset exposure tracking
    • Total portfolio exposure monitoring
    • High water mark and drawdown calculation
    • Comprehensive portfolio snapshots

    PERFORMANCE METRICS
    ══════════════════
    • Total Return
    • Sharpe Ratio (risk-adjusted return)
    • Sortino Ratio (downside risk)
    • Calmar Ratio (return/drawdown)
    • Maximum Drawdown
    • Win Rate & Profit Factor
    • Trade Statistics
    """
    print(features)


def main():
    """Main entry point with interactive menu."""
    while True:
        print("\n" + "="*60)
        print("  QUANTQUEST TRADING PLATFORM")
        print("="*60)
        print("\n  Select an option:\n")
        print("    1. Run Full Simulation (Moving Average)")
        print("    2. Run Momentum Strategy")
        print("    3. Run Mean Reversion Strategy")
        print("    4. Compare All Strategies")
        print("    5. Streaming Data Demo")
        print("    6. View Platform Features")
        print("    0. Exit\n")
        
        choice = input("  Enter choice (0-6): ").strip()
        
        if choice == "1":
            run_simulation("moving_average")
        elif choice == "2":
            run_simulation("momentum")
        elif choice == "3":
            run_simulation("mean_reversion")
        elif choice == "4":
            run_strategy_comparison()
        elif choice == "5":
            run_streaming_demo()
        elif choice == "6":
            show_features()
        elif choice == "0":
            print("\n  Thank you for using QuantQuest!\n")
            sys.exit(0)
        else:
            print("\n  Invalid choice. Please try again.")
        
        input("\n  Press Enter to continue...")


if __name__ == "__main__":
    # Run with command line argument or interactive menu
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg == "compare":
            run_strategy_comparison()
        elif arg == "stream":
            run_streaming_demo()
        elif arg == "features":
            show_features()
        elif arg in ["ma", "moving_average"]:
            run_simulation("moving_average")
        elif arg == "momentum":
            run_simulation("momentum")
        elif arg in ["mr", "mean_reversion"]:
            run_simulation("mean_reversion")
        else:
            print(f"Unknown argument: {arg}")
            print("Usage: python main.py [compare|stream|features|ma|momentum|mr]")
    else:
        main()
