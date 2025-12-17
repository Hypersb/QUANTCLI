"""
Real-time price fetching
Uses CCXT for exchange connectivity
"""

from typing import Dict, Any, Optional
import ccxt
from datetime import datetime, timedelta


class PriceService:
    """Service for fetching real-time prices"""
    
    def __init__(self, exchange_id: str = 'binance'):
        """
        Initialize price service
        
        Args:
            exchange_id: Exchange to use (default: binance)
        """
        self.exchange_id = exchange_id
        self.exchange = getattr(ccxt, exchange_id)()
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._cache_ttl = 10  # seconds
    
    def get_ticker(self, symbol: str, use_cache: bool = True) -> Dict[str, Any]:
        """
        Get ticker data for a symbol
        
        Args:
            symbol: Trading pair (e.g., 'BTC/USDT')
            use_cache: Whether to use cached data
            
        Returns:
            Ticker data dictionary
        """
        # Check cache
        if use_cache and symbol in self._cache:
            cached = self._cache[symbol]
            age = (datetime.now() - cached['timestamp']).total_seconds()
            if age < self._cache_ttl:
                return cached['data']
        
        # Fetch from exchange
        ticker = self.exchange.fetch_ticker(symbol)
        
        # Cache result
        self._cache[symbol] = {
            'data': ticker,
            'timestamp': datetime.now()
        }
        
        return ticker
    
    def get_price(self, symbol: str) -> float:
        """
        Get current price for a symbol
        
        Args:
            symbol: Trading pair
            
        Returns:
            Current price
        """
        ticker = self.get_ticker(symbol)
        return ticker['last']


# Global price service instance
_price_service: Optional[PriceService] = None


def get_price_service() -> PriceService:
    """Get or create global price service instance"""
    global _price_service
    if _price_service is None:
        _price_service = PriceService()
    return _price_service


def get_current_price(symbol: str) -> Dict[str, Any]:
    """
    Get current price data for a symbol
    
    Args:
        symbol: Trading pair
        
    Returns:
        Dictionary with price data
    """
    service = get_price_service()
    ticker = service.get_ticker(symbol)
    
    return {
        'symbol': symbol,
        'last': ticker['last'],
        'bid': ticker['bid'],
        'ask': ticker['ask'],
        'volume': ticker['baseVolume'],
        'timestamp': ticker['timestamp']
    }
