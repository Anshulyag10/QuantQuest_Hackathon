"""
Position - Represents a trading position in an asset

Tracks quantity, entry price, and P&L for a single position.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Position:
    """
    Represents a position in a single asset.
    """
    symbol: str
    quantity: int
    avg_entry_price: float
    current_price: float = 0.0
    
    def update_price(self, new_price: float):
        """
        Update the current market price.
        
        Args:
            new_price: New market price
        """
        self.current_price = new_price
    
    def get_market_value(self) -> float:
        """
        Get current market value of the position.
        
        Returns:
            Current market value
        """
        return self.quantity * self.current_price
    
    def get_cost_basis(self) -> float:
        """
        Get the total cost basis of the position.
        
        Returns:
            Total cost basis
        """
        return self.quantity * self.avg_entry_price
    
    def get_unrealized_pnl(self) -> float:
        """
        Get unrealized profit/loss.
        
        Returns:
            Unrealized P&L (positive = profit, negative = loss)
        """
        return self.get_market_value() - self.get_cost_basis()
    
    def get_unrealized_pnl_percent(self) -> float:
        """
        Get unrealized P&L as percentage.
        
        Returns:
            Unrealized P&L percentage
        """
        cost_basis = self.get_cost_basis()
        if cost_basis == 0:
            return 0.0
        return (self.get_unrealized_pnl() / cost_basis) * 100
    
    def add_quantity(self, quantity: int, price: float):
        """
        Add to the position (average up/down).
        
        Args:
            quantity: Quantity to add
            price: Price at which adding
        """
        total_cost = self.get_cost_basis() + (quantity * price)
        self.quantity += quantity
        self.avg_entry_price = total_cost / self.quantity if self.quantity > 0 else 0
    
    def reduce_quantity(self, quantity: int) -> float:
        """
        Reduce the position (close partial or full).
        
        Args:
            quantity: Quantity to reduce
            
        Returns:
            Realized P&L from the reduction
        """
        if quantity > self.quantity:
            quantity = self.quantity
        
        # Calculate realized P&L
        realized_pnl = quantity * (self.current_price - self.avg_entry_price)
        
        # Reduce quantity
        self.quantity -= quantity
        
        return realized_pnl
    
    def __repr__(self) -> str:
        """String representation of position."""
        return (
            f"Position({self.symbol}: {self.quantity} @ ${self.avg_entry_price:.2f}, "
            f"Current: ${self.current_price:.2f}, "
            f"Unrealized P&L: ${self.get_unrealized_pnl():.2f})"
        )
