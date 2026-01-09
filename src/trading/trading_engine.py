"""
Trading Engine - Core trading logic and strategy execution

Processes market data, executes strategies, and manages order flow.
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
    """
    
    def __init__(
        self,
        portfolio: PortfolioManager,
        strategy: BaseStrategy,
        commission: float = 0.001
    ):
        """
        Initialize trading engine.
        
        Args:
            portfolio: Portfolio manager instance
            strategy: Trading strategy to execute
            commission: Commission rate (default 0.1%)
        """
        self.portfolio = portfolio
        self.strategy = strategy
        self.executor = OrderExecutor(commission)
        self.order_history: List[Order] = []
        self.trade_log: List[Dict] = []
    
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
            
            # Calculate position size (simplified - could be more sophisticated)
            position_value = self.portfolio.cash * 0.2  # Max 20% per position
            quantity = int(position_value / current_price)
            
            if quantity == 0:
                continue
            
            # Determine order side
            if signal > 0:  # Buy signal
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
                        quantity=position.quantity,
                        order_type=OrderType.MARKET
                    )
                    orders.append(order)
        
        return orders
    
    def execute_orders(
        self,
        orders: List[Order],
        current_prices: Dict[str, float]
    ):
        """
        Execute a list of orders.
        
        Args:
            orders: List of orders to execute
            current_prices: Current market prices
        """
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
                    self.portfolio.buy(
                        order.symbol,
                        order.quantity,
                        execution_price,
                        commission
                    )
                else:  # SELL
                    self.portfolio.sell(
                        order.symbol,
                        order.quantity,
                        execution_price,
                        commission
                    )
                
                # Log trade
                self.trade_log.append({
                    'timestamp': order.timestamp,
                    'symbol': order.symbol,
                    'side': order.side.value,
                    'quantity': order.quantity,
                    'price': execution_price,
                    'commission': commission,
                    'order_id': order.order_id
                })
            
            self.order_history.append(order)
    
    def run(
        self,
        market_data: pd.DataFrame,
        verbose: bool = True
    ) -> Dict:
        """
        Run the trading simulation.
        
        Args:
            market_data: Historical market data
            verbose: Print progress information
            
        Returns:
            Dictionary of performance metrics
        """
        # Initialize market simulator
        simulator = MarketSimulator(market_data)
        
        if verbose:
            print(f"\n{'='*60}")
            print(f"Starting Trading Simulation")
            print(f"{'='*60}")
            print(f"Initial Capital: ${self.portfolio.initial_capital:,.2f}")
            print(f"Strategy: {self.strategy.__class__.__name__}")
            print(f"{'='*60}\n")
        
        # Track equity curve
        equity_curve = []
        
        # Run simulation
        step_count = 0
        while not simulator.is_complete():
            # Get current market data
            current_prices = simulator.get_current_prices()
            historical_data = simulator.get_historical_data(
                lookback=self.strategy.lookback_period
            )
            
            if not current_prices:
                break
            
            # Update portfolio with current prices
            self.portfolio.update_prices(current_prices)
            
            # Generate trading signals
            signals = self.strategy.generate_signals(historical_data)
            
            # Process signals and create orders
            orders = self.process_signals(signals, current_prices)
            
            # Execute orders
            self.execute_orders(orders, current_prices)
            
            # Track equity
            equity_curve.append({
                'timestamp': simulator.timestamps[simulator.current_index],
                'equity': self.portfolio.get_total_value()
            })
            
            # Move to next time step
            simulator.step()
            step_count += 1
            
            # Print progress with P&L and exposure snapshots
            if verbose and step_count % 50 == 0:
                total_value = self.portfolio.get_total_value()
                realized_pnl = self.portfolio.realized_pnl
                unrealized_pnl = self.portfolio.get_unrealized_pnl()
                exposure = self.portfolio.get_total_exposure()
                print(
                    "Step {:<5d}: Value=${:>12,.2f} | Realized=${:>10,.2f} | "
                    "Unrealized=${:>10,.2f} | Exposure={:>6.2f}%".format(
                        step_count,
                        total_value,
                        realized_pnl,
                        unrealized_pnl,
                        exposure
                    )
                )
        
        # Calculate performance metrics
        metrics = self._calculate_metrics(equity_curve)
        
        if verbose:
            print(f"\n{'='*60}")
            print(f"Simulation Complete")
            print(f"{'='*60}\n")
            self.portfolio.print_summary()
            self._print_metrics(metrics)
        
        return metrics
    
    def _calculate_metrics(self, equity_curve: List[Dict]) -> Dict:
        """
        Calculate performance metrics.
        
        Args:
            equity_curve: List of equity values over time
            
        Returns:
            Dictionary of metrics
        """
        if not equity_curve:
            return {}
        
        df = pd.DataFrame(equity_curve)
        
        # Total return
        initial_value = self.portfolio.initial_capital
        final_value = df['equity'].iloc[-1]
        total_return = (final_value - initial_value) / initial_value
        
        # Returns
        df['returns'] = df['equity'].pct_change()
        
        # Sharpe ratio (annualized, assuming 252 trading days)
        avg_return = df['returns'].mean()
        std_return = df['returns'].std()
        sharpe_ratio = (avg_return / std_return) * (252 ** 0.5) if std_return > 0 else 0
        
        # Maximum drawdown
        df['cummax'] = df['equity'].cummax()
        df['drawdown'] = (df['equity'] - df['cummax']) / df['cummax']
        max_drawdown = df['drawdown'].min()

        # Trade statistics
        num_trades = len(self.trade_log)

        # Win rate and profit factor based on realized P&L from portfolio history
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
        profit_factor = total_wins / total_losses if total_losses > 0 else 0

        return {
            'total_return': total_return,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'num_trades': num_trades,
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'final_value': final_value,
            'initial_value': initial_value
        }
    
    def _print_metrics(self, metrics: Dict):
        """Print performance metrics."""
        if not metrics:
            return
        
        print(f"\n{'='*60}")
        print(f"Performance Metrics")
        print(f"{'='*60}")
        print(f"Total Return:     {metrics['total_return']*100:>10.2f}%")
        print(f"Sharpe Ratio:     {metrics['sharpe_ratio']:>10.2f}")
        print(f"Max Drawdown:     {metrics['max_drawdown']*100:>10.2f}%")
        print(f"Number of Trades: {metrics['num_trades']:>10}")
        print(f"Win Rate:         {metrics['win_rate']*100:>10.2f}%")
        print(f"Profit Factor:    {metrics['profit_factor']:>10.2f}")
        print(f"{'='*60}\n")
    
    def get_trade_history(self) -> pd.DataFrame:
        """
        Get trade history as DataFrame.
        
        Returns:
            DataFrame of all trades
        """
        if not self.trade_log:
            return pd.DataFrame()
        
        return pd.DataFrame(self.trade_log)
