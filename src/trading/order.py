"""
Order Management System

Defines order types and execution logic for the trading platform.
"""

from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


class OrderType(Enum):
    """Types of orders supported."""
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"


class OrderSide(Enum):
    """Order side - buy or sell."""
    BUY = "BUY"
    SELL = "SELL"


class OrderStatus(Enum):
    """Order execution status."""
    PENDING = "PENDING"
    FILLED = "FILLED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"


@dataclass
class Order:
    """
    Represents a trading order.
    """
    symbol: str
    side: OrderSide
    quantity: int
    order_type: OrderType
    price: Optional[float] = None  # For limit/stop orders
    timestamp: datetime = None
    order_id: str = None
    status: OrderStatus = OrderStatus.PENDING
    filled_quantity: int = 0
    filled_price: float = 0.0
    
    def __post_init__(self):
        """Initialize order with timestamp and ID if not provided."""
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.order_id is None:
            self.order_id = f"{self.symbol}_{self.timestamp.strftime('%Y%m%d%H%M%S%f')}"
    
    def fill(self, quantity: int, price: float):
        """
        Fill the order (partial or complete).
        
        Args:
            quantity: Quantity filled
            price: Execution price
        """
        self.filled_quantity += quantity
        self.filled_price = price
        
        if self.filled_quantity >= self.quantity:
            self.status = OrderStatus.FILLED
        elif self.filled_quantity > 0:
            self.status = OrderStatus.PARTIALLY_FILLED
    
    def cancel(self):
        """Cancel the order."""
        self.status = OrderStatus.CANCELLED
    
    def reject(self):
        """Reject the order."""
        self.status = OrderStatus.REJECTED
    
    def is_filled(self) -> bool:
        """Check if order is completely filled."""
        return self.status == OrderStatus.FILLED
    
    def __repr__(self) -> str:
        """String representation of order."""
        return (
            f"Order(id={self.order_id}, {self.side.value} {self.quantity} {self.symbol} "
            f"@ {self.price if self.price else 'MARKET'}, status={self.status.value})"
        )


class OrderExecutor:
    """
    Executes orders against market data.
    """
    
    def __init__(self, commission: float = 0.001):
        """
        Initialize order executor.
        
        Args:
            commission: Commission rate (default 0.1%)
        """
        self.commission = commission
    
    def execute_order(
        self,
        order: Order,
        current_price: float
    ) -> tuple[bool, float, float]:
        """
        Attempt to execute an order at current market price.
        
        Args:
            order: Order to execute
            current_price: Current market price
            
        Returns:
            Tuple of (executed, execution_price, commission)
        """
        executed = False
        execution_price = 0.0
        commission = 0.0
        
        # Check if order can be executed
        if order.order_type == OrderType.MARKET:
            executed = True
            execution_price = current_price
        
        elif order.order_type == OrderType.LIMIT:
            if order.side == OrderSide.BUY and current_price <= order.price:
                executed = True
                execution_price = order.price
            elif order.side == OrderSide.SELL and current_price >= order.price:
                executed = True
                execution_price = order.price
        
        elif order.order_type == OrderType.STOP:
            if order.side == OrderSide.BUY and current_price >= order.price:
                executed = True
                execution_price = current_price
            elif order.side == OrderSide.SELL and current_price <= order.price:
                executed = True
                execution_price = current_price
        
        # Calculate commission if executed
        if executed:
            order.fill(order.quantity, execution_price)
            commission = execution_price * order.quantity * self.commission
        
        return executed, execution_price, commission
