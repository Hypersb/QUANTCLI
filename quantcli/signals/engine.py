"""
Signal generation engine
Coordinates strategy execution and signal generation
"""

from typing import Dict, Any, Optional
import pandas as pd

from quantcli.strategies.base import BaseStrategy, Signal
from quantcli.strategies.rsi import RSIStrategy
from quantcli.strategies.ema import EMAStrategy
from quantcli.strategies.breakout import BreakoutStrategy
from quantcli.data.history import get_historical_data
from quantcli.utils.config import config_manager


class SignalEngine:
    """
    Engine for generating trading signals
    Loads strategies and generates signals based on market data
    """
    
    def __init__(self):
        """Initialize signal engine"""
        self.strategies = {
            'rsi': RSIStrategy,
            'ema': EMAStrategy,
            'breakout': BreakoutStrategy
        }
    
    def _load_strategy(self, strategy_name: str) -> BaseStrategy:
        """
        Load a strategy instance
        
        Args:
            strategy_name: Name of strategy
            
        Returns:
            Strategy instance
        """
        if strategy_name not in self.strategies:
            raise ValueError(f"Unknown strategy: {strategy_name}. Available: {list(self.strategies.keys())}")
        
        # Try to load config
        try:
            config = config_manager.load(f"{strategy_name}_strategy")
        except FileNotFoundError:
            config = {}
        
        strategy_class = self.strategies[strategy_name]
        return strategy_class(config)
    
    def generate(
        self,
        strategy_name: str,
        symbol: str,
        timeframe: str = '1h',
        lookback_days: int = 30
    ) -> Dict[str, Any]:
        """
        Generate a trading signal
        
        Args:
            strategy_name: Name of strategy to use
            symbol: Trading pair
            timeframe: Data timeframe
            lookback_days: Days of historical data to use
            
        Returns:
            Signal dictionary
        """
        # Load strategy
        strategy = self._load_strategy(strategy_name)
        
        # Get historical data
        data = get_historical_data(symbol, timeframe, lookback_days)
        
        # Generate signal
        signal = strategy.generate_signal(data)
        
        # Add metadata
        result = signal.to_dict()
        result['strategy'] = strategy_name
        result['symbol'] = symbol
        result['timeframe'] = timeframe
        
        return result
    
    def generate_multiple(
        self,
        symbol: str,
        strategy_names: Optional[list] = None,
        timeframe: str = '1h'
    ) -> Dict[str, Dict[str, Any]]:
        """
        Generate signals from multiple strategies
        
        Args:
            symbol: Trading pair
            strategy_names: List of strategy names (None for all)
            timeframe: Data timeframe
            
        Returns:
            Dictionary of strategy_name: signal
        """
        if strategy_names is None:
            strategy_names = list(self.strategies.keys())
        
        signals = {}
        for strategy_name in strategy_names:
            try:
                signal = self.generate(strategy_name, symbol, timeframe)
                signals[strategy_name] = signal
            except Exception as e:
                signals[strategy_name] = {
                    'error': str(e),
                    'direction': Signal.FLAT,
                    'confidence': 0
                }
        
        return signals
