"""
Unit Tests for Trading Engine

Tests core functionality of the trading platform.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
import pandas as pd
from datetime import datetime, timedelta

from src.market_data.data_generator import MarketDataGenerator, MarketSimulator
from src.trading.order import Order, OrderType, OrderSide, OrderExecutor
from src.trading.strategies.moving_average import MovingAverageStrategy
from src.trading.strategies.momentum import MomentumStrategy
from src.portfolio.portfolio_manager import PortfolioManager
from src.portfolio.position import Position


class TestMarketDataGenerator(unittest.TestCase):
    """Test market data generation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.symbols = ['TEST1', 'TEST2']
        self.generator = MarketDataGenerator(
            symbols=self.symbols,
            seed=42
        )
    
    def test_generate_historical_data(self):
        """Test historical data generation."""
        data = self.generator.generate_historical_data(days=10)
        
        self.assertIsInstance(data, pd.DataFrame)
        self.assertGreater(len(data), 0)
        
        # Check columns
        required_cols = ['timestamp', 'symbol', 'open', 'high', 'low', 'close', 'volume']
        for col in required_cols:
            self.assertIn(col, data.columns)
        
        # Check symbols
        self.assertEqual(set(data['symbol'].unique()), set(self.symbols))
    
    def test_price_sanity(self):
        """Test that generated prices are sane."""
        data = self.generator.generate_historical_data(days=5)
        
        for _, row in data.iterrows():
            # High should be >= Low
            self.assertGreaterEqual(row['high'], row['low'])
            
            # Open and Close should be between High and Low
            self.assertGreaterEqual(row['high'], row['open'])
            self.assertGreaterEqual(row['high'], row['close'])
            self.assertLessEqual(row['low'], row['open'])
            self.assertLessEqual(row['low'], row['close'])
            
            # All prices should be positive
            self.assertGreater(row['open'], 0)
            self.assertGreater(row['high'], 0)
            self.assertGreater(row['low'], 0)
            self.assertGreater(row['close'], 0)


class TestPosition(unittest.TestCase):
    """Test position management."""
    
    def test_create_position(self):
        """Test position creation."""
        pos = Position(symbol='TEST', quantity=100, avg_entry_price=50.0, current_price=50.0)
        
        self.assertEqual(pos.symbol, 'TEST')
        self.assertEqual(pos.quantity, 100)
        self.assertEqual(pos.avg_entry_price, 50.0)
    
    def test_unrealized_pnl(self):
        """Test unrealized P&L calculation."""
        pos = Position(symbol='TEST', quantity=100, avg_entry_price=50.0, current_price=55.0)
        
        # Expected: (55 - 50) * 100 = 500
        self.assertEqual(pos.get_unrealized_pnl(), 500.0)
    
    def test_add_quantity(self):
        """Test adding to position (averaging)."""
        pos = Position(symbol='TEST', quantity=100, avg_entry_price=50.0, current_price=50.0)
        
        # Add 100 shares at $60
        pos.add_quantity(100, 60.0)
        
        self.assertEqual(pos.quantity, 200)
        # Average should be (100*50 + 100*60) / 200 = 55
        self.assertEqual(pos.avg_entry_price, 55.0)
    
    def test_reduce_quantity(self):
        """Test reducing position."""
        pos = Position(symbol='TEST', quantity=100, avg_entry_price=50.0, current_price=55.0)
        
        # Sell 50 shares
        realized_pnl = pos.reduce_quantity(50)
        
        self.assertEqual(pos.quantity, 50)
        # Realized P&L: 50 * (55 - 50) = 250
        self.assertEqual(realized_pnl, 250.0)


