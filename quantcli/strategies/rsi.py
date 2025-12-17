"""
RSI Mean Reversion Strategy
Buy when RSI is oversold, sell when overbought
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional

from quantcli.strategies.base import BaseStrategy, Signal


class RSIStrategy(BaseStrategy):
    """
    RSI Mean Reversion Strategy
    
    Logic:
    - LONG when RSI < oversold threshold (default: 30)
    - SHORT when RSI > overbought threshold (default: 70)
    - FLAT otherwise
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize RSI strategy
        
        Config parameters:
        - rsi_period: RSI calculation period (default: 14)
        - oversold: Oversold threshold (default: 30)
        - overbought: Overbought threshold (default: 70)
        - stop_loss_pct: Stop loss percentage (default: 2.0)
        - take_profit_pct: Take profit percentage (default: 5.0)
        """
        super().__init__(config)
        
        self.rsi_period = self.get_config('rsi_period', 14)
        self.oversold = self.get_config('oversold', 30)
        self.overbought = self.get_config('overbought', 70)
        self.stop_loss_pct = self.get_config('stop_loss_pct', 2.0)
        self.take_profit_pct = self.get_config('take_profit_pct', 5.0)
    
    def _calculate_rsi(self, data: pd.DataFrame) -> pd.Series:
        """
        Calculate RSI indicator
        
        Args:
            data: OHLCV DataFrame
            
        Returns:
            Series with RSI values
        """
        close = data['close']
        delta = close.diff()
        
        gain = (delta.where(delta > 0, 0)).rolling(window=self.rsi_period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.rsi_period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def generate_signal(self, data: pd.DataFrame) -> Signal:
        """
        Generate RSI-based signal
        
        Args:
            data: OHLCV DataFrame
            
        Returns:
            Signal object
        """
        # Calculate RSI
        data = data.copy()
        data['rsi'] = self._calculate_rsi(data)
        
        # Get latest values
        current_rsi = data['rsi'].iloc[-1]
        current_price = data['close'].iloc[-1]
        
        # Check for NaN (not enough data)
        if pd.isna(current_rsi):
            return Signal(
                direction=Signal.FLAT,
                confidence=0,
                reason="Insufficient data to calculate RSI",
                entry_price=current_price
            )
        
        # Generate signal
        if current_rsi < self.oversold:
            # Oversold - BUY signal
            confidence = 100 * (self.oversold - current_rsi) / self.oversold
            stop_loss = current_price * (1 - self.stop_loss_pct / 100)
            take_profit = current_price * (1 + self.take_profit_pct / 100)
            
            return Signal(
                direction=Signal.LONG,
                confidence=confidence,
                reason=f"RSI oversold: {current_rsi:.1f} < {self.oversold}",
                entry_price=current_price,
                stop_loss=stop_loss,
                take_profit=take_profit
            )
        
        elif current_rsi > self.overbought:
            # Overbought - SELL signal
            confidence = 100 * (current_rsi - self.overbought) / (100 - self.overbought)
            stop_loss = current_price * (1 + self.stop_loss_pct / 100)
            take_profit = current_price * (1 - self.take_profit_pct / 100)
            
            return Signal(
                direction=Signal.SHORT,
                confidence=confidence,
                reason=f"RSI overbought: {current_rsi:.1f} > {self.overbought}",
                entry_price=current_price,
                stop_loss=stop_loss,
                take_profit=take_profit
            )
        
        else:
            # Neutral zone
            return Signal(
                direction=Signal.FLAT,
                confidence=50,
                reason=f"RSI neutral: {current_rsi:.1f}",
                entry_price=current_price
            )
