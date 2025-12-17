"""
Breakout Strategy
Trade range breakouts with volume confirmation
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional

from quantcli.strategies.base import BaseStrategy, Signal


class BreakoutStrategy(BaseStrategy):
    """
    Breakout Strategy
    
    Logic:
    - LONG when price breaks above resistance with volume
    - SHORT when price breaks below support with volume
    - FLAT otherwise
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize Breakout strategy
        
        Config parameters:
        - lookback_period: Period for support/resistance (default: 20)
        - volume_multiplier: Volume threshold multiplier (default: 1.5)
        - breakout_threshold: Price breakout threshold % (default: 0.5)
        - stop_loss_pct: Stop loss percentage (default: 2.5)
        - take_profit_pct: Take profit percentage (default: 6.0)
        """
        super().__init__(config)
        
        self.lookback_period = self.get_config('lookback_period', 20)
        self.volume_multiplier = self.get_config('volume_multiplier', 1.5)
        self.breakout_threshold = self.get_config('breakout_threshold', 0.5)
        self.stop_loss_pct = self.get_config('stop_loss_pct', 2.5)
        self.take_profit_pct = self.get_config('take_profit_pct', 6.0)
    
    def _calculate_levels(self, data: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate support and resistance levels
        
        Args:
            data: OHLCV DataFrame
            
        Returns:
            Dictionary with support and resistance levels
        """
        recent_data = data.tail(self.lookback_period)
        
        resistance = recent_data['high'].max()
        support = recent_data['low'].min()
        avg_volume = recent_data['volume'].mean()
        
        return {
            'resistance': resistance,
            'support': support,
            'avg_volume': avg_volume
        }
    
    def generate_signal(self, data: pd.DataFrame) -> Signal:
        """
        Generate breakout signal
        
        Args:
            data: OHLCV DataFrame
            
        Returns:
            Signal object
        """
        # Need enough data
        if len(data) < self.lookback_period:
            return Signal(
                direction=Signal.FLAT,
                confidence=0,
                reason="Insufficient data for breakout detection",
                entry_price=data['close'].iloc[-1]
            )
        
        # Calculate levels
        levels = self._calculate_levels(data)
        
        # Get current values
        current_price = data['close'].iloc[-1]
        current_high = data['high'].iloc[-1]
        current_low = data['low'].iloc[-1]
        current_volume = data['volume'].iloc[-1]
        
        resistance = levels['resistance']
        support = levels['support']
        avg_volume = levels['avg_volume']
        
        # Calculate breakout amounts
        resistance_breakout = (current_high - resistance) / resistance * 100
        support_breakout = (support - current_low) / support * 100
        
        # Check volume confirmation
        volume_confirmed = current_volume > avg_volume * self.volume_multiplier
        
        # Upside breakout
        if resistance_breakout > self.breakout_threshold and volume_confirmed:
            confidence = min(70 + resistance_breakout * 10, 95)
            stop_loss = support  # Use support as stop loss
            take_profit = current_price * (1 + self.take_profit_pct / 100)
            
            return Signal(
                direction=Signal.LONG,
                confidence=confidence,
                reason=f"Upside breakout: {resistance_breakout:.2f}% above resistance with volume",
                entry_price=current_price,
                stop_loss=stop_loss,
                take_profit=take_profit
            )
        
        # Downside breakout
        elif support_breakout > self.breakout_threshold and volume_confirmed:
            confidence = min(70 + support_breakout * 10, 95)
            stop_loss = resistance  # Use resistance as stop loss
            take_profit = current_price * (1 - self.take_profit_pct / 100)
            
            return Signal(
                direction=Signal.SHORT,
                confidence=confidence,
                reason=f"Downside breakout: {support_breakout:.2f}% below support with volume",
                entry_price=current_price,
                stop_loss=stop_loss,
                take_profit=take_profit
            )
        
        # Near resistance without breakout
        elif (resistance - current_price) / resistance * 100 < 1.0:
            return Signal(
                direction=Signal.FLAT,
                confidence=40,
                reason=f"Near resistance ${resistance:.2f}, waiting for breakout",
                entry_price=current_price
            )
        
        # Near support without breakout
        elif (current_price - support) / support * 100 < 1.0:
            return Signal(
                direction=Signal.FLAT,
                confidence=40,
                reason=f"Near support ${support:.2f}, waiting for breakout",
                entry_price=current_price
            )
        
        # In range
        else:
            range_pct = (resistance - support) / support * 100
            return Signal(
                direction=Signal.FLAT,
                confidence=50,
                reason=f"Price in range (${support:.2f} - ${resistance:.2f}, {range_pct:.1f}%)",
                entry_price=current_price
            )
