"""
Market Data Generator - Synthetic Price Data Generation

This module generates realistic market data using various models including:
- Geometric Brownian Motion (Random Walk)
- Jump Diffusion (Merton Model)
- Regime Switching
- Volatility Clustering (GARCH-like)
- Configurable drift and volatility
- Multiple asset simulation
- Real-time streaming capability
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Generator
from enum import Enum


class MarketRegime(Enum):
    """Market regime states for regime-switching model."""
    BULL = "bull"
    BEAR = "bear"
    SIDEWAYS = "sideways"
    HIGH_VOLATILITY = "high_volatility"


class MarketDataGenerator:
    """
    Generates synthetic market data for trading simulation.
    
    Uses advanced models to simulate realistic price movements:
    - Geometric Brownian Motion (GBM) as base
    - Optional jump diffusion for sudden moves
    - Optional volatility clustering
    - Optional regime switching
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
        self.seed = seed
        
        if seed is not None:
            np.random.seed(seed)
        
        # Set initial prices
        if initial_prices is None:
            self.initial_prices = {
                symbol: np.random.uniform(50, 500) for symbol in symbols
            }
        else:
            self.initial_prices = initial_prices
        
        # Current prices for streaming
        self.current_prices = self.initial_prices.copy()
        
        # Regime state
        self.current_regime = MarketRegime.SIDEWAYS
        
    def generate_price_path(
        self,
        initial_price: float,
        num_steps: int,
        dt: float = 1/252,  # Daily timestep (252 trading days/year)
        include_jumps: bool = False,
        jump_intensity: float = 0.02,
        jump_size_mean: float = 0.0,
        jump_size_std: float = 0.03
    ) -> np.ndarray:
        """
        Generate a single price path using Geometric Brownian Motion.
        
        Formula: dS = μ*S*dt + σ*S*dW + J*S*dN
        where dW ~ N(0, dt), dN ~ Poisson(λ*dt), J ~ N(μ_J, σ_J)
        
        Args:
            initial_price: Starting price
            num_steps: Number of time steps
            dt: Time step size (default: 1 day)
            include_jumps: Whether to include jump diffusion
            jump_intensity: Poisson intensity for jumps
            jump_size_mean: Mean of jump size distribution
            jump_size_std: Std of jump size distribution
            
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
            
            # Jump component (Merton model)
            jump_component = 0
            if include_jumps:
                # Poisson process for jump occurrence
                if np.random.random() < jump_intensity:
                    jump_component = np.random.normal(jump_size_mean, jump_size_std)
            
            # Calculate next price
            prices[t] = prices[t-1] * np.exp(
                drift_component + volatility_component + jump_component
            )
        
        return prices
    
    def generate_price_path_with_volatility_clustering(
        self,
        initial_price: float,
        num_steps: int,
        dt: float = 1/252,
        alpha: float = 0.1,
        beta: float = 0.85,
        omega: float = 0.00001
    ) -> tuple:
        """
        Generate price path with GARCH(1,1)-like volatility clustering.
        
        σ²_t = ω + α*ε²_{t-1} + β*σ²_{t-1}
        
        Args:
            initial_price: Starting price
            num_steps: Number of time steps
            dt: Time step size
            alpha: GARCH alpha parameter
            beta: GARCH beta parameter
            omega: GARCH omega (long-run variance)
            
        Returns:
            Tuple of (prices, volatilities)
        """
        prices = np.zeros(num_steps)
        volatilities = np.zeros(num_steps)
        
        prices[0] = initial_price
        volatilities[0] = self.volatility ** 2
        
        prev_epsilon = 0
        
        for t in range(1, num_steps):
            # Update volatility (GARCH-like)
            volatilities[t] = omega + alpha * prev_epsilon**2 + beta * volatilities[t-1]
            current_vol = np.sqrt(volatilities[t])
            
            # Random shock
            epsilon = np.random.normal(0, 1)
            prev_epsilon = epsilon * current_vol
            
            # Price update
            drift_component = self.drift * dt
            volatility_component = current_vol * np.sqrt(dt) * epsilon
            
            prices[t] = prices[t-1] * np.exp(drift_component + volatility_component)
        
        return prices, np.sqrt(volatilities)
    
    def generate_historical_data(
        self,
        days: int = 252,
        start_date: Optional[datetime] = None,
        include_jumps: bool = True,
        volatility_clustering: bool = True
    ) -> pd.DataFrame:
        """
        Generate historical market data for all symbols.
        
        Args:
            days: Number of trading days to generate
            start_date: Starting date (default: today - days)
            include_jumps: Include jump diffusion in price generation
            volatility_clustering: Include GARCH-like volatility clustering
            
        Returns:
            DataFrame with columns: [timestamp, symbol, open, high, low, close, volume]
        """
        if start_date is None:
            start_date = datetime.now() - timedelta(days=days)
        
        all_data = []
        
        for symbol in self.symbols:
            # Generate base price path
            if volatility_clustering:
                prices, _ = self.generate_price_path_with_volatility_clustering(
                    self.initial_prices[symbol],
                    days
                )
            else:
                prices = self.generate_price_path(
                    self.initial_prices[symbol],
                    days,
                    include_jumps=include_jumps
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
                
                # Generate volume (log-normal distribution with regime adjustment)
                base_volume = np.random.lognormal(15, 1.5)
                # Higher volume on bigger price moves
                price_move = abs(close_price - open_price) / open_price if i > 0 else 0
                volume_multiplier = 1 + (price_move * 10)
                volume = int(base_volume * volume_multiplier)
                
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
            initial_prices = self.current_prices
        
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
        
        self.current_prices = new_prices
        return new_prices
    
    def stream_prices(
        self,
        num_ticks: int = 100,
        tick_delay: float = 0.0
    ) -> Generator[Dict[str, float], None, None]:
        """
        Generator that yields streaming price data.
        
        Args:
            num_ticks: Number of ticks to generate
            tick_delay: Delay between ticks (seconds), for simulation
            
        Yields:
            Dictionary of symbol -> price for each tick
        """
        import time
        
        for _ in range(num_ticks):
            yield self.generate_streaming_data()
            if tick_delay > 0:
                time.sleep(tick_delay)
    
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
    
    def generate_correlated_data(
        self,
        days: int = 252,
        correlation_matrix: Optional[np.ndarray] = None
    ) -> pd.DataFrame:
        """
        Generate correlated price data across multiple assets.
        
        Args:
            days: Number of trading days
            correlation_matrix: Correlation matrix for assets
            
        Returns:
            DataFrame with correlated price movements
        """
        n_symbols = len(self.symbols)
        
        # Default correlation matrix (positive correlations like real markets)
        if correlation_matrix is None:
            correlation_matrix = np.ones((n_symbols, n_symbols)) * 0.5
            np.fill_diagonal(correlation_matrix, 1.0)
        
        # Cholesky decomposition for correlated random numbers
        cholesky = np.linalg.cholesky(correlation_matrix)
        
        # Generate correlated returns
        uncorrelated_returns = np.random.normal(0, 1, (days, n_symbols))
        correlated_returns = uncorrelated_returns @ cholesky.T
        
        all_data = []
        
        for i, symbol in enumerate(self.symbols):
            price = self.initial_prices[symbol]
            prices = [price]
            
            for day in range(1, days):
                ret = self.drift + self.volatility * correlated_returns[day, i]
                price = price * np.exp(ret)
                prices.append(price)
            
            # Generate OHLC from prices
            start_date = datetime.now() - timedelta(days=days)
            
            for day, close_price in enumerate(prices):
                daily_vol = close_price * self.volatility * 0.5
                open_price = close_price + np.random.normal(0, daily_vol)
                high_price = max(open_price, close_price) + abs(np.random.normal(0, daily_vol))
                low_price = min(open_price, close_price) - abs(np.random.normal(0, daily_vol))
                
                all_data.append({
                    'timestamp': start_date + timedelta(days=day),
                    'symbol': symbol,
                    'open': round(open_price, 2),
                    'high': round(high_price, 2),
                    'low': round(low_price, 2),
                    'close': round(close_price, 2),
                    'volume': int(np.random.lognormal(15, 1.5))
                })
        
        df = pd.DataFrame(all_data)
        return df.sort_values(['timestamp', 'symbol']).reset_index(drop=True)


class MarketSimulator:
    """
    Simulates market conditions and feeds data to the trading engine.
    
    Supports both batch and streaming modes.
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
    
    def get_current_ohlcv(self) -> Dict[str, Dict]:
        """
        Get current OHLCV data for all symbols.
        
        Returns:
            Dictionary of symbol -> {open, high, low, close, volume}
        """
        if self.current_index >= len(self.timestamps):
            return {}
        
        current_time = self.timestamps[self.current_index]
        current_data = self.market_data[
            self.market_data['timestamp'] == current_time
        ]
        
        result = {}
        for _, row in current_data.iterrows():
            result[row['symbol']] = {
                'open': row['open'],
                'high': row['high'],
                'low': row['low'],
                'close': row['close'],
                'volume': row['volume']
            }
        
        return result
    
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
    
    def get_progress(self) -> float:
        """Get simulation progress as percentage."""
        if len(self.timestamps) == 0:
            return 100.0
        return (self.current_index / len(self.timestamps)) * 100
    
    def get_current_timestamp(self) -> Optional[datetime]:
        """Get current timestamp."""
        if self.current_index < len(self.timestamps):
            return self.timestamps[self.current_index]
        return None
