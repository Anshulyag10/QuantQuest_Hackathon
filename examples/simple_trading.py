"""
Simple Trading Simulation Example

Demonstrates the core features of the QuantQuest trading platform:
1. Synthetic market data generation
2. Trading strategy execution
3. Real-time P&L tracking
4. Portfolio exposure monitoring
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.market_data.data_generator import MarketDataGenerator
from src.trading.trading_engine import TradingEngine
from src.trading.strategies.moving_average import MovingAverageStrategy
from src.portfolio.portfolio_manager import PortfolioManager


def main():
    """Run a simple trading simulation demonstrating key features."""
    
    print("\n" + "="*70)
    print("  SIMPLE TRADING SIMULATION EXAMPLE")
    print("="*70 + "\n")
    
    # ═══════════════════════════════════════════════════════════════════════
    # 1. MARKET DATA GENERATION
    # ═══════════════════════════════════════════════════════════════════════
    print("📊 STEP 1: Generating Synthetic Market Data")
    print("-"*50)
    
    # Create data generator with realistic parameters
    data_gen = MarketDataGenerator(
        symbols=['AAPL', 'GOOGL', 'MSFT'],
        drift=0.0003,       # Slight upward trend
        volatility=0.025,   # 2.5% daily volatility
        seed=42             # Reproducibility
    )
    
    # Generate historical data using GBM with volatility clustering
    market_data = data_gen.generate_historical_data(
        days=100,                    # 100 trading days
        include_jumps=True,          # Add jump diffusion
        volatility_clustering=True   # GARCH-like behavior
    )
    
    print(f"  ✓ Generated {len(market_data)} data points")
    print(f"  ✓ Symbols: {', '.join(market_data['symbol'].unique())}")
    print(f"  ✓ Period: {market_data['timestamp'].min().strftime('%Y-%m-%d')} to "
          f"{market_data['timestamp'].max().strftime('%Y-%m-%d')}")
    print()
    
    # ═══════════════════════════════════════════════════════════════════════
    # 2. PORTFOLIO INITIALIZATION
    # ═══════════════════════════════════════════════════════════════════════
    print("💰 STEP 2: Initializing Portfolio")
    print("-"*50)
    
    portfolio = PortfolioManager(initial_capital=50000)
    
    print(f"  ✓ Initial Capital: ${portfolio.initial_capital:,.2f}")
    print(f"  ✓ Tracking: Realized P&L, Unrealized P&L, Exposure")
    print()
    
    # ═══════════════════════════════════════════════════════════════════════
    # 3. STRATEGY SETUP
    # ═══════════════════════════════════════════════════════════════════════
    print("📈 STEP 3: Setting Up Trading Strategy")
    print("-"*50)
    
    strategy = MovingAverageStrategy(
        short_window=10,   # 10-day fast MA
        long_window=30     # 30-day slow MA
    )
    
    print(f"  ✓ Strategy: Moving Average Crossover")
    print(f"  ✓ Fast MA: {strategy.short_window} days")
    print(f"  ✓ Slow MA: {strategy.long_window} days")
    print(f"  ✓ Buy Signal: Fast MA crosses above Slow MA")
    print(f"  ✓ Sell Signal: Fast MA crosses below Slow MA")
    print()
    
    # ═══════════════════════════════════════════════════════════════════════
    # 4. TRADING ENGINE
    # ═══════════════════════════════════════════════════════════════════════
    print("⚙️  STEP 4: Initializing Trading Engine")
    print("-"*50)
    
    engine = TradingEngine(
        portfolio=portfolio,
        strategy=strategy,
        commission=0.001,         # 0.1% commission
        position_size_pct=0.25,   # 25% of capital per trade
        max_positions=3           # Max 3 concurrent positions
    )
    
    print(f"  ✓ Commission: 0.1% per trade")
    print(f"  ✓ Position Size: 25% of capital max")
    print(f"  ✓ Max Positions: 3")
    print()
    
    # ═══════════════════════════════════════════════════════════════════════
    # 5. RUN SIMULATION
    # ═══════════════════════════════════════════════════════════════════════
    print("🚀 STEP 5: Running Simulation")
    print("-"*50)
    print()
    
    # Run the simulation with verbose output
    metrics = engine.run(market_data, verbose=True, print_interval=20)
    
    # ═══════════════════════════════════════════════════════════════════════
    # 6. RESULTS SUMMARY
    # ═══════════════════════════════════════════════════════════════════════
    print("\n" + "="*70)
    print("  SIMULATION COMPLETE - KEY RESULTS")
    print("="*70)
    
    print(f"\n  📈 Performance:")
    print(f"     Total Return:     {metrics['total_return_pct']:>+10.2f}%")
    print(f"     Total P&L:        ${metrics['total_pnl']:>+12,.2f}")
    print(f"     Sharpe Ratio:     {metrics['sharpe_ratio']:>10.2f}")
    
    print(f"\n  📊 Risk:")
    print(f"     Max Drawdown:     {metrics['max_drawdown_pct']:>10.2f}%")
    print(f"     Final Exposure:   {metrics['final_exposure']:>10.1f}%")
    
    print(f"\n  💼 Trading:")
    print(f"     Total Trades:     {metrics['num_trades']:>10}")
    print(f"     Win Rate:         {metrics['win_rate_pct']:>10.2f}%")
    print(f"     Profit Factor:    {metrics['profit_factor']:>10.2f}")
    
    print(f"\n  💰 P&L Breakdown:")
    print(f"     Realized P&L:     ${metrics['realized_pnl']:>+12,.2f}")
    print(f"     Unrealized P&L:   ${metrics['unrealized_pnl']:>+12,.2f}")
    print(f"     Commissions:      ${metrics['total_commission']:>12,.2f}")
    
    print("\n" + "="*70 + "\n")
    
    return metrics


if __name__ == "__main__":
    main()
