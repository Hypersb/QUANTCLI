"""
Paper trading broker
Simulates trading without real money
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json
from pathlib import Path

from quantcli.broker.base import BaseBroker, Order


class PaperBroker(BaseBroker):
    """
    Paper trading broker for simulation
    Tracks positions and balances in memory
    """
    
    def __init__(self, initial_capital: float = 10000.0, data_file: str = "paper_broker_data.json"):
        """
        Initialize paper broker
        
        Args:
            initial_capital: Starting capital in USDT
            data_file: File to persist broker state
        """
        self.data_file = Path(data_file)
        self.initial_capital = initial_capital
        
        # Try to load existing state
        if self.data_file.exists():
            self._load_state()
        else:
            self._initialize_state()
    
    def _initialize_state(self):
        """Initialize fresh broker state"""
        self.balance = {'USDT': self.initial_capital}
        self.positions: Dict[str, Dict[str, Any]] = {}
        self.order_history: List[Dict[str, Any]] = []
        self._save_state()
    
    def _load_state(self):
        """Load broker state from file"""
        with open(self.data_file, 'r') as f:
            data = json.load(f)
        
        self.balance = data.get('balance', {'USDT': self.initial_capital})
        self.positions = data.get('positions', {})
        self.order_history = data.get('order_history', [])
    
    def _save_state(self):
        """Save broker state to file"""
        data = {
            'balance': self.balance,
            'positions': self.positions,
            'order_history': self.order_history
        }
        
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _get_current_price(self, symbol: str) -> float:
        """Get current market price for symbol"""
        from quantcli.data.prices import get_current_price
        
        price_data = get_current_price(symbol)
        return price_data['last']
    
    def buy(self, symbol: str, amount: float, price: Optional[float] = None) -> Dict[str, Any]:
        """
        Execute a buy order
        
        Args:
            symbol: Trading pair (e.g., 'BTC/USDT')
            amount: Amount to buy
            price: Limit price (None for market order)
            
        Returns:
            Order details
        """
        # Get market price if not specified
        if price is None:
            price = self._get_current_price(symbol)
        
        # Calculate total cost (with 0.1% fee)
        fee_rate = 0.001
        cost = amount * price
        total_cost = cost * (1 + fee_rate)
        
        # Check balance
        if self.balance.get('USDT', 0) < total_cost:
            raise ValueError(f"Insufficient balance. Need ${total_cost:.2f}, have ${self.balance.get('USDT', 0):.2f}")
        
        # Execute order
        self.balance['USDT'] -= total_cost
        
        # Extract base currency from symbol (e.g., 'BTC' from 'BTC/USDT')
        base_currency = symbol.split('/')[0]
        
        # Update or create position
        if symbol in self.positions:
            # Average down the position
            pos = self.positions[symbol]
            total_amount = pos['amount'] + amount
            avg_price = (pos['entry_price'] * pos['amount'] + price * amount) / total_amount
            
            self.positions[symbol] = {
                'amount': total_amount,
                'entry_price': avg_price,
                'timestamp': datetime.now().isoformat()
            }
        else:
            self.positions[symbol] = {
                'amount': amount,
                'entry_price': price,
                'timestamp': datetime.now().isoformat()
            }
        
        # Record order
        order = Order(symbol, 'buy', amount, price)
        self.order_history.append(order.to_dict())
        
        self._save_state()
        
        return order.to_dict()
    
    def sell(self, symbol: str, amount: float, price: Optional[float] = None) -> Dict[str, Any]:
        """
        Execute a sell order
        
        Args:
            symbol: Trading pair
            amount: Amount to sell
            price: Limit price (None for market order)
            
        Returns:
            Order details
        """
        # Check if we have the position
        if symbol not in self.positions:
            raise ValueError(f"No position in {symbol}")
        
        position = self.positions[symbol]
        if position['amount'] < amount:
            raise ValueError(f"Insufficient position. Have {position['amount']:.4f}, trying to sell {amount:.4f}")
        
        # Get market price if not specified
        if price is None:
            price = self._get_current_price(symbol)
        
        # Calculate proceeds (with 0.1% fee)
        fee_rate = 0.001
        proceeds = amount * price
        net_proceeds = proceeds * (1 - fee_rate)
        
        # Execute order
        self.balance['USDT'] = self.balance.get('USDT', 0) + net_proceeds
        
        # Update position
        position['amount'] -= amount
        
        if position['amount'] < 0.0001:  # Close position if near zero
            del self.positions[symbol]
        
        # Record order
        order = Order(symbol, 'sell', amount, price)
        self.order_history.append(order.to_dict())
        
        self._save_state()
        
        return order.to_dict()
    
    def get_balance(self) -> Dict[str, float]:
        """Get current balance"""
        return self.balance.copy()
    
    def get_positions(self) -> Dict[str, Dict[str, Any]]:
        """Get current positions"""
        return self.positions.copy()
    
    def get_order_history(self) -> List[Dict[str, Any]]:
        """Get order history"""
        return self.order_history.copy()
    
    def reset(self):
        """Reset broker to initial state"""
        self._initialize_state()


# Global paper broker instance
paper_broker = PaperBroker()
