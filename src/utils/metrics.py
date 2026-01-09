"""
Utility functions for performance metrics and analysis
"""

import pandas as pd
import numpy as np
from typing import List, Dict


def calculate_sharpe_ratio(
    returns: pd.Series,
    risk_free_rate: float = 0.02,
    periods_per_year: int = 252
) -> float:
    """
    Calculate annualized Sharpe ratio.
    
    Args:
        returns: Series of returns
        risk_free_rate: Annual risk-free rate
        periods_per_year: Number of periods in a year (252 for daily)
        
    Returns:
        Sharpe ratio
    """
    if returns.std() == 0:
        return 0.0
    
    excess_returns = returns - (risk_free_rate / periods_per_year)
    sharpe = excess_returns.mean() / returns.std()
    annualized_sharpe = sharpe * np.sqrt(periods_per_year)
    
    return annualized_sharpe


def calculate_sortino_ratio(
    returns: pd.Series,
    risk_free_rate: float = 0.02,
    periods_per_year: int = 252
) -> float:
    """
    Calculate annualized Sortino ratio (uses downside deviation).
    
    Args:
        returns: Series of returns
        risk_free_rate: Annual risk-free rate
        periods_per_year: Number of periods in a year
        
    Returns:
        Sortino ratio
    """
    excess_returns = returns - (risk_free_rate / periods_per_year)
    
    # Calculate downside deviation
    downside_returns = returns[returns < 0]
    if len(downside_returns) == 0 or downside_returns.std() == 0:
        return 0.0
    
    downside_deviation = downside_returns.std()
    sortino = excess_returns.mean() / downside_deviation
    annualized_sortino = sortino * np.sqrt(periods_per_year)
    
    return annualized_sortino


def calculate_max_drawdown(equity_curve: pd.Series) -> Dict[str, float]:
    """
    Calculate maximum drawdown and related metrics.
    
    Args:
        equity_curve: Series of portfolio values over time
        
    Returns:
        Dictionary with max_drawdown, drawdown_duration, recovery_duration
    """
    # Calculate running maximum
    running_max = equity_curve.expanding().max()
    
    # Calculate drawdown
    drawdown = (equity_curve - running_max) / running_max
    
    # Max drawdown
    max_drawdown = drawdown.min()
    
    # Find drawdown periods
    max_dd_idx = drawdown.idxmin()
    
    # Duration (simplified - count of periods)
    drawdown_duration = len(drawdown[drawdown < 0])
    
    return {
        'max_drawdown': max_drawdown,
        'max_drawdown_date': max_dd_idx,
        'drawdown_duration': drawdown_duration
    }


def calculate_win_rate(trades: List[Dict]) -> Dict[str, float]:
    """
    Calculate win rate and related statistics from trade history.
    
    Args:
        trades: List of trade dictionaries
        
    Returns:
        Dictionary with win_rate, avg_win, avg_loss, profit_factor
    """
    if not trades:
        return {
            'win_rate': 0.0,
            'avg_win': 0.0,
            'avg_loss': 0.0,
            'profit_factor': 0.0
        }
    
    # Filter closed trades (sells) with P&L
    closed_trades = [t for t in trades if 'realized_pnl' in t]
    
    if not closed_trades:
        return {
            'win_rate': 0.0,
            'avg_win': 0.0,
            'avg_loss': 0.0,
            'profit_factor': 0.0
        }
    
    # Separate wins and losses
    wins = [t['realized_pnl'] for t in closed_trades if t['realized_pnl'] > 0]
    losses = [t['realized_pnl'] for t in closed_trades if t['realized_pnl'] < 0]
    
    # Calculate metrics
    num_trades = len(closed_trades)
    num_wins = len(wins)
    win_rate = num_wins / num_trades if num_trades > 0 else 0
    
    avg_win = np.mean(wins) if wins else 0
    avg_loss = np.mean(losses) if losses else 0
    
    # Profit factor: total wins / abs(total losses)
    total_wins = sum(wins) if wins else 0
    total_losses = abs(sum(losses)) if losses else 0
    profit_factor = total_wins / total_losses if total_losses > 0 else 0
    
    return {
        'win_rate': win_rate,
        'avg_win': avg_win,
        'avg_loss': avg_loss,
        'profit_factor': profit_factor,
        'num_trades': num_trades,
        'num_wins': num_wins,
        'num_losses': len(losses)
    }


def calculate_calmar_ratio(
    returns: pd.Series,
    max_drawdown: float,
    periods_per_year: int = 252
) -> float:
    """
    Calculate Calmar ratio (annual return / max drawdown).
    
    Args:
        returns: Series of returns
        max_drawdown: Maximum drawdown (as negative value)
        periods_per_year: Number of periods in a year
        
    Returns:
        Calmar ratio
    """
    if max_drawdown >= 0:
        return 0.0
    
    annual_return = returns.mean() * periods_per_year
    calmar = annual_return / abs(max_drawdown)
    
    return calmar


def calculate_value_at_risk(
    returns: pd.Series,
    confidence_level: float = 0.95
) -> float:
    """
    Calculate Value at Risk (VaR) using historical method.
    
    Args:
        returns: Series of returns
        confidence_level: Confidence level (e.g., 0.95 for 95%)
        
    Returns:
        VaR value (as positive number representing potential loss)
    """
    if returns.empty:
        return 0.0
    
    var = np.percentile(returns, (1 - confidence_level) * 100)
    
    return abs(var)


def generate_performance_report(
    equity_curve: pd.Series,
    trade_history: List[Dict],
    initial_capital: float
) -> Dict:
    """
    Generate comprehensive performance report.
    
    Args:
        equity_curve: Series of portfolio values
        trade_history: List of trade dictionaries
        initial_capital: Starting capital
        
    Returns:
        Dictionary of performance metrics
    """
    # Calculate returns
    returns = equity_curve.pct_change().dropna()
    
    # Total return
    total_return = (equity_curve.iloc[-1] - initial_capital) / initial_capital
    
    # Annualized return
    num_periods = len(equity_curve)
    years = num_periods / 252
    annualized_return = (1 + total_return) ** (1 / years) - 1 if years > 0 else 0
    
    # Risk metrics
    sharpe = calculate_sharpe_ratio(returns)
    sortino = calculate_sortino_ratio(returns)
    dd_metrics = calculate_max_drawdown(equity_curve)
    calmar = calculate_calmar_ratio(returns, dd_metrics['max_drawdown'])
    var_95 = calculate_value_at_risk(returns, 0.95)
    
    # Trade statistics
    trade_stats = calculate_win_rate(trade_history)
    
    return {
        'total_return': total_return,
        'annualized_return': annualized_return,
        'sharpe_ratio': sharpe,
        'sortino_ratio': sortino,
        'calmar_ratio': calmar,
        'max_drawdown': dd_metrics['max_drawdown'],
        'value_at_risk_95': var_95,
        'volatility': returns.std() * np.sqrt(252),
        **trade_stats
    }
