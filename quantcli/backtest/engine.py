"""
Backtesting engine
Bar-by-bar simulation of trading strategies
"""

from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
from datetime import datetime

from quantcli.strategies.base import BaseStrategy, Signal
from quantcli.strategies.rsi import RSIStrategy
from quantcli.strategies.ema import EMAStrategy
from quantcli.strategies.breakout import BreakoutStrategy
from quantcli.data.history import get_historical_data
from quantcli.backtest.metrics import MetricsCalculator
from quantcli.risk.position import RiskManager
from quantcli.utils.config import config_manager


class BacktestEngine:
    """
    Engine for backtesting trading strategies
    Simulates trading with realistic fees and slippage
    """
    
    def __init__(
        self,
        strategy_name: str,
        symbol: str,
        initial_capital: float = 10000.0,
        fee_rate: float = 0.001,
        slippage_pct: float = 0.05
    ):
        """
        Initialize backtest engine
        
        Args:
            strategy_name: Name of strategy to test
            symbol: Trading pair
            initial_capital: Starting capital
            fee_rate: Trading fee rate (0.001 = 0.1%)
            slippage_pct: Slippage percentage
        """
        self.strategy_name = strategy_name
        self.symbol = symbol
        self.initial_capital = initial_capital
        self.fee_rate = fee_rate
        self.slippage_pct = slippage_pct
        
        # Load strategy
        self.strategy = self._load_strategy()
        
        # Initialize state
        self.capital = initial_capital
        self.position = 0.0
        self.position_entry_price = 0.0
        self.trades: List[Dict[str, Any]] = []
        self.equity_curve: List[float] = [initial_capital]
        
        # Risk management
        self.risk_manager = RiskManager()
    
    def _load_strategy(self) -> BaseStrategy:
        """Load strategy instance"""
        strategies = {
            'rsi': RSIStrategy,
            'ema': EMAStrategy,
            'breakout': BreakoutStrategy
        }
        
        if self.strategy_name not in strategies:
            raise ValueError(f"Unknown strategy: {self.strategy_name}")
        
        # Try to load config
        try:
            config = config_manager.load(f"{self.strategy_name}_strategy")
        except FileNotFoundError:
            config = {}
        
        strategy_class = strategies[self.strategy_name]
        return strategy_class(config)
    
    def _apply_slippage(self, price: float, side: str) -> float:
        """
        Apply slippage to price
        
        Args:
            price: Original price
            side: 'buy' or 'sell'
            
        Returns:
            Price with slippage
        """
        slippage = price * (self.slippage_pct / 100)
        
        if side == 'buy':
            return price + slippage
        else:
            return price - slippage
    
    def _execute_trade(
        self,
        signal: Signal,
        current_price: float,
        timestamp: int
    ):
        """
        Execute a trade based on signal
        
        Args:
            signal: Trading signal
            current_price: Current market price
            timestamp: Current timestamp
        """
        # Close existing position if signal conflicts
        if self.position != 0:
            # Check if we should exit
            should_exit = False
            
            if self.position > 0 and signal.direction == Signal.SHORT:
                should_exit = True
            elif self.position < 0 and signal.direction == Signal.LONG:
                should_exit = True
            elif signal.direction == Signal.FLAT:
                should_exit = True
            
            if should_exit:
                self._close_position(current_price, timestamp, 'signal_exit')
        
        # Open new position if signal is not flat
        if signal.direction != Signal.FLAT and self.position == 0:
            # Calculate position size
            risk_info = self.risk_manager.calculate_position_size(
                capital=self.capital,
                entry_price=current_price,
                stop_loss=signal.stop_loss
            )
            
            if risk_info['size'] > 0:
                # Apply slippage
                if signal.direction == Signal.LONG:
                    entry_price = self._apply_slippage(current_price, 'buy')
                    amount = risk_info['size']
                else:  # SHORT
                    entry_price = self._apply_slippage(current_price, 'sell')
                    amount = -risk_info['size']
                
                # Calculate cost with fees
                cost = abs(amount) * entry_price
                fee = cost * self.fee_rate
                total_cost = cost + fee
                
                # Check if we have enough capital
                if total_cost <= self.capital:
                    self.position = amount
                    self.position_entry_price = entry_price
                    self.capital -= total_cost
    
    def _close_position(
        self,
        current_price: float,
        timestamp: int,
        reason: str = 'manual'
    ):
        """
        Close current position
        
        Args:
            current_price: Current market price
            timestamp: Current timestamp
            reason: Reason for closing
        """
        if self.position == 0:
            return
        
        # Apply slippage
        if self.position > 0:
            exit_price = self._apply_slippage(current_price, 'sell')
        else:
            exit_price = self._apply_slippage(current_price, 'buy')
        
        # Calculate proceeds
        proceeds = abs(self.position) * exit_price
        fee = proceeds * self.fee_rate
        net_proceeds = proceeds - fee
        
        # Calculate PnL
        if self.position > 0:
            pnl = net_proceeds - (abs(self.position) * self.position_entry_price)
        else:
            pnl = (abs(self.position) * self.position_entry_price) - net_proceeds
        
        # Update capital
        self.capital += net_proceeds
        
        # Record trade
        self.trades.append({
            'timestamp': timestamp,
            'entry_price': self.position_entry_price,
            'exit_price': exit_price,
            'position': self.position,
            'pnl': pnl,
            'reason': reason
        })
        
        # Update risk manager
        self.risk_manager.update_daily_pnl(pnl)
        
        # Reset position
        self.position = 0.0
        self.position_entry_price = 0.0
    
    def run(
        self,
        timeframe: str = '1h',
        days: int = 90
    ) -> Dict[str, Any]:
        """
        Run backtest
        
        Args:
            timeframe: Data timeframe
            days: Number of days to backtest
            
        Returns:
            Dictionary with backtest results
        """
        # Get historical data
        data = get_historical_data(self.symbol, timeframe, days)
        
        if len(data) < 50:
            raise ValueError("Insufficient data for backtesting")
        
        # Bar-by-bar simulation
        for i in range(50, len(data)):  # Start after warmup period
            # Get data up to current bar
            current_data = data.iloc[:i+1].copy()
            current_bar = current_data.iloc[-1]
            
            # Generate signal
            signal = self.strategy.generate_signal(current_data)
            
            # Execute trade logic
            self._execute_trade(signal, current_bar['close'], current_bar['timestamp'])
            
            # Record equity
            current_equity = self.capital
            if self.position != 0:
                current_equity += abs(self.position) * current_bar['close']
            
            self.equity_curve.append(current_equity)
        
        # Close any remaining position
        if self.position != 0:
            self._close_position(
                data.iloc[-1]['close'],
                data.iloc[-1]['timestamp'],
                'backtest_end'
            )
        
        # Calculate metrics
        equity_series = pd.Series(self.equity_curve)
        metrics = MetricsCalculator.calculate_all(
            equity_series,
            self.trades,
            self.initial_capital
        )
        
        return metrics
