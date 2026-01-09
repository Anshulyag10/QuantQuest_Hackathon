"""
Moving Average Crossover Strategy

Generates buy signals when short-term MA crosses above long-term MA.
Generates sell signals when short-term MA crosses below long-term MA.
"""

import pandas as pd
from typing import Dict
from .base_strategy import BaseStrategy


class MovingAverageStrategy(BaseStrategy):
    """
    Moving Average Crossover Strategy.
    
    This classic strategy uses two moving averages:
    - Short-term MA (fast)
    - Long-term MA (slow)
    
    Buy when short MA crosses above long MA (golden cross)
    Sell when short MA crosses below long MA (death cross)
    """
    
    def __init__(
        self,
        short_window: int = 20,
        long_window: int = 50
    ):
        """
        Initialize the moving average strategy.
        
        Args:
            short_window: Short-term moving average period
            long_window: Long-term moving average period
        """
        super().__init__(lookback_period=long_window + 5)
        self.short_window = short_window
        self.long_window = long_window
        
        # Track previous signals to detect crossovers
        self.previous_signals = {}
    
    def calculate_moving_averages(
        self,
        data: pd.DataFrame
    ) -> tuple[pd.Series, pd.Series]:
        """
        Calculate short and long moving averages.
        
        Args:
            data: Price data
            
        Returns:
            Tuple of (short_ma, long_ma)
        """
        short_ma = data['close'].rolling(window=self.short_window).mean()
        long_ma = data['close'].rolling(window=self.long_window).mean()
        
        return short_ma, long_ma
    
    def generate_signals(self, market_data: pd.DataFrame) -> Dict[str, int]:
        """
        Generate trading signals based on moving average crossover.
        
        Args:
            market_data: DataFrame containing market data
            
        Returns:
            Dictionary of symbol -> signal
        """
        signals = {}
        
        if not self.validate_data(market_data):
            return signals
        
        # Generate signals for each symbol
        symbols = market_data['symbol'].unique()
        
        for symbol in symbols:
            symbol_data = self.get_latest_data(market_data, symbol)
            
            if len(symbol_data) < self.long_window:
                signals[symbol] = 0
                continue
            
            # Calculate moving averages
            short_ma, long_ma = self.calculate_moving_averages(symbol_data)
            
            # Get current and previous values
            current_short = short_ma.iloc[-1]
            current_long = long_ma.iloc[-1]
            
            if len(short_ma) > 1:
                prev_short = short_ma.iloc[-2]
                prev_long = long_ma.iloc[-2]
            else:
                signals[symbol] = 0
                continue
            
            # Check for crossover
            signal = 0
            
            # Golden Cross: short MA crosses above long MA
            if prev_short <= prev_long and current_short > current_long:
                signal = 1  # Buy signal
            
            # Death Cross: short MA crosses below long MA
            elif prev_short >= prev_long and current_short < current_long:
                signal = -1  # Sell signal
            
            # Hold if already in position and trend continues
            elif symbol in self.previous_signals:
                prev_signal = self.previous_signals[symbol]
                
                # Continue holding buy position if short MA still above long MA
                if prev_signal == 1 and current_short > current_long:
                    signal = 0  # Hold
                
                # Continue holding short/out if short MA still below long MA
                elif prev_signal == -1 and current_short < current_long:
                    signal = 0  # Hold
            
            signals[symbol] = signal
            self.previous_signals[symbol] = signal
        
        return signals
    
    def __str__(self) -> str:
        """String representation of the strategy."""
        return f"MovingAverageStrategy(short={self.short_window}, long={self.long_window})"
