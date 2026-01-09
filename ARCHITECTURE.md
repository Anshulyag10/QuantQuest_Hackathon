# QuantQuest - System Architecture

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     QuantQuest Trading Platform                  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                        1. DATA LAYER                             │
├─────────────────────────────────────────────────────────────────┤
│  MarketDataGenerator                                             │
│  ├── Geometric Brownian Motion                                   │
│  ├── Random Walk Simulation                                      │
│  ├── OHLC Data Generation                                        │
│  └── Market Events (Crashes/Rallies)                            │
│                                                                  │
│  MarketSimulator                                                 │
│  ├── Data Streaming                                              │
│  ├── Historical Data Access                                      │
│  └── Time Step Management                                        │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      2. STRATEGY LAYER                           │
├─────────────────────────────────────────────────────────────────┤
│  BaseStrategy (Abstract)                                         │
│  ├── Moving Average Strategy                                     │
│  │   └── Golden/Death Cross Detection                           │
│  ├── Momentum Strategy                                           │
│  │   └── Price Momentum + RSI                                   │
│  └── Mean Reversion Strategy                                     │
│      └── Z-Score Based Signals                                  │
│                                                                  │
│  Signal Output: {symbol: signal}                                │
│  where signal ∈ {-1 (sell), 0 (hold), 1 (buy)}                 │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                     3. TRADING ENGINE LAYER                      │
├─────────────────────────────────────────────────────────────────┤
│  TradingEngine                                                   │
│  ├── Signal Processing                                           │
│  ├── Position Sizing                                             │
│  ├── Order Generation                                            │
│  └── Execution Management                                        │
│                                                                  │
│  Order Types                                                     │
│  ├── Market Orders                                               │
│  ├── Limit Orders                                                │
│  └── Stop Orders                                                 │
│                                                                  │
│  OrderExecutor                                                   │
│  ├── Order Validation                                            │
│  ├── Price Matching                                              │
│  └── Commission Calculation                                      │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    4. PORTFOLIO LAYER                            │
├─────────────────────────────────────────────────────────────────┤
│  PortfolioManager                                                │
│  ├── Cash Management                                             │
│  ├── Position Tracking                                           │
│  ├── P&L Calculation                                             │
│  └── Risk Monitoring                                             │
│                                                                  │
│  Position                                                        │
│  ├── Quantity Tracking                                           │
│  ├── Average Entry Price                                         │
│  ├── Unrealized P&L                                              │
│  └── Market Value                                                │
│                                                                  │
│  Trade History                                                   │
│  ├── Realized P&L Log                                            │
│  ├── Commission Tracking                                         │
│  └── Trade Timestamps                                            │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                     5. ANALYTICS LAYER                           │
├─────────────────────────────────────────────────────────────────┤
│  Performance Metrics                                             │
│  ├── Total Return                                                │
│  ├── Sharpe Ratio                                                │
│  ├── Sortino Ratio                                               │
│  ├── Maximum Drawdown                                            │
│  ├── Calmar Ratio                                                │
│  ├── Value at Risk (VaR)                                         │
│  ├── Win Rate                                                    │
│  └── Profit Factor                                               │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow

```
Market Data → Strategy → Signals → Trading Engine → Orders → 
Portfolio → P&L → Metrics
```

## Component Interaction

```
┌──────────────┐
│  main.py     │  ← Entry Point
└──────┬───────┘
       │
       ├─→ ┌──────────────────┐
       │   │ MarketData       │
       │   │ Generator        │
       │   └────────┬─────────┘
       │            │
       ├─→ ┌────────▼─────────┐
       │   │ Portfolio        │
       │   │ Manager          │
       │   └────────┬─────────┘
       │            │
       ├─→ ┌────────▼─────────┐
       │   │ Strategy         │
       │   │ (MA/Momentum)    │
       │   └────────┬─────────┘
       │            │
       └─→ ┌────────▼─────────┐
           │ Trading          │
           │ Engine           │
           └──────────────────┘
```

