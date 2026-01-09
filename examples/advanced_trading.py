"""
Advanced Trading Example

Demonstrates advanced features:
- Custom strategy implementation
- Multiple asset trading
- Performance analysis
- Trade history visualization
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

from src.market_data.data_generator import MarketDataGenerator
from src.trading.trading_engine import TradingEngine
from src.trading.strategies.base_strategy import BaseStrategy
from src.portfolio.portfolio_manager import PortfolioManager
from src.utils.metrics import generate_performance_report


class CustomMultiFactorStrategy(BaseStrategy):
    """
    Custom multi-factor strategy combining momentum and mean reversion.
    """
    
    def __init__(self, momentum_period: int = 20, mean_period: int = 30):
        super().__init__(lookback_period=max(momentum_period, mean_period) + 5)
        self.momentum_period = momentum_period
        self.mean_period = mean_period
    
    def generate_signals(self, market_data: pd.DataFrame) -> dict:
        """Generate signals using multiple factors."""
        signals = {}
        
        if not self.validate_data(market_data):
            return signals
        
        for symbol in market_data['symbol'].unique():
            symbol_data = self.get_latest_data(market_data, symbol)
            
            if len(symbol_data) < self.lookback_period:
                signals[symbol] = 0
                continue
            
            # Factor 1: Momentum
            current_price = symbol_data['close'].iloc[-1]
            past_price = symbol_data['close'].iloc[-self.momentum_period]
            momentum = (current_price - past_price) / past_price
            
            # Factor 2: Mean Reversion
            mean_price = symbol_data['close'].tail(self.mean_period).mean()
            std_price = symbol_data['close'].tail(self.mean_period).std()
            z_score = (current_price - mean_price) / std_price if std_price > 0 else 0
            
            # Combine factors
            signal = 0
            
            # Strong momentum + not overbought -> Buy
            if momentum > 0.03 and z_score < 1.5:
                signal = 1
            
            # Negative momentum or very overbought -> Sell
            elif momentum < -0.02 or z_score > 2:
                signal = -1
            
            signals[symbol] = signal
        
        return signals


def plot_equity_curve(trade_log, portfolio_value):
    """Plot equity curve over time."""
    if not trade_log:
        print("No trades to plot")
        return
    
    df = pd.DataFrame(trade_log)
    
    plt.figure(figsize=(12, 6))
    plt.plot(df.index, df['cash_after'], label='Cash', alpha=0.7)
    plt.axhline(y=portfolio_value, color='r', linestyle='--', label='Final Value')
    plt.xlabel('Trade Number')
    plt.ylabel('Portfolio Value ($)')
    plt.title('Portfolio Value Over Time')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('equity_curve.png')
    print("Equity curve saved to equity_curve.png")


def main():
    """Run advanced trading simulation."""
    
    print("\n" + "="*80)
    print(" " * 25 + "ADVANCED TRADING EXAMPLE")
    print("="*80 + "\n")
    
    # Configuration
    SYMBOLS = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'NVDA', 'META', 'NFLX']
    INITIAL_CAPITAL = 200000
    SIMULATION_DAYS = 365
    
    print("CONFIGURATION:")
    print(f"  Symbols: {', '.join(SYMBOLS)}")
    print(f"  Initial Capital: ${INITIAL_CAPITAL:,.2f}")
    print(f"  Simulation Period: {SIMULATION_DAYS} days")
    print(f"  Strategy: Custom Multi-Factor (Momentum + Mean Reversion)")
    print("\n" + "-"*80 + "\n")
    
    # Generate market data
    print("Generating market data with realistic characteristics...")
    data_gen = MarketDataGenerator(
        symbols=SYMBOLS,
        drift=0.0003,  # Slightly bullish market
        volatility=0.025,  # Higher volatility
        seed=123
    )
    
    market_data = data_gen.generate_historical_data(days=SIMULATION_DAYS)
    
    # Add some market events
    print("Adding random market events (crashes/rallies)...")
    market_data = data_gen.add_market_events(
        market_data,
        event_probability=0.03,
        event_magnitude=0.08
    )
    
    print(f"Generated {len(market_data)} data points")
    print(f"Date range: {market_data['timestamp'].min()} to {market_data['timestamp'].max()}\n")
    
    # Initialize components
    print("Initializing trading system...")
    portfolio = PortfolioManager(initial_capital=INITIAL_CAPITAL)
    strategy = CustomMultiFactorStrategy(momentum_period=20, mean_period=30)
    engine = TradingEngine(portfolio, strategy, commission=0.0015)
    
    print("✓ Portfolio initialized")
    print("✓ Custom strategy loaded")
    print("✓ Trading engine ready\n")
    
    # Run simulation
    print("Running simulation...")
    print("="*80)
    
    metrics = engine.run(market_data, verbose=True)
    
    # Detailed analysis
    print("\n" + "="*80)
    print("DETAILED PERFORMANCE ANALYSIS")
    print("="*80 + "\n")
    
    # Get trade history
    trade_history = engine.get_trade_history()
    
    if not trade_history.empty:
        print(f"Total Trades: {len(trade_history)}")
        print(f"\nTrade Breakdown:")
        print(f"  Buy Orders:  {len(trade_history[trade_history['side'] == 'BUY'])}")
        print(f"  Sell Orders: {len(trade_history[trade_history['side'] == 'SELL'])}")
        
        # Most traded symbols
        print(f"\nMost Traded Symbols:")
        symbol_counts = trade_history['symbol'].value_counts().head(5)
        for symbol, count in symbol_counts.items():
            print(f"  {symbol}: {count} trades")
        
        # Average trade size
        avg_commission = trade_history['commission'].mean()
        total_commission = trade_history['commission'].sum()
        print(f"\nCommission Analysis:")
        print(f"  Average per trade: ${avg_commission:.2f}")
        print(f"  Total paid: ${total_commission:.2f}")
        
        # Trade history sample
        print(f"\nSample Trade History (First 5 trades):")
        print(trade_history.head(5).to_string(index=False))
        
        print(f"\nSample Trade History (Last 5 trades):")
        print(trade_history.tail(5).to_string(index=False))
    
    # Portfolio statistics
    print(f"\n" + "-"*80)
    stats = portfolio.get_statistics()
    print(f"\nPortfolio Statistics:")
    print(f"  Initial Capital:  ${stats['initial_capital']:,.2f}")
    print(f"  Final Value:      ${stats['total_value']:,.2f}")
    print(f"  Total Return:     {stats['total_return']*100:.2f}%")
    print(f"  Realized P&L:     ${stats['realized_pnl']:,.2f}")
    print(f"  Unrealized P&L:   ${stats['unrealized_pnl']:,.2f}")
    print(f"  Cash Remaining:   ${stats['current_cash']:,.2f}")
    print(f"  Portfolio Value:  ${stats['portfolio_value']:,.2f}")
    print(f"  Total Exposure:   {stats['total_exposure']:.2f}%")
    print(f"  Open Positions:   {stats['num_positions']}")
    
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80 + "\n")
    
    # Optional: Plot equity curve
    try:
        plot_equity_curve(portfolio.trade_history, stats['total_value'])
    except Exception as e:
        print(f"Could not generate plot: {e}")


if __name__ == "__main__":
    main()
