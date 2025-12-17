"""
Performance analytics
Tracks and analyzes trade performance
"""

from typing import Dict, Any, List
import pandas as pd
import json
from pathlib import Path
from datetime import datetime


class PerformanceAnalytics:
    """
    Tracks and analyzes trading performance
    """
    
    def __init__(self, data_file: str = "performance_data.json"):
        """
        Initialize performance analytics
        
        Args:
            data_file: File to store performance data
        """
        self.data_file = Path(data_file)
        self.trades: List[Dict[str, Any]] = []
        
        # Load existing data
        if self.data_file.exists():
            self._load_data()
    
    def _load_data(self):
        """Load performance data from file"""
        with open(self.data_file, 'r') as f:
            data = json.load(f)
            self.trades = data.get('trades', [])
    
    def _save_data(self):
        """Save performance data to file"""
        data = {'trades': self.trades}
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def record_trade(
        self,
        symbol: str,
        side: str,
        entry_price: float,
        exit_price: float,
        amount: float,
        pnl: float,
        strategy: str = 'manual'
    ):
        """
        Record a completed trade
        
        Args:
            symbol: Trading pair
            side: 'long' or 'short'
            entry_price: Entry price
            exit_price: Exit price
            amount: Position size
            pnl: Profit/loss
            strategy: Strategy name
        """
        trade = {
            'timestamp': datetime.now().isoformat(),
            'symbol': symbol,
            'side': side,
            'entry_price': entry_price,
            'exit_price': exit_price,
            'amount': amount,
            'pnl': pnl,
            'strategy': strategy
        }
        
        self.trades.append(trade)
        self._save_data()
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get performance summary
        
        Returns:
            Dictionary with performance metrics
        """
        if not self.trades:
            return {
                'total_trades': 0,
                'total_pnl': 0,
                'win_rate': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'profit_factor': 0
            }
        
        # Calculate metrics
        total_pnl = sum(t['pnl'] for t in self.trades)
        winning_trades = [t for t in self.trades if t['pnl'] > 0]
        losing_trades = [t for t in self.trades if t['pnl'] < 0]
        
        win_rate = (len(winning_trades) / len(self.trades)) * 100 if self.trades else 0
        
        avg_win = sum(t['pnl'] for t in winning_trades) / len(winning_trades) if winning_trades else 0
        avg_loss = sum(t['pnl'] for t in losing_trades) / len(losing_trades) if losing_trades else 0
        
        gross_profit = sum(t['pnl'] for t in winning_trades)
        gross_loss = abs(sum(t['pnl'] for t in losing_trades))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
        
        return {
            'total_trades': len(self.trades),
            'total_pnl': total_pnl,
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades)
        }
    
    def get_trades_by_strategy(self, strategy: str) -> List[Dict[str, Any]]:
        """Get trades filtered by strategy"""
        return [t for t in self.trades if t['strategy'] == strategy]
    
    def get_trades_by_symbol(self, symbol: str) -> List[Dict[str, Any]]:
        """Get trades filtered by symbol"""
        return [t for t in self.trades if t['symbol'] == symbol]
    
    def export_to_csv(self, filename: str = "trades.csv"):
        """
        Export trades to CSV
        
        Args:
            filename: Output filename
        """
        if not self.trades:
            print("No trades to export")
            return
        
        df = pd.DataFrame(self.trades)
        df.to_csv(filename, index=False)
        print(f"Exported {len(self.trades)} trades to {filename}")
    
    def clear_history(self):
        """Clear all trade history"""
        self.trades = []
        self._save_data()
