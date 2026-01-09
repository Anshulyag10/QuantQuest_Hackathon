"""
Trading Engine - Core trading logic and strategy execution

Processes market data, executes strategies, and manages order flow.
Provides real-time P&L tracking, exposure monitoring, and comprehensive metrics.
"""

import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime

from ..market_data.data_generator import MarketSimulator
from ..portfolio.portfolio_manager import PortfolioManager
from .order import Order, OrderType, OrderSide, OrderExecutor
from .strategies.base_strategy import BaseStrategy


class TradingEngine:
    """
    Core trading engine that executes strategies and manages trades.
    
    Features:
    - Strategy signal processing
    - Order execution with commission
    - Real-time P&L tracking (realized + unrealized)
    - Portfolio exposure monitoring
    - Comprehensive performance metrics
    """
    
    def __init__(
        self,
        portfolio: PortfolioManager,
        strategy: BaseStrategy,
        commission: float = 0.001,
        position_size_pct: float = 0.2,
        max_positions: int = 10
    ):
        """
        Initialize trading engine.
        
        Args:
            portfolio: Portfolio manager instance
            strategy: Trading strategy to execute
            commission: Commission rate (default 0.1%)
            position_size_pct: Max % of capital per position (default 20%)
            max_positions: Maximum number of concurrent positions
        """
        self.portfolio = portfolio
        self.strategy = strategy
        self.executor = OrderExecutor(commission)
        self.position_size_pct = position_size_pct
        self.max_positions = max_positions
        
        # Order and trade tracking
        self.order_history: List[Order] = []
        self.trade_log: List[Dict] = []
        
        # Performance tracking
        self.equity_curve: List[Dict] = []
        self.daily_pnl: List[Dict] = []
    
    def process_signals(
        self,
        signals: Dict[str, int],
        current_prices: Dict[str, float]
    ) -> List[Order]:
        """
        Convert trading signals to orders.
        
        Args:
            signals: Dictionary of symbol -> signal (-1, 0, 1)
                    -1: sell, 0: hold, 1: buy
            current_prices: Current market prices
            
        Returns:
            List of generated orders
        """
        orders = []
        
        for symbol, signal in signals.items():
            if signal == 0:
                continue
            
            current_price = current_prices.get(symbol, 0)
            if current_price == 0:
                continue
            
            # Calculate position size based on available capital
            available_capital = self.portfolio.cash
            position_value = available_capital * self.position_size_pct
            quantity = int(position_value / current_price)
            
            if quantity == 0:
                continue
            
            # Check position limits
            num_positions = len(self.portfolio.positions)
            
            # Determine order side
            if signal > 0:  # Buy signal
                # Only buy if we don't already have a position and under max positions
                if symbol not in self.portfolio.positions and num_positions < self.max_positions:
                    order = Order(
                        symbol=symbol,
                        side=OrderSide.BUY,
                        quantity=quantity,
                        order_type=OrderType.MARKET
                    )
                    orders.append(order)
            
            elif signal < 0:  # Sell signal
                # Check if we have a position to sell
                position = self.portfolio.get_position(symbol)
                if position and position.quantity > 0:
                    order = Order(
                        symbol=symbol,
                        side=OrderSide.SELL,
                        quantity=position.quantity,  # Sell entire position
                        order_type=OrderType.MARKET
                    )
                    orders.append(order)
        
        return orders
    
    def execute_orders(
        self,
        orders: List[Order],
        current_prices: Dict[str, float],
        timestamp: Optional[datetime] = None
    ) -> List[Dict]:
        """
        Execute a list of orders.
        
        Args:
            orders: List of orders to execute
            current_prices: Current market prices
            timestamp: Current simulation timestamp
            
        Returns:
            List of execution details
        """
        executions = []
        
        for order in orders:
            current_price = current_prices.get(order.symbol, 0)
            if current_price == 0:
                order.reject()
                continue
            
            # Try to execute the order
            executed, execution_price, commission = self.executor.execute_order(
                order, current_price
            )
            
            if executed:
                # Update portfolio
                if order.side == OrderSide.BUY:
                    try:
                        self.portfolio.buy(
                            order.symbol,
                            order.quantity,
                            execution_price,
                            commission
                        )
                    except ValueError as e:
                        # Insufficient funds
                        order.reject()
                        continue
                else:  # SELL
                    try:
                        self.portfolio.sell(
                            order.symbol,
                            order.quantity,
                            execution_price,
                            commission
                        )
                    except ValueError as e:
                        # No position or insufficient quantity
                        order.reject()
                        continue
                
                # Log trade
                trade_record = {
                    'timestamp': timestamp or order.timestamp,
                    'symbol': order.symbol,
                    'side': order.side.value,
                    'quantity': order.quantity,
                    'price': execution_price,
                    'commission': commission,
                    'order_id': order.order_id,
                    'value': order.quantity * execution_price
                }
                self.trade_log.append(trade_record)
                executions.append(trade_record)
            
            self.order_history.append(order)
        
        return executions
    
    def run(
        self,
        market_data: pd.DataFrame,
        verbose: bool = True,
        print_interval: int = 50
    ) -> Dict:
        """
        Run the trading simulation.
        
        Args:
            market_data: Historical market data
            verbose: Print progress information
            print_interval: Steps between progress updates
            
        Returns:
            Dictionary of performance metrics
        """
        # Initialize market simulator
        simulator = MarketSimulator(market_data)
        
        if verbose:
            print(f"\n{'='*70}")
            print(f"{'TRADING SIMULATION':^70}")
            print(f"{'='*70}")
            print(f"\n  Initial Capital:  ${self.portfolio.initial_capital:>15,.2f}")
            print(f"  Strategy:         {self.strategy.__class__.__name__:>15}")
            print(f"  Position Size:    {self.position_size_pct*100:>14.0f}%")
            print(f"  Commission:       {self.executor.commission*100:>14.2f}%")
            print(f"\n{'='*70}\n")
        
        # Reset tracking
        self.equity_curve = []
        self.daily_pnl = []
        prev_value = self.portfolio.initial_capital
        
        # Run simulation
        step_count = 0
        while not simulator.is_complete():
            # Get current market data
            current_prices = simulator.get_current_prices()
            historical_data = simulator.get_historical_data(
                lookback=self.strategy.lookback_period
            )
            current_timestamp = simulator.get_current_timestamp()
            
            if not current_prices:
                break
            
            # Update portfolio with current prices
            self.portfolio.update_prices(current_prices)
            
            # Generate trading signals
            signals = self.strategy.generate_signals(historical_data)
            
            # Process signals and create orders
            orders = self.process_signals(signals, current_prices)
            
            # Execute orders
            executions = self.execute_orders(orders, current_prices, current_timestamp)
            
            # Track equity and daily P&L
            current_value = self.portfolio.get_total_value()
            daily_return = (current_value - prev_value) / prev_value if prev_value > 0 else 0
            
            self.equity_curve.append({
                'timestamp': current_timestamp,
                'equity': current_value,
                'cash': self.portfolio.cash,
                'positions_value': self.portfolio.get_portfolio_value()
            })
            
            self.daily_pnl.append({
                'timestamp': current_timestamp,
                'pnl': current_value - prev_value,
                'return': daily_return
            })
            
            prev_value = current_value
            
            # Move to next time step
            simulator.step()
            step_count += 1
            
            # Print progress with comprehensive P&L and exposure info
            if verbose and step_count % print_interval == 0:
                total_value = self.portfolio.get_total_value()
                realized_pnl = self.portfolio.realized_pnl
                unrealized_pnl = self.portfolio.get_unrealized_pnl()
                total_pnl = realized_pnl + unrealized_pnl
                exposure = self.portfolio.get_total_exposure()
                num_pos = len(self.portfolio.positions)
                
                # Calculate return percentage
                return_pct = ((total_value - self.portfolio.initial_capital) / 
                             self.portfolio.initial_capital * 100)
                
                print(f"  Day {step_count:>4} │ "
                      f"Value: ${total_value:>12,.2f} │ "
                      f"P&L: ${total_pnl:>10,.2f} ({return_pct:>+6.2f}%) │ "
                      f"Exposure: {exposure:>5.1f}% │ "
                      f"Positions: {num_pos}")
                
                # Show position details if any executions this period
                if executions and verbose:
                    for ex in executions:
                        action = "BUY " if ex['side'] == 'buy' else "SELL"
                        print(f"           └─ {action} {ex['quantity']} {ex['symbol']} @ ${ex['price']:.2f}")
        
        # Calculate performance metrics
        metrics = self._calculate_metrics()
        
        if verbose:
            print(f"\n{'='*70}")
            print(f"{'SIMULATION COMPLETE':^70}")
            print(f"{'='*70}\n")
            
            # Print portfolio summary
            self.portfolio.print_summary()
            
            # Print metrics
            self._print_metrics(metrics)
        
        return metrics
    
    def run_streaming(
        self,
        data_generator,
        num_ticks: int = 1000,
        verbose: bool = True
    ) -> Dict:
        """
        Run simulation with streaming data.
        
        Args:
            data_generator: MarketDataGenerator instance
            num_ticks: Number of ticks to process
            verbose: Print progress
            
        Returns:
            Performance metrics
        """
        if verbose:
            print(f"\n{'='*70}")
            print(f"{'STREAMING SIMULATION':^70}")
            print(f"{'='*70}\n")
        
        # Track prices for strategy
        price_history = {symbol: [] for symbol in data_generator.symbols}
        
        for tick, prices in enumerate(data_generator.stream_prices(num_ticks)):
            # Update price history
            for symbol, price in prices.items():
                price_history[symbol].append(price)
            
            # Update portfolio
            self.portfolio.update_prices(prices)
            
            # Need enough history for strategy
            min_history = min(len(h) for h in price_history.values())
            if min_history < self.strategy.lookback_period:
                continue
            
            # Create DataFrame for strategy
            data_rows = []
            for symbol in data_generator.symbols:
                recent_prices = price_history[symbol][-self.strategy.lookback_period:]
                for i, price in enumerate(recent_prices):
                    data_rows.append({
                        'timestamp': tick - self.strategy.lookback_period + i,
                        'symbol': symbol,
                        'close': price,
                        'open': price,
                        'high': price,
                        'low': price,
                        'volume': 1000000
                    })
            
            market_data = pd.DataFrame(data_rows)
            
            # Generate signals
            signals = self.strategy.generate_signals(market_data)
            
            # Process and execute
            orders = self.process_signals(signals, prices)
            self.execute_orders(orders, prices)
            
            # Track equity
            self.equity_curve.append({
                'timestamp': tick,
                'equity': self.portfolio.get_total_value()
            })
            
            if verbose and tick % 100 == 0:
                print(f"  Tick {tick}: Value=${self.portfolio.get_total_value():,.2f}")
        
        return self._calculate_metrics()
    
    def _calculate_metrics(self) -> Dict:
        """
        Calculate comprehensive performance metrics.
        
        Returns:
            Dictionary of metrics
        """
        if not self.equity_curve:
            return {}
        
        df = pd.DataFrame(self.equity_curve)
        
        # Basic metrics
        initial_value = self.portfolio.initial_capital
        final_value = df['equity'].iloc[-1]
        total_return = (final_value - initial_value) / initial_value
        
        # Returns series
        df['returns'] = df['equity'].pct_change()
        returns = df['returns'].dropna()
        
        # Risk metrics
        avg_return = returns.mean() if len(returns) > 0 else 0
        std_return = returns.std() if len(returns) > 0 else 0
        
        # Sharpe ratio (annualized, assuming 252 trading days)
        sharpe_ratio = (avg_return / std_return) * (252 ** 0.5) if std_return > 0 else 0
        
        # Sortino ratio (downside deviation)
        downside_returns = returns[returns < 0]
        downside_std = downside_returns.std() if len(downside_returns) > 0 else 0
        sortino_ratio = (avg_return / downside_std) * (252 ** 0.5) if downside_std > 0 else 0
        
        # Maximum drawdown
        df['cummax'] = df['equity'].cummax()
        df['drawdown'] = (df['equity'] - df['cummax']) / df['cummax']
        max_drawdown = df['drawdown'].min()
        
        # Trade statistics
        num_trades = len(self.trade_log)
        
        # Win rate and profit factor from realized P&L
        pnl_trades = [
            t['realized_pnl']
            for t in self.portfolio.trade_history
            if 'realized_pnl' in t
        ]
        
        num_closed = len(pnl_trades)
        wins = sum(1 for pnl in pnl_trades if pnl > 0)
        losses = sum(1 for pnl in pnl_trades if pnl < 0)
        total_wins = sum(pnl for pnl in pnl_trades if pnl > 0)
        total_losses = abs(sum(pnl for pnl in pnl_trades if pnl < 0))
        
        win_rate = wins / num_closed if num_closed > 0 else 0
        profit_factor = total_wins / total_losses if total_losses > 0 else float('inf') if total_wins > 0 else 0
        
        # Average trade metrics
        avg_win = total_wins / wins if wins > 0 else 0
        avg_loss = total_losses / losses if losses > 0 else 0
        
        # Calmar ratio (return / max drawdown)
        calmar_ratio = abs(total_return / max_drawdown) if max_drawdown != 0 else 0
        
        # Volatility (annualized)
        annual_volatility = std_return * (252 ** 0.5)
        
        return {
            # Returns
            'total_return': total_return,
            'total_return_pct': total_return * 100,
            'final_value': final_value,
            'initial_value': initial_value,
            'total_pnl': final_value - initial_value,
            
            # Risk metrics
            'sharpe_ratio': sharpe_ratio,
            'sortino_ratio': sortino_ratio,
            'calmar_ratio': calmar_ratio,
            'max_drawdown': max_drawdown,
            'max_drawdown_pct': max_drawdown * 100,
            'annual_volatility': annual_volatility,
            
            # Trade statistics
            'num_trades': num_trades,
            'num_closed_trades': num_closed,
            'winning_trades': wins,
            'losing_trades': losses,
            'win_rate': win_rate,
            'win_rate_pct': win_rate * 100,
            'profit_factor': profit_factor,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            
            # Portfolio
            'realized_pnl': self.portfolio.realized_pnl,
            'unrealized_pnl': self.portfolio.get_unrealized_pnl(),
            'total_commission': self.portfolio.total_commission,
            'final_exposure': self.portfolio.get_total_exposure()
        }
    
    def _print_metrics(self, metrics: Dict):
        """Print performance metrics in a formatted way."""
        if not metrics:
            return
        
        print(f"\n{'='*70}")
        print(f"{'PERFORMANCE METRICS':^70}")
        print(f"{'='*70}\n")
        
        # Returns section
        print("  RETURNS")
        print("  " + "-"*40)
        print(f"    Total Return:          {metrics['total_return_pct']:>+10.2f}%")
        print(f"    Total P&L:             ${metrics['total_pnl']:>+12,.2f}")
        print(f"    Final Portfolio Value: ${metrics['final_value']:>12,.2f}")
        
        # Risk section
        print(f"\n  RISK METRICS")
        print("  " + "-"*40)
        print(f"    Sharpe Ratio:          {metrics['sharpe_ratio']:>10.2f}")
        print(f"    Sortino Ratio:         {metrics['sortino_ratio']:>10.2f}")
        print(f"    Calmar Ratio:          {metrics['calmar_ratio']:>10.2f}")
        print(f"    Max Drawdown:          {metrics['max_drawdown_pct']:>10.2f}%")
        print(f"    Annual Volatility:     {metrics['annual_volatility']*100:>10.2f}%")
        
        # Trade statistics
        print(f"\n  TRADE STATISTICS")
        print("  " + "-"*40)
        print(f"    Total Trades:          {metrics['num_trades']:>10}")
        print(f"    Winning Trades:        {metrics['winning_trades']:>10}")
        print(f"    Losing Trades:         {metrics['losing_trades']:>10}")
        print(f"    Win Rate:              {metrics['win_rate_pct']:>10.2f}%")
        print(f"    Profit Factor:         {metrics['profit_factor']:>10.2f}")
        if metrics['avg_win'] > 0:
            print(f"    Average Win:           ${metrics['avg_win']:>10,.2f}")
        if metrics['avg_loss'] > 0:
            print(f"    Average Loss:          ${metrics['avg_loss']:>10,.2f}")
        
        # P&L breakdown
        print(f"\n  P&L BREAKDOWN")
        print("  " + "-"*40)
        print(f"    Realized P&L:          ${metrics['realized_pnl']:>+12,.2f}")
        print(f"    Unrealized P&L:        ${metrics['unrealized_pnl']:>+12,.2f}")
        print(f"    Total Commissions:     ${metrics['total_commission']:>12,.2f}")
        print(f"    Final Exposure:        {metrics['final_exposure']:>10.1f}%")
        
        print(f"\n{'='*70}\n")
    
    def get_trade_history(self) -> pd.DataFrame:
        """
        Get trade history as DataFrame.
        
        Returns:
            DataFrame of all trades
        """
        if not self.trade_log:
            return pd.DataFrame()
        
        return pd.DataFrame(self.trade_log)
    
    def get_equity_curve(self) -> pd.DataFrame:
        """
        Get equity curve as DataFrame.
        
        Returns:
            DataFrame with timestamp and equity values
        """
        if not self.equity_curve:
            return pd.DataFrame()
        
        return pd.DataFrame(self.equity_curve)
    
    def get_daily_pnl(self) -> pd.DataFrame:
        """
        Get daily P&L as DataFrame.
        
        Returns:
            DataFrame with daily P&L values
        """
        if not self.daily_pnl:
            return pd.DataFrame()
        
        return pd.DataFrame(self.daily_pnl)