## Simulation Loop

```
START
  │
  ├─→ Initialize Components
  │     ├── Generate Market Data
  │     ├── Create Portfolio
  │     ├── Initialize Strategy
  │     └── Setup Trading Engine
  │
  ├─→ FOR each time step:
  │     │
  │     ├── Get Current Market Data
  │     │     ↓
  │     ├── Update Portfolio Prices
  │     │     ↓
  │     ├── Generate Trading Signals
  │     │     ↓
  │     ├── Process Signals → Orders
  │     │     ↓
  │     ├── Execute Orders
  │     │     ↓
  │     ├── Update Portfolio
  │     │     ↓
  │     └── Track Equity
  │
  └─→ Calculate Performance Metrics
        │
        ├── Total Return
        ├── Risk Metrics
        └── Trade Statistics
  │
END
```

## Key Classes

### 1. MarketDataGenerator
```
Purpose: Generate synthetic market data
Input: Symbols, drift, volatility
Output: DataFrame with OHLC data
```

### 2. Strategy Classes
```
Purpose: Generate trading signals
Input: Historical market data
Output: {symbol: signal} dictionary
```

### 3. TradingEngine
```
Purpose: Execute strategies
Input: Market data, portfolio, strategy
Output: Trade executions, metrics
```

### 4. PortfolioManager
```
Purpose: Manage positions and P&L
Input: Buy/sell orders
Output: Portfolio state, P&L
Tracks:
  - Cash
  - Positions
  - Realized P&L
  - Unrealized P&L
  - Exposure
```

### 5. Order/OrderExecutor
```
Purpose: Order management
Input: Order details, market price
Output: Execution status
```

## Signal Flow Example

```
1. Market Data:
   AAPL: $150.00 → $151.00 → $152.00

2. Strategy (MA):
   Short MA: $150.50
   Long MA:  $149.00
   Signal:   BUY (golden cross)

3. Trading Engine:
   Create Order: BUY 100 AAPL @ MARKET

4. Order Executor:
   Execute: 100 AAPL @ $152.00
   Commission: $15.20

5. Portfolio:
   Cash: -$15,215.20
   Position: +100 AAPL @ $152.00
   Unrealized P&L: $0

6. Later (Price = $155.00):
   Update Price
   Unrealized P&L: +$300
```

## P&L Tracking Example

```
Initial Capital: $100,000

Trade 1: BUY 100 AAPL @ $150
  Cash: $85,000
  Position Value: $15,000
  Unrealized P&L: $0
  Realized P&L: $0

Price Update: AAPL → $155
  Cash: $85,000
  Position Value: $15,500
  Unrealized P&L: +$500  ← Tracking open position
  Realized P&L: $0

Trade 2: SELL 100 AAPL @ $155
  Cash: $100,500
  Position Value: $0
  Unrealized P&L: $0
  Realized P&L: +$500    ← Trade closed, P&L realized
  
Total P&L = Realized + Unrealized = $500 + $0 = $500
```

## Exposure Monitoring

```
Portfolio Value: $100,000
Positions:
  AAPL:  $30,000 → 30% exposure
  GOOGL: $25,000 → 25% exposure
  MSFT:  $20,000 → 20% exposure
  Cash:  $25,000 → 25% cash

Total Exposure: 75% (invested)
Cash Position: 25% (available)
```

## Strategy Comparison Flow

```
Same Market Data
       │
       ├──→ Strategy 1 (MA)     → Engine → Portfolio → Results
       ├──→ Strategy 2 (Momentum) → Engine → Portfolio → Results
       └──→ Strategy 3 (MeanRev)  → Engine → Portfolio → Results
                                                               │
                                                               ↓
                                                    Compare Performance
```

This architecture ensures:
- ✓ Modularity
- ✓ Extensibility
- ✓ Testability
- ✓ Maintainability
- ✓ Clear separation of concerns
