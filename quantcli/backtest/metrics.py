"""
Backtesting metrics calculation
Calculates performance metrics for backtests
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any


class MetricsCalculator:
    """Calculate backtest performance metrics"""
    
    @staticmethod
    def calculate_returns(equity_curve: pd.Series) -> pd.Series:
        """Calculate returns from equity curve"""
        return equity_curve.pct_change().fillna(0)
    
    @staticmethod
    def total_return(initial_capital: float, final_capital: float) -> float:
        """Calculate total return percentage"""
        return ((final_capital - initial_capital) / initial_capital) * 100
    
    @staticmethod
    def max_drawdown(equity_curve: pd.Series) -> float:
        """
        Calculate maximum drawdown percentage
        
        Args:
            equity_curve: Series of equity values
            
        Returns:
            Max drawdown as percentage
        """
        peak = equity_curve.expanding(min_periods=1).max()
        drawdown = (equity_curve - peak) / peak * 100
        return drawdown.min()
    
    @staticmethod
    def sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.0) -> float:
        """
        Calculate Sharpe ratio
        
        Args:
            returns: Series of returns
            risk_free_rate: Risk-free rate (annualized)
            
        Returns:
            Sharpe ratio
        """
        if len(returns) == 0 or returns.std() == 0:
            return 0.0
        
        excess_returns = returns - (risk_free_rate / 252)  # Daily risk-free rate
        return np.sqrt(252) * (excess_returns.mean() / excess_returns.std())
    
    @staticmethod
    def win_rate(trades: List[Dict[str, Any]]) -> float:
        """
        Calculate win rate percentage
        
        Args:
            trades: List of trade dictionaries with 'pnl' key
            
        Returns:
            Win rate percentage
        """
        if not trades:
            return 0.0
        
        winning_trades = sum(1 for t in trades if t['pnl'] > 0)
        return (winning_trades / len(trades)) * 100
    
    @staticmethod
    def profit_factor(trades: List[Dict[str, Any]]) -> float:
        """
        Calculate profit factor (gross profit / gross loss)
        
        Args:
            trades: List of trade dictionaries
            
        Returns:
            Profit factor
        """
        if not trades:
            return 0.0
        
        gross_profit = sum(t['pnl'] for t in trades if t['pnl'] > 0)
        gross_loss = abs(sum(t['pnl'] for t in trades if t['pnl'] < 0))
        
        if gross_loss == 0:
            return float('inf') if gross_profit > 0 else 0.0
        
        return gross_profit / gross_loss
    
    @staticmethod
    def average_trade(trades: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Calculate average trade statistics
        
        Args:
            trades: List of trade dictionaries
            
        Returns:
            Dictionary with average trade stats
        """
        if not trades:
            return {'avg_pnl': 0, 'avg_win': 0, 'avg_loss': 0}
        
        all_pnl = [t['pnl'] for t in trades]
        wins = [t['pnl'] for t in trades if t['pnl'] > 0]
        losses = [t['pnl'] for t in trades if t['pnl'] < 0]
        
        return {
            'avg_pnl': np.mean(all_pnl) if all_pnl else 0,
            'avg_win': np.mean(wins) if wins else 0,
            'avg_loss': np.mean(losses) if losses else 0
        }
    
    @staticmethod
    def calculate_all(
        equity_curve: pd.Series,
        trades: List[Dict[str, Any]],
        initial_capital: float
    ) -> Dict[str, Any]:
        """
        Calculate all metrics
        
        Args:
            equity_curve: Series of equity values
            trades: List of completed trades
            initial_capital: Starting capital
            
        Returns:
            Dictionary of all metrics
        """
        returns = MetricsCalculator.calculate_returns(equity_curve)
        avg_stats = MetricsCalculator.average_trade(trades)
        
        return {
            'total_return': MetricsCalculator.total_return(initial_capital, equity_curve.iloc[-1]),
            'max_drawdown': MetricsCalculator.max_drawdown(equity_curve),
            'sharpe_ratio': MetricsCalculator.sharpe_ratio(returns),
            'win_rate': MetricsCalculator.win_rate(trades),
            'profit_factor': MetricsCalculator.profit_factor(trades),
            'total_trades': len(trades),
            'avg_pnl': avg_stats['avg_pnl'],
            'avg_win': avg_stats['avg_win'],
            'avg_loss': avg_stats['avg_loss'],
            'final_equity': equity_curve.iloc[-1]
        }
