"""
Position sizing and risk management
Calculates appropriate position sizes based on risk parameters
"""

from typing import Dict, Any, Optional
import pandas as pd
import numpy as np


class RiskManager:
    """
    Manages position sizing and risk limits
    """
    
    def __init__(
        self,
        max_risk_per_trade: float = 2.0,
        max_position_size_pct: float = 10.0,
        max_daily_loss_pct: float = 5.0,
        use_atr_stops: bool = True,
        atr_multiplier: float = 2.0
    ):
        """
        Initialize risk manager
        
        Args:
            max_risk_per_trade: Max % of capital to risk per trade
            max_position_size_pct: Max % of capital per position
            max_daily_loss_pct: Max % daily loss limit
            use_atr_stops: Use ATR-based stop losses
            atr_multiplier: ATR multiplier for stops
        """
        self.max_risk_per_trade = max_risk_per_trade
        self.max_position_size_pct = max_position_size_pct
        self.max_daily_loss_pct = max_daily_loss_pct
        self.use_atr_stops = use_atr_stops
        self.atr_multiplier = atr_multiplier
        
        self.daily_pnl = 0.0
        self.daily_loss_limit_hit = False
    
    def calculate_position_size(
        self,
        capital: float,
        entry_price: float,
        stop_loss: Optional[float] = None,
        data: Optional[pd.DataFrame] = None
    ) -> Dict[str, Any]:
        """
        Calculate appropriate position size
        
        Args:
            capital: Available capital
            entry_price: Entry price
            stop_loss: Stop loss price
            data: Historical data for ATR calculation
            
        Returns:
            Dictionary with position size and risk details
        """
        # Check daily loss limit
        if self.daily_loss_limit_hit:
            return {
                'size': 0,
                'reason': 'Daily loss limit hit',
                'stop_loss': stop_loss
            }
        
        # Calculate stop loss if not provided
        if stop_loss is None and data is not None and self.use_atr_stops:
            atr = self._calculate_atr(data)
            stop_loss = entry_price - (atr * self.atr_multiplier)
        
        if stop_loss is None:
            # Default 2% stop loss
            stop_loss = entry_price * 0.98
        
        # Calculate risk per share
        risk_per_unit = abs(entry_price - stop_loss)
        
        # Calculate max position based on risk per trade
        max_risk_amount = capital * (self.max_risk_per_trade / 100)
        size_by_risk = max_risk_amount / risk_per_unit
        
        # Calculate max position based on position size limit
        max_position_amount = capital * (self.max_position_size_pct / 100)
        size_by_position = max_position_amount / entry_price
        
        # Take the smaller of the two
        position_size = min(size_by_risk, size_by_position)
        
        # Calculate actual risk
        actual_risk_amount = position_size * risk_per_unit
        actual_risk_pct = (actual_risk_amount / capital) * 100
        
        return {
            'size': position_size,
            'stop_loss': stop_loss,
            'risk_amount': actual_risk_amount,
            'risk_pct': actual_risk_pct,
            'risk_per_unit': risk_per_unit
        }
    
    def _calculate_atr(self, data: pd.DataFrame, period: int = 14) -> float:
        """
        Calculate Average True Range
        
        Args:
            data: OHLCV DataFrame
            period: ATR period
            
        Returns:
            ATR value
        """
        high = data['high']
        low = data['low']
        close = data['close']
        
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        
        return atr.iloc[-1]
    
    def update_daily_pnl(self, pnl: float):
        """
        Update daily PnL and check limits
        
        Args:
            pnl: Profit/loss amount
        """
        self.daily_pnl += pnl
    
    def check_daily_limit(self, capital: float) -> bool:
        """
        Check if daily loss limit is hit
        
        Args:
            capital: Current capital
            
        Returns:
            True if limit hit
        """
        loss_pct = abs(self.daily_pnl / capital) * 100
        
        if self.daily_pnl < 0 and loss_pct >= self.max_daily_loss_pct:
            self.daily_loss_limit_hit = True
            return True
        
        return False
    
    def reset_daily(self):
        """Reset daily tracking (call at start of new day)"""
        self.daily_pnl = 0.0
        self.daily_loss_limit_hit = False
