"""
Market Data Generator - Synthetic Price Data Generation

This module generates realistic market data using various models including:
- Geometric Brownian Motion (Random Walk)
- Configurable drift and volatility
- Multiple asset simulation
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional


class MarketDataGenerator:
    """
    Generates synthetic market data for trading simulation.
    
    Uses Geometric Brownian Motion to simulate realistic price movements.
    """
    
    def __init__(
        self,
        symbols: List[str],
        initial_prices: Optional[Dict[str, float]] = None,
        drift: float = 0.0001,
        volatility: float = 0.02,
        seed: Optional[int] = None
    ):
        """
        Initialize the market data generator.
        
        Args:
            symbols: List of asset symbols to generate data for
            initial_prices: Dictionary of initial prices for each symbol
            drift: Daily drift (mu) - expected return
            volatility: Daily volatility (sigma) - standard deviation
            seed: Random seed for reproducibility
        """
        self.symbols = symbols
        self.drift = drift
        self.volatility = volatility
        
        if seed is not None:
            np.random.seed(seed)
        
        # Set initial prices
        if initial_prices is None:
            self.initial_prices = {
                symbol: np.random.uniform(50, 500) for symbol in symbols
            }
        else:
            self.initial_prices = initial_prices
    
    def generate_price_path(
        self,
        initial_price: float,
        num_steps: int,
        dt: float = 1/252  # Daily timestep (252 trading days/year)
    ) -> np.ndarray:
        """
        Generate a single price path using Geometric Brownian Motion.
        
        Formula: dS = μ*S*dt + σ*S*dW
        where dW ~ N(0, dt)
        
        Args:
            initial_price: Starting price
            num_steps: Number of time steps
            dt: Time step size (default: 1 day)
            
        Returns:
            Array of prices
        """
        prices = np.zeros(num_steps)
        prices[0] = initial_price
        
        for t in range(1, num_steps):
            # Random component (Wiener process)
            random_shock = np.random.normal(0, np.sqrt(dt))
            
            # GBM formula
            drift_component = self.drift * dt
            volatility_component = self.volatility * random_shock
            
            # Calculate next price
            prices[t] = prices[t-1] * np.exp(drift_component + volatility_component)
        
        return prices
    
    def generate_historical_data(
        self,
        days: int = 252,
        start_date: Optional[datetime] = None
    ) -> pd.DataFrame:
        """
        Generate historical market data for all symbols.
        
        Args:
            days: Number of trading days to generate
            start_date: Starting date (default: today - days)
            
        Returns:
            DataFrame with columns: [timestamp, symbol, open, high, low, close, volume]
        """
        if start_date is None:
            start_date = datetime.now() - timedelta(days=days)
        
        all_data = []
        
        for symbol in self.symbols:
            # Generate base price path
            prices = self.generate_price_path(
                self.initial_prices[symbol],
                days
            )
            
            # Generate OHLC data
            for i, close_price in enumerate(prices):
                # Add realistic intraday variation
                daily_volatility = close_price * self.volatility * 0.5
                
                open_price = close_price + np.random.normal(0, daily_volatility)
                high_price = max(open_price, close_price) + abs(np.random.normal(0, daily_volatility))
                low_price = min(open_price, close_price) - abs(np.random.normal(0, daily_volatility))
                
                # Ensure high >= low
                high_price = max(high_price, low_price)
                
                # Generate volume (log-normal distribution)
                volume = int(np.random.lognormal(15, 1.5))
                
                timestamp = start_date + timedelta(days=i)
                
                all_data.append({
                    'timestamp': timestamp,
                    'symbol': symbol,
                    'open': round(open_price, 2),
                    'high': round(high_price, 2),
                    'low': round(low_price, 2),
                    'close': round(close_price, 2),
                    'volume': volume
                })
        
        df = pd.DataFrame(all_data)
        df = df.sort_values(['timestamp', 'symbol']).reset_index(drop=True)
        
        return df
    
    def generate_streaming_data(
        self,
        initial_prices: Optional[Dict[str, float]] = None
    ) -> Dict[str, float]:
        """
        Generate a single tick of market data (streaming simulation).
        
        Args:
            initial_prices: Current prices for each symbol
            
        Returns:
            Dictionary of symbol -> new_price
        """
        if initial_prices is None:
            initial_prices = self.initial_prices
        
        new_prices = {}
        
        for symbol in self.symbols:
            current_price = initial_prices.get(symbol, self.initial_prices[symbol])
            
            # Generate single step price movement
            dt = 1/252/6.5  # Assume 6.5 hour trading day, each tick is ~1 minute
            random_shock = np.random.normal(0, np.sqrt(dt))
            
            drift_component = self.drift * dt
            volatility_component = self.volatility * random_shock
            
            new_price = current_price * np.exp(drift_component + volatility_component)
            new_prices[symbol] = round(new_price, 2)
        
        return new_prices
    
    def add_market_events(
        self,
        data: pd.DataFrame,
        event_probability: float = 0.05,
        event_magnitude: float = 0.1
    ) -> pd.DataFrame:
        """
        Add random market events (crashes, rallies) to the data.
        
        Args:
            data: DataFrame of market data
            event_probability: Probability of event on any given day
            event_magnitude: Magnitude of price movement during event
            
        Returns:
            Modified DataFrame with market events
        """
        data = data.copy()
        
        for symbol in self.symbols:
            symbol_mask = data['symbol'] == symbol
            symbol_data = data[symbol_mask].copy()
            
            for idx in symbol_data.index:
                if np.random.random() < event_probability:
                    # Random event (50% crash, 50% rally)
                    direction = 1 if np.random.random() > 0.5 else -1
                    shock = direction * event_magnitude
                    
                    # Apply shock to all prices
                    for col in ['open', 'high', 'low', 'close']:
                        data.loc[idx, col] *= (1 + shock)
        
        return data


class MarketSimulator:
    """
    Simulates market conditions and feeds data to the trading engine.
    """
    
    def __init__(self, market_data: pd.DataFrame):
        """
        Initialize the market simulator.
        
        Args:
            market_data: DataFrame containing historical market data
        """
        self.market_data = market_data
        self.current_index = 0
        self.timestamps = sorted(market_data['timestamp'].unique())
    
    def get_current_prices(self) -> Dict[str, float]:
        """
        Get current market prices for all symbols.
        
        Returns:
            Dictionary of symbol -> current_price
        """
        if self.current_index >= len(self.timestamps):
            return {}
        
        current_time = self.timestamps[self.current_index]
        current_data = self.market_data[
            self.market_data['timestamp'] == current_time
        ]
        
        return dict(zip(current_data['symbol'], current_data['close']))
    
    def get_current_data(self) -> pd.DataFrame:
        """
        Get current market data for all symbols.
        
        Returns:
            DataFrame of current market data
        """
        if self.current_index >= len(self.timestamps):
            return pd.DataFrame()
        
        current_time = self.timestamps[self.current_index]
        return self.market_data[self.market_data['timestamp'] == current_time]
    
    def get_historical_data(self, lookback: int = 50) -> pd.DataFrame:
        """
        Get historical market data up to current point.
        
        Args:
            lookback: Number of periods to look back
            
        Returns:
            DataFrame of historical market data
        """
        end_idx = min(self.current_index + 1, len(self.timestamps))
        start_idx = max(0, end_idx - lookback)
        
        historical_times = self.timestamps[start_idx:end_idx]
        
        return self.market_data[
            self.market_data['timestamp'].isin(historical_times)
        ]
    
    def step(self) -> bool:
        """
        Advance to next time step.
        
        Returns:
            True if more data available, False if end reached
        """
        self.current_index += 1
        return self.current_index < len(self.timestamps)
    
    def reset(self):
        """Reset simulator to beginning."""
        self.current_index = 0
    
    def is_complete(self) -> bool:
        """Check if simulation is complete."""
        return self.current_index >= len(self.timestamps)
