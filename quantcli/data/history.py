"""
Historical market data fetching and caching
Provides OHLCV data for backtesting and analysis
"""

from typing import Optional, List
from datetime import datetime, timedelta
import pandas as pd
import ccxt
from pathlib import Path
import json


class HistoryService:
    """Service for fetching and caching historical data"""
    
    def __init__(self, exchange_id: str = 'binance', cache_dir: str = '.cache'):
        """
        Initialize history service
        
        Args:
            exchange_id: Exchange to use
            cache_dir: Directory for caching data
        """
        self.exchange_id = exchange_id
        self.exchange = getattr(ccxt, exchange_id)()
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
    
    def _get_cache_path(self, symbol: str, timeframe: str) -> Path:
        """Get cache file path for symbol and timeframe"""
        safe_symbol = symbol.replace('/', '_')
        return self.cache_dir / f"{safe_symbol}_{timeframe}.parquet"
    
    def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str = '1h',
        days: int = 90,
        use_cache: bool = True
    ) -> pd.DataFrame:
        """
        Fetch OHLCV data
        
        Args:
            symbol: Trading pair
            timeframe: Candle timeframe (1m, 5m, 1h, 1d)
            days: Number of days to fetch
            use_cache: Whether to use cached data
            
        Returns:
            DataFrame with OHLCV data
        """
        cache_path = self._get_cache_path(symbol, timeframe)
        
        # Try to load from cache
        if use_cache and cache_path.exists():
            df = pd.read_parquet(cache_path)
            
            # Check if cache is recent enough
            last_timestamp = df['timestamp'].max()
            age = datetime.now() - pd.to_datetime(last_timestamp, unit='ms')
            
            if age < timedelta(hours=1):
                return df
        
        # Fetch from exchange
        since = int((datetime.now() - timedelta(days=days)).timestamp() * 1000)
        
        ohlcv = self.exchange.fetch_ohlcv(
            symbol=symbol,
            timeframe=timeframe,
            since=since
        )
        
        # Convert to DataFrame
        df = pd.DataFrame(
            ohlcv,
            columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
        )
        
        # Cache the data
        df.to_parquet(cache_path)
        
        return df
    
    def get_latest_candles(
        self,
        symbol: str,
        timeframe: str = '1h',
        limit: int = 100
    ) -> pd.DataFrame:
        """
        Get latest N candles
        
        Args:
            symbol: Trading pair
            timeframe: Candle timeframe
            limit: Number of candles
            
        Returns:
            DataFrame with OHLCV data
        """
        ohlcv = self.exchange.fetch_ohlcv(
            symbol=symbol,
            timeframe=timeframe,
            limit=limit
        )
        
        df = pd.DataFrame(
            ohlcv,
            columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
        )
        
        return df


# Global history service instance
_history_service: Optional[HistoryService] = None


def get_history_service() -> HistoryService:
    """Get or create global history service instance"""
    global _history_service
    if _history_service is None:
        _history_service = HistoryService()
    return _history_service


def get_historical_data(
    symbol: str,
    timeframe: str = '1h',
    days: int = 90
) -> pd.DataFrame:
    """
    Get historical OHLCV data
    
    Args:
        symbol: Trading pair
        timeframe: Candle timeframe
        days: Number of days
        
    Returns:
        DataFrame with OHLCV data
    """
    service = get_history_service()
    return service.fetch_ohlcv(symbol, timeframe, days)
