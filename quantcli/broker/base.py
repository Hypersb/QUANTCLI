"""
Base broker interface
Defines the contract for all broker implementations
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime


class Order:
    """Represents a trading order"""
    
    def __init__(
        self,
        symbol: str,
        side: str,
        amount: float,
        price: float,
        timestamp: Optional[datetime] = None
    ):
        self.symbol = symbol
        self.side = side  # 'buy' or 'sell'
        self.amount = amount
        self.price = price
        self.timestamp = timestamp or datetime.now()
        self.total = amount * price
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert order to dictionary"""
        return {
            'symbol': self.symbol,
            'side': self.side,
            'amount': self.amount,
            'price': self.price,
            'total': self.total,
            'timestamp': self.timestamp.isoformat()
        }


class BaseBroker(ABC):
    """
    Abstract base class for broker implementations
    Defines the interface for paper and live brokers
    """
    
    @abstractmethod
    def buy(self, symbol: str, amount: float, price: Optional[float] = None) -> Dict[str, Any]:
        """
        Execute a buy order
        
        Args:
            symbol: Trading pair symbol
            amount: Amount to buy
            price: Price (None for market order)
            
        Returns:
            Order details
        """
        pass
    
    @abstractmethod
    def sell(self, symbol: str, amount: float, price: Optional[float] = None) -> Dict[str, Any]:
        """
        Execute a sell order
        
        Args:
            symbol: Trading pair symbol
            amount: Amount to sell
            price: Price (None for market order)
            
        Returns:
            Order details
        """
        pass
    
    @abstractmethod
    def get_balance(self) -> Dict[str, float]:
        """
        Get current balance
        
        Returns:
            Dictionary of currency: amount
        """
        pass
    
    @abstractmethod
    def get_positions(self) -> Dict[str, Dict[str, Any]]:
        """
        Get current open positions
        
        Returns:
            Dictionary of symbol: position details
        """
        pass
    
    @abstractmethod
    def get_order_history(self) -> List[Dict[str, Any]]:
        """
        Get order history
        
        Returns:
            List of order dictionaries
        """
        pass
