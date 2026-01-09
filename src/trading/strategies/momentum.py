"""
Momentum Strategy

Buys assets with positive momentum and sells assets with negative momentum.
"""

import pandas as pd
import numpy as np
from typing import Dict
from .base_strategy import BaseStrategy


class MomentumStrategy(BaseStrategy):
    """
    Momentum Trading Strategy.
    
    This strategy calculates price momentum over a lookback period:
    - Positive momentum (price trending up) -> Buy signal
    - Negative momentum (price trending down) -> Sell signal
    
    Momentum is calculated as the rate of change in price.
    """
    
    def __init__(
        self,
        lookback_period: int = 20,
        threshold: float = 0.02
    ):
        """
        Initialize the momentum strategy.
        
        Args:
            lookback_period: Period to calculate momentum
            threshold: Minimum momentum threshold to trigger signals (e.g., 0.02 = 2%)
        """
        super().__init__(lookback_period=lookback_period + 5)
        self.momentum_period = lookback_period
        self.threshold = threshold
    
    def calculate_momentum(self, data: pd.DataFrame) -> float:
        """
        Calculate momentum for a price series.
        
        Momentum = (Current Price - Price N periods ago) / Price N periods ago
        
        Args:
            data: Price data
            
        Returns:
            Momentum value
        """
        if len(data) < self.momentum_period + 1:
            return 0.0
        
        current_price = data['close'].iloc[-1]
        past_price = data['close'].iloc[-self.momentum_period - 1]
        
        if past_price == 0:
            return 0.0
        
        momentum = (current_price - past_price) / past_price
        
        return momentum
    
    def calculate_rsi(self, data: pd.DataFrame, period: int = 14) -> float:
        """
        Calculate Relative Strength Index (RSI).
        
        RSI measures momentum by comparing upward and downward price movements.
        
        Args:
            data: Price data
            period: RSI period (default 14)
            
        Returns:
            RSI value (0-100)
        """
        if len(data) < period + 1:
            return 50.0  # Neutral
        
        # Calculate price changes
        delta = data['close'].diff()
        
        # Separate gains and losses
        gains = delta.where(delta > 0, 0)
        losses = -delta.where(delta < 0, 0)
        
        # Calculate average gains and losses
        avg_gain = gains.rolling(window=period).mean()
        avg_loss = losses.rolling(window=period).mean()
        
        # Calculate RS and RSI
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 50.0
    
    def generate_signals(self, market_data: pd.DataFrame) -> Dict[str, int]:
        """
        Generate trading signals based on momentum.
        
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
            
            if len(symbol_data) < self.momentum_period + 1:
                signals[symbol] = 0
                continue
            
            # Calculate momentum
            momentum = self.calculate_momentum(symbol_data)
            
            # Optional: Calculate RSI for additional confirmation
            rsi = self.calculate_rsi(symbol_data)
            
            # Generate signal based on momentum
            signal = 0
            
            # Strong positive momentum -> Buy
            if momentum > self.threshold and rsi < 70:  # Not overbought
                signal = 1
            
            # Strong negative momentum -> Sell
            elif momentum < -self.threshold or rsi > 70:  # Negative momentum or overbought
                signal = -1
            
            # Weak momentum -> Hold
            else:
                signal = 0
            
            signals[symbol] = signal
        
        return signals
    
    def __str__(self) -> str:
        """String representation of the strategy."""
        return f"MomentumStrategy(period={self.momentum_period}, threshold={self.threshold})"


class MeanReversionStrategy(BaseStrategy):
    """
    Mean Reversion Strategy.
    
    This strategy assumes prices revert to their mean:
    - Price significantly below mean -> Buy signal (expect reversion up)
    - Price significantly above mean -> Sell signal (expect reversion down)
    """
    
    def __init__(
        self,
        lookback_period: int = 20,
        std_threshold: float = 2.0
    ):
        """
        Initialize mean reversion strategy.
        
        Args:
            lookback_period: Period to calculate mean and std
            std_threshold: Number of standard deviations from mean to trigger signal
        """
        super().__init__(lookback_period=lookback_period + 5)
        self.mean_period = lookback_period
        self.std_threshold = std_threshold
    
    def generate_signals(self, market_data: pd.DataFrame) -> Dict[str, int]:
        """
        Generate trading signals based on mean reversion.
        
        Args:
            market_data: DataFrame containing market data
            
        Returns:
            Dictionary of symbol -> signal
        """
        signals = {}
        
        if not self.validate_data(market_data):
            return signals
        
        symbols = market_data['symbol'].unique()
        
        for symbol in symbols:
            symbol_data = self.get_latest_data(market_data, symbol)
            
            if len(symbol_data) < self.mean_period:
                signals[symbol] = 0
                continue
            
            # Calculate mean and standard deviation
            prices = symbol_data['close']
            mean_price = prices.mean()
            std_price = prices.std()
            current_price = prices.iloc[-1]
            
            if std_price == 0:
                signals[symbol] = 0
                continue
            
            # Calculate z-score (number of std deviations from mean)
            z_score = (current_price - mean_price) / std_price
            
            signal = 0
            
            # Price is far below mean -> Buy (expect reversion up)
            if z_score < -self.std_threshold:
                signal = 1
            
            # Price is far above mean -> Sell (expect reversion down)
            elif z_score > self.std_threshold:
                signal = -1
            
            signals[symbol] = signal
        
        return signals
    
    def __str__(self) -> str:
        """String representation of the strategy."""
        return f"MeanReversionStrategy(period={self.mean_period}, threshold={self.std_threshold})"
