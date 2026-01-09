"""
Base Strategy Class

Abstract base class for all trading strategies.
"""

from abc import ABC, abstractmethod
import pandas as pd
from typing import Dict


class BaseStrategy(ABC):
    """
    Abstract base class for trading strategies.
    
    All strategies must implement the generate_signals method.
    """
    
    def __init__(self, lookback_period: int = 50):
        """
        Initialize the strategy.
        
        Args:
            lookback_period: Number of periods to look back for calculations
        """
        self.lookback_period = lookback_period
    
    @abstractmethod
    def generate_signals(self, market_data: pd.DataFrame) -> Dict[str, int]:
        """
        Generate trading signals based on market data.
        
        Args:
            market_data: DataFrame containing market data with columns:
                        [timestamp, symbol, open, high, low, close, volume]
        
        Returns:
            Dictionary mapping symbol to signal:
                1: Buy signal
                0: Hold/No signal
                -1: Sell signal
        """
        pass
    
    def validate_data(self, market_data: pd.DataFrame) -> bool:
        """
        Validate that market data has sufficient history.
        
        Args:
            market_data: Market data DataFrame
            
        Returns:
            True if data is valid, False otherwise
        """
        if market_data.empty:
            return False
        
        # Check each symbol has enough data
        for symbol in market_data['symbol'].unique():
            symbol_data = market_data[market_data['symbol'] == symbol]
            if len(symbol_data) < self.lookback_period:
                return False
        
        return True
    
    def get_latest_data(
        self,
        market_data: pd.DataFrame,
        symbol: str
    ) -> pd.DataFrame:
        """
        Get latest data for a specific symbol.
        
        Args:
            market_data: Complete market data
            symbol: Symbol to filter
            
        Returns:
            DataFrame containing data for the symbol
        """
        symbol_data = market_data[market_data['symbol'] == symbol].copy()
        symbol_data = symbol_data.sort_values('timestamp')
        return symbol_data.tail(self.lookback_period)
