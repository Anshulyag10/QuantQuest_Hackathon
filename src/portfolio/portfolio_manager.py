"""
Portfolio Manager - Manages portfolio, tracks P&L, and monitors risk

Comprehensive portfolio management including:
- Position management (open, close, scale)
- Cash management
- Realized and unrealized P&L tracking
- Portfolio exposure monitoring (per asset and total)
- Risk metrics
- Detailed reporting
"""

from typing import Dict, Optional, List
from datetime import datetime
from tabulate import tabulate

from .position import Position


class PortfolioManager:
    """
    Manages the trading portfolio.
    
    Tracks positions, cash, and calculates P&L and exposure metrics.
    Provides comprehensive reporting capabilities.
    """
    
    def __init__(self, initial_capital: float = 100000.0):
        """
        Initialize portfolio manager.
        
        Args:
            initial_capital: Starting capital
        """
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.positions: Dict[str, Position] = {}
        
        # P&L tracking
        self.realized_pnl = 0.0
        self.total_commission = 0.0
        
        # High water mark for drawdown calculation
        self.high_water_mark = initial_capital
        
        # Trade history
        self.trade_history: List[Dict] = []
        
        # Snapshot history for tracking over time
        self.portfolio_snapshots: List[Dict] = []
    
    def buy(
        self,
        symbol: str,
        quantity: int,
        price: float,
        commission: float = 0.0
    ) -> Dict:
        """
        Buy an asset.
        
        Args:
            symbol: Asset symbol
            quantity: Quantity to buy
            price: Purchase price
            commission: Transaction commission
            
        Returns:
            Trade details dictionary
        """
        cost = quantity * price + commission
        
        # Check if we have enough cash
        if cost > self.cash:
            raise ValueError(f"Insufficient cash: need ${cost:.2f}, have ${self.cash:.2f}")
        
        # Deduct cash
        self.cash -= cost
        self.total_commission += commission
        
        # Update or create position
        if symbol in self.positions:
            self.positions[symbol].add_quantity(quantity, price)
        else:
            self.positions[symbol] = Position(
                symbol=symbol,
                quantity=quantity,
                avg_entry_price=price,
                current_price=price
            )
        
        # Record trade
        trade_record = {
            'timestamp': datetime.now(),
            'symbol': symbol,
            'action': 'BUY',
            'quantity': quantity,
            'price': price,
            'value': quantity * price,
            'commission': commission,
            'cash_after': self.cash,
            'portfolio_value_after': self.get_total_value()
        }
        self.trade_history.append(trade_record)
        
        return trade_record
    
    def sell(
        self,
        symbol: str,
        quantity: int,
        price: float,
        commission: float = 0.0
    ) -> Dict:
        """
        Sell an asset.
        
        Args:
            symbol: Asset symbol
            quantity: Quantity to sell
            price: Sale price
            commission: Transaction commission
            
        Returns:
            Trade details dictionary
        """
        # Check if we have the position
        if symbol not in self.positions:
            raise ValueError(f"No position in {symbol}")
        
        position = self.positions[symbol]
        
        # Check if we have enough quantity
        if quantity > position.quantity:
            raise ValueError(
                f"Insufficient quantity: trying to sell {quantity}, "
                f"have {position.quantity}"
            )
        
        # Update current price before calculating P&L
        position.update_price(price)
        
        # Calculate realized P&L
        realized_pnl = position.reduce_quantity(quantity)
        self.realized_pnl += realized_pnl
        
        # Add cash from sale
        proceeds = quantity * price - commission
        self.cash += proceeds
        self.total_commission += commission
        
        # Update high water mark
        current_value = self.get_total_value()
        self.high_water_mark = max(self.high_water_mark, current_value)
        
        # Remove position if fully closed
        if position.quantity == 0:
            del self.positions[symbol]
        
        # Record trade
        trade_record = {
            'timestamp': datetime.now(),
            'symbol': symbol,
            'action': 'SELL',
            'quantity': quantity,
            'price': price,
            'value': quantity * price,
            'commission': commission,
            'realized_pnl': realized_pnl,
            'cash_after': self.cash,
            'portfolio_value_after': current_value
        }
        self.trade_history.append(trade_record)
        
        return trade_record
    
    def update_prices(self, prices: Dict[str, float]):
        """
        Update current market prices for all positions.
        
        Args:
            prices: Dictionary of symbol -> current_price
        """
        for symbol, position in self.positions.items():
            if symbol in prices:
                position.update_price(prices[symbol])
        
        # Update high water mark
        current_value = self.get_total_value()
        self.high_water_mark = max(self.high_water_mark, current_value)
    
    def take_snapshot(self, timestamp: Optional[datetime] = None):
        """
        Take a snapshot of current portfolio state.
        
        Args:
            timestamp: Timestamp for the snapshot
        """
        snapshot = {
            'timestamp': timestamp or datetime.now(),
            'cash': self.cash,
            'portfolio_value': self.get_portfolio_value(),
            'total_value': self.get_total_value(),
            'realized_pnl': self.realized_pnl,
            'unrealized_pnl': self.get_unrealized_pnl(),
            'exposure': self.get_total_exposure(),
            'num_positions': len(self.positions),
            'positions': {s: {'qty': p.quantity, 'price': p.current_price} 
                         for s, p in self.positions.items()}
        }
        self.portfolio_snapshots.append(snapshot)
    
    def get_position(self, symbol: str) -> Optional[Position]:
        """
        Get position for a symbol.
        
        Args:
            symbol: Asset symbol
            
        Returns:
            Position object or None
        """
        return self.positions.get(symbol)
    
    def get_unrealized_pnl(self) -> float:
        """
        Get total unrealized P&L across all positions.
        
        Returns:
            Total unrealized P&L
        """
        return sum(pos.get_unrealized_pnl() for pos in self.positions.values())
    
    def get_total_pnl(self) -> float:
        """
        Get total P&L (realized + unrealized).
        
        Returns:
            Total P&L
        """
        return self.realized_pnl + self.get_unrealized_pnl()
    
    def get_portfolio_value(self) -> float:
        """
        Get total value of positions (excluding cash).
        
        Returns:
            Total market value of all positions
        """
        return sum(pos.get_market_value() for pos in self.positions.values())
    
    def get_total_value(self) -> float:
        """
        Get total portfolio value (positions + cash).
        
        Returns:
            Total portfolio value
        """
        return self.cash + self.get_portfolio_value()
    
    def get_exposure(self) -> Dict[str, float]:
        """
        Get exposure per asset as percentage of portfolio.
        
        Returns:
            Dictionary of symbol -> exposure_percentage
        """
        total_value = self.get_total_value()
        
        if total_value == 0:
            return {}
        
        exposure = {}
        for symbol, position in self.positions.items():
            market_value = position.get_market_value()
            exposure[symbol] = (market_value / total_value) * 100
        
        return exposure
    
    def get_total_exposure(self) -> float:
        """
        Get total portfolio exposure (% of capital invested).
        
        Returns:
            Total exposure percentage
        """
        total_value = self.get_total_value()
        
        if total_value == 0:
            return 0.0
        
        portfolio_value = self.get_portfolio_value()
        return (portfolio_value / total_value) * 100
    
    def get_cash_percentage(self) -> float:
        """
        Get cash as percentage of total portfolio.
        
        Returns:
            Cash percentage
        """
        total_value = self.get_total_value()
        if total_value == 0:
            return 100.0
        return (self.cash / total_value) * 100
    
    def get_current_drawdown(self) -> float:
        """
        Get current drawdown from high water mark.
        
        Returns:
            Current drawdown as percentage (negative number)
        """
        if self.high_water_mark == 0:
            return 0.0
        
        current_value = self.get_total_value()
        return ((current_value - self.high_water_mark) / self.high_water_mark) * 100
    
    def get_return(self) -> float:
        """
        Get total return percentage.
        
        Returns:
            Total return as percentage
        """
        if self.initial_capital == 0:
            return 0.0
        return ((self.get_total_value() - self.initial_capital) / self.initial_capital) * 100
    
    def print_summary(self):
        """Print detailed portfolio summary."""
        print(f"\n{'='*80}")
        print(f"{'PORTFOLIO SUMMARY':^80}")
        print(f"{'='*80}\n")
        
        # Account summary
        total_value = self.get_total_value()
        total_return = self.get_return()
        
        print("  ACCOUNT OVERVIEW")
        print("  " + "-"*50)
        print(f"    Initial Capital:        ${self.initial_capital:>15,.2f}")
        print(f"    Current Cash:           ${self.cash:>15,.2f}")
        print(f"    Positions Value:        ${self.get_portfolio_value():>15,.2f}")
        print(f"    Total Value:            ${total_value:>15,.2f}")
        print(f"    Total Return:           {total_return:>+15.2f}%")
        
        # P&L summary
        total_pnl = self.get_total_pnl()
        
        print(f"\n  PROFIT & LOSS")
        print("  " + "-"*50)
        print(f"    Realized P&L:           ${self.realized_pnl:>+15,.2f}")
        print(f"    Unrealized P&L:         ${self.get_unrealized_pnl():>+15,.2f}")
        print(f"    Total P&L:              ${total_pnl:>+15,.2f}")
        print(f"    Total Commissions:      ${self.total_commission:>15,.2f}")
        
        # Risk metrics
        print(f"\n  RISK METRICS")
        print("  " + "-"*50)
        print(f"    Portfolio Exposure:     {self.get_total_exposure():>15.2f}%")
        print(f"    Cash Position:          {self.get_cash_percentage():>15.2f}%")
        print(f"    Current Drawdown:       {self.get_current_drawdown():>+15.2f}%")
        print(f"    High Water Mark:        ${self.high_water_mark:>15,.2f}")
        
        # Positions
        if self.positions:
            print(f"\n  OPEN POSITIONS")
            print("  " + "-"*76)
            
            position_data = []
            for symbol, pos in self.positions.items():
                unrealized = pos.get_unrealized_pnl()
                unrealized_pct = pos.get_unrealized_pnl_percent()
                exposure = self.get_exposure().get(symbol, 0)
                
                position_data.append([
                    symbol,
                    pos.quantity,
                    f"${pos.avg_entry_price:.2f}",
                    f"${pos.current_price:.2f}",
                    f"${pos.get_market_value():,.2f}",
                    f"${unrealized:+,.2f}",
                    f"{unrealized_pct:+.2f}%",
                    f"{exposure:.1f}%"
                ])
            
            headers = ['Symbol', 'Qty', 'Entry', 'Current', 'Value', 'P&L', 'Return', 'Exposure']
            print(tabulate(position_data, headers=headers, tablefmt='simple', 
                          colalign=('left', 'right', 'right', 'right', 'right', 'right', 'right', 'right')))
        else:
            print(f"\n  No open positions")
        
        # Trade statistics
        num_trades = len(self.trade_history)
        buys = sum(1 for t in self.trade_history if t['action'] == 'BUY')
        sells = sum(1 for t in self.trade_history if t['action'] == 'SELL')
        
        print(f"\n  TRADE STATISTICS")
        print("  " + "-"*50)
        print(f"    Total Trades:           {num_trades:>15}")
        print(f"    Buy Orders:             {buys:>15}")
        print(f"    Sell Orders:            {sells:>15}")
        
        print(f"\n{'='*80}\n")
    
    def print_positions(self):
        """Print current positions in a compact format."""
        if not self.positions:
            print("No open positions")
            return
        
        print("\nCurrent Positions:")
        print("-" * 60)
        
        for symbol, pos in self.positions.items():
            unrealized = pos.get_unrealized_pnl()
            unrealized_pct = pos.get_unrealized_pnl_percent()
            
            status = "+" if unrealized >= 0 else ""
            print(f"  {symbol}: {pos.quantity} shares @ ${pos.current_price:.2f} "
                  f"({status}${unrealized:.2f}, {status}{unrealized_pct:.1f}%)")
    
    def print_exposure(self):
        """Print exposure breakdown."""
        print("\nPortfolio Exposure:")
        print("-" * 40)
        
        exposure = self.get_exposure()
        cash_pct = self.get_cash_percentage()
        
        print(f"  Cash: {cash_pct:.1f}%")
        
        for symbol, exp in sorted(exposure.items(), key=lambda x: -x[1]):
            print(f"  {symbol}: {exp:.1f}%")
        
        print(f"  Total Invested: {self.get_total_exposure():.1f}%")
    
    def get_statistics(self) -> Dict:
        """
        Get comprehensive portfolio statistics.
        
        Returns:
            Dictionary of statistics
        """
        total_value = self.get_total_value()
        total_return = (total_value - self.initial_capital) / self.initial_capital
        
        return {
            'initial_capital': self.initial_capital,
            'current_cash': self.cash,
            'portfolio_value': self.get_portfolio_value(),
            'total_value': total_value,
            'realized_pnl': self.realized_pnl,
            'unrealized_pnl': self.get_unrealized_pnl(),
            'total_pnl': self.get_total_pnl(),
            'total_return': total_return,
            'total_return_pct': total_return * 100,
            'total_commission': self.total_commission,
            'num_positions': len(self.positions),
            'total_exposure': self.get_total_exposure(),
            'cash_percentage': self.get_cash_percentage(),
            'current_drawdown': self.get_current_drawdown(),
            'high_water_mark': self.high_water_mark,
            'num_trades': len(self.trade_history)
        }
    
    def reset(self):
        """Reset portfolio to initial state."""
        self.cash = self.initial_capital
        self.positions = {}
        self.realized_pnl = 0.0
        self.total_commission = 0.0
        self.high_water_mark = self.initial_capital
        self.trade_history = []
        self.portfolio_snapshots = []