class TestPortfolioManager(unittest.TestCase):
    """Test portfolio management."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.portfolio = PortfolioManager(initial_capital=100000)
    
    def test_initial_state(self):
        """Test initial portfolio state."""
        self.assertEqual(self.portfolio.cash, 100000)
        self.assertEqual(len(self.portfolio.positions), 0)
        self.assertEqual(self.portfolio.realized_pnl, 0)
    
    def test_buy_asset(self):
        """Test buying an asset."""
        self.portfolio.buy('TEST', 100, 50.0, commission=5.0)
        
        # Cash should be reduced by cost + commission
        expected_cash = 100000 - (100 * 50.0) - 5.0
        self.assertEqual(self.portfolio.cash, expected_cash)
        
        # Should have position
        self.assertIn('TEST', self.portfolio.positions)
        self.assertEqual(self.portfolio.positions['TEST'].quantity, 100)
    
    def test_sell_asset(self):
        """Test selling an asset."""
        # Buy first
        self.portfolio.buy('TEST', 100, 50.0, commission=5.0)
        
        # Update price and sell
        self.portfolio.update_prices({'TEST': 60.0})
        initial_cash = self.portfolio.cash
        
        self.portfolio.sell('TEST', 100, 60.0, commission=5.0)
        
        # Cash should increase by proceeds - commission
        expected_cash = initial_cash + (100 * 60.0) - 5.0
        self.assertEqual(self.portfolio.cash, expected_cash)
        
        # Position should be closed
        self.assertNotIn('TEST', self.portfolio.positions)
        
        # Realized P&L: (60 - 50) * 100 = 1000
        self.assertEqual(self.portfolio.realized_pnl, 1000.0)
    
    def test_insufficient_cash(self):
        """Test buying with insufficient cash."""
        with self.assertRaises(ValueError):
            self.portfolio.buy('TEST', 10000, 50.0)
    
    def test_insufficient_quantity(self):
        """Test selling more than owned."""
        self.portfolio.buy('TEST', 100, 50.0)
        
        with self.assertRaises(ValueError):
            self.portfolio.sell('TEST', 200, 60.0)


class TestOrderExecution(unittest.TestCase):
    """Test order execution."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.executor = OrderExecutor(commission=0.001)
    
    def test_market_order_buy(self):
        """Test market buy order execution."""
        order = Order(
            symbol='TEST',
            side=OrderSide.BUY,
            quantity=100,
            order_type=OrderType.MARKET
        )
        
        executed, price, commission = self.executor.execute_order(order, 50.0)
        
        self.assertTrue(executed)
        self.assertEqual(price, 50.0)
        self.assertTrue(order.is_filled())
    
    def test_limit_order_buy(self):
        """Test limit buy order execution."""
        order = Order(
            symbol='TEST',
            side=OrderSide.BUY,
            quantity=100,
            order_type=OrderType.LIMIT,
            price=50.0
        )
        
        # Should execute when market price <= limit price
        executed, _, _ = self.executor.execute_order(order, 49.0)
        self.assertTrue(executed)
        
        # Should not execute when market price > limit price
        order2 = Order(
            symbol='TEST',
            side=OrderSide.BUY,
            quantity=100,
            order_type=OrderType.LIMIT,
            price=50.0
        )
        executed, _, _ = self.executor.execute_order(order2, 51.0)
        self.assertFalse(executed)


class TestMovingAverageStrategy(unittest.TestCase):
    """Test moving average strategy."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.strategy = MovingAverageStrategy(short_window=5, long_window=10)
    
    def test_strategy_initialization(self):
        """Test strategy initialization."""
        self.assertEqual(self.strategy.short_window, 5)
        self.assertEqual(self.strategy.long_window, 10)
    
    def test_signal_generation(self):
        """Test signal generation."""
        # Create mock data with upward trend
        dates = pd.date_range(start='2024-01-01', periods=20, freq='D')
        data = []
        
        for i, date in enumerate(dates):
            # Create upward trending prices
            price = 100 + i * 2
            data.append({
                'timestamp': date,
                'symbol': 'TEST',
                'open': price,
                'high': price + 1,
                'low': price - 1,
                'close': price,
                'volume': 1000000
            })
        
        df = pd.DataFrame(data)
        
        signals = self.strategy.generate_signals(df)
        
        # Should generate signals for TEST symbol
        self.assertIn('TEST', signals)
        self.assertIn(signals['TEST'], [-1, 0, 1])


class TestMomentumStrategy(unittest.TestCase):
    """Test momentum strategy."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.strategy = MomentumStrategy(lookback_period=10, threshold=0.05)
    
    def test_strategy_initialization(self):
        """Test strategy initialization."""
        self.assertEqual(self.strategy.momentum_period, 10)
        self.assertEqual(self.strategy.threshold, 0.05)


class TestMarketSimulator(unittest.TestCase):
    """Test market simulator."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create sample data
        data_gen = MarketDataGenerator(symbols=['TEST'], seed=42)
        self.market_data = data_gen.generate_historical_data(days=5)
        self.simulator = MarketSimulator(self.market_data)
    
    def test_initialization(self):
        """Test simulator initialization."""
        self.assertEqual(self.simulator.current_index, 0)
        self.assertFalse(self.simulator.is_complete())
    
    def test_step(self):
        """Test stepping through simulation."""
        initial_index = self.simulator.current_index
        self.simulator.step()
        self.assertEqual(self.simulator.current_index, initial_index + 1)
    
    def test_get_current_prices(self):
        """Test getting current prices."""
        prices = self.simulator.get_current_prices()
        self.assertIsInstance(prices, dict)
        self.assertIn('TEST', prices)


def run_tests():
    """Run all tests."""
    unittest.main(argv=[''], verbosity=2, exit=False)


if __name__ == '__main__':
    print("\n" + "="*80)
    print(" " * 25 + "RUNNING UNIT TESTS")
    print("="*80 + "\n")
    
    run_tests()
    
    print("\n" + "="*80)
    print(" " * 25 + "TESTS COMPLETE")
    print("="*80 + "\n")
