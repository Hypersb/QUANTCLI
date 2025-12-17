"""
Base strategy interface
All strategies inherit from this class
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import pandas as pd


class Signal:
    """Represents a trading signal"""
    
    LONG = 'LONG'
    SHORT = 'SHORT'
    FLAT = 'FLAT'
    
    def __init__(
        self,
        direction: str,
        confidence: float,
        reason: str,
        entry_price: Optional[float] = None,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None
    ):
        """
        Initialize signal
        
        Args:
            direction: LONG, SHORT, or FLAT
            confidence: Confidence score 0-100
            reason: Human-readable reason
            entry_price: Suggested entry price
            stop_loss: Stop loss price
            take_profit: Take profit price
        """
        self.direction = direction
        self.confidence = max(0, min(100, confidence))
        self.reason = reason
        self.entry_price = entry_price
        self.stop_loss = stop_loss
        self.take_profit = take_profit
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert signal to dictionary"""
        return {
            'direction': self.direction,
            'confidence': self.confidence,
            'reason': self.reason,
            'entry_price': self.entry_price,
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit
        }


class BaseStrategy(ABC):
    """
    Abstract base class for trading strategies
    All strategies must implement generate_signal method
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize strategy
        
        Args:
            config: Strategy configuration dictionary
        """
        self.config = config or {}
        self.name = self.__class__.__name__
    
    @abstractmethod
    def generate_signal(self, data: pd.DataFrame) -> Signal:
        """
        Generate a trading signal based on market data
        
        Args:
            data: DataFrame with OHLCV data (columns: timestamp, open, high, low, close, volume)
            
        Returns:
            Signal object
        """
        pass
    
    def _calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate technical indicators
        Subclasses can override to add custom indicators
        
        Args:
            data: OHLCV DataFrame
            
        Returns:
            DataFrame with indicators added
        """
        return data.copy()
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.config.get(key, default)
