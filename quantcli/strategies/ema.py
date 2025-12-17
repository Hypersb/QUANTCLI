"""
EMA Trend Following Strategy
Follow exponential moving average crossovers
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional

from quantcli.strategies.base import BaseStrategy, Signal


class EMAStrategy(BaseStrategy):
    """
    EMA Trend Following Strategy
    
    Logic:
    - LONG when fast EMA crosses above slow EMA (golden cross)
    - SHORT when fast EMA crosses below slow EMA (death cross)
    - FLAT otherwise
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize EMA strategy
        
        Config parameters:
        - fast_period: Fast EMA period (default: 12)
        - slow_period: Slow EMA period (default: 26)
        - stop_loss_pct: Stop loss percentage (default: 3.0)
        - take_profit_pct: Take profit percentage (default: 8.0)
        """
        super().__init__(config)
        
        self.fast_period = self.get_config('fast_period', 12)
        self.slow_period = self.get_config('slow_period', 26)
        self.stop_loss_pct = self.get_config('stop_loss_pct', 3.0)
        self.take_profit_pct = self.get_config('take_profit_pct', 8.0)
    
    def _calculate_ema(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate EMA indicators
        
        Args:
            data: OHLCV DataFrame
            
        Returns:
            DataFrame with EMA columns added
        """
        df = data.copy()
        df['ema_fast'] = df['close'].ewm(span=self.fast_period, adjust=False).mean()
        df['ema_slow'] = df['close'].ewm(span=self.slow_period, adjust=False).mean()
        return df
    
    def generate_signal(self, data: pd.DataFrame) -> Signal:
        """
        Generate EMA crossover signal
        
        Args:
            data: OHLCV DataFrame
            
        Returns:
            Signal object
        """
        # Calculate EMAs
        data = self._calculate_ema(data)
        
        # Get latest values
        current_price = data['close'].iloc[-1]
        current_fast = data['ema_fast'].iloc[-1]
        current_slow = data['ema_slow'].iloc[-1]
        
        # Get previous values for crossover detection
        prev_fast = data['ema_fast'].iloc[-2]
        prev_slow = data['ema_slow'].iloc[-2]
        
        # Check for NaN
        if pd.isna(current_fast) or pd.isna(current_slow):
            return Signal(
                direction=Signal.FLAT,
                confidence=0,
                reason="Insufficient data to calculate EMAs",
                entry_price=current_price
            )
        
        # Calculate trend strength
        distance_pct = abs(current_fast - current_slow) / current_slow * 100
        
        # Detect crossover
        bullish_cross = prev_fast <= prev_slow and current_fast > current_slow
        bearish_cross = prev_fast >= prev_slow and current_fast < current_slow
        
        if bullish_cross:
            # Golden cross - LONG
            confidence = min(80 + distance_pct * 10, 100)
            stop_loss = current_price * (1 - self.stop_loss_pct / 100)
            take_profit = current_price * (1 + self.take_profit_pct / 100)
            
            return Signal(
                direction=Signal.LONG,
                confidence=confidence,
                reason=f"EMA golden cross (fast: {current_fast:.2f} > slow: {current_slow:.2f})",
                entry_price=current_price,
                stop_loss=stop_loss,
                take_profit=take_profit
            )
        
        elif bearish_cross:
            # Death cross - SHORT
            confidence = min(80 + distance_pct * 10, 100)
            stop_loss = current_price * (1 + self.stop_loss_pct / 100)
            take_profit = current_price * (1 - self.take_profit_pct / 100)
            
            return Signal(
                direction=Signal.SHORT,
                confidence=confidence,
                reason=f"EMA death cross (fast: {current_fast:.2f} < slow: {current_slow:.2f})",
                entry_price=current_price,
                stop_loss=stop_loss,
                take_profit=take_profit
            )
        
        elif current_fast > current_slow:
            # Uptrend but no fresh crossover
            confidence = min(50 + distance_pct * 5, 70)
            return Signal(
                direction=Signal.LONG,
                confidence=confidence,
                reason=f"In uptrend (fast EMA > slow EMA by {distance_pct:.2f}%)",
                entry_price=current_price
            )
        
        elif current_fast < current_slow:
            # Downtrend but no fresh crossover
            confidence = min(50 + distance_pct * 5, 70)
            return Signal(
                direction=Signal.SHORT,
                confidence=confidence,
                reason=f"In downtrend (fast EMA < slow EMA by {distance_pct:.2f}%)",
                entry_price=current_price
            )
        
        else:
            # EMAs aligned
            return Signal(
                direction=Signal.FLAT,
                confidence=50,
                reason="EMAs aligned, no clear trend",
                entry_price=current_price
            )
