"""
Example: Paper trading workflow

This script demonstrates a complete paper trading workflow:
1. Check prices
2. Generate signals
3. Execute trades
4. Monitor portfolio
"""

from quantcli.data.prices import get_current_price
from quantcli.signals.engine import SignalEngine
from quantcli.broker.paper import paper_broker
from rich.console import Console
import time

console = Console()


def check_prices(symbols: list):
    """Check current prices for multiple symbols"""
    console.print("\n[bold cyan]Current Prices[/bold cyan]")
    
    for symbol in symbols:
        try:
            price_data = get_current_price(symbol)
            console.print(f"{symbol}: ${price_data['last']:.2f}")
        except Exception as e:
            console.print(f"[red]{symbol}: Error - {e}[/red]")


def generate_signals(symbols: list, strategy: str = 'rsi'):
    """Generate signals for multiple symbols"""
    console.print(f"\n[bold cyan]Signals ({strategy.upper()})[/bold cyan]")
    
    engine = SignalEngine()
    signals = {}
    
    for symbol in symbols:
        try:
            signal = engine.generate(strategy, symbol)
            signals[symbol] = signal
            
            # Display signal
            direction = signal['direction']
            color = "green" if direction == 'LONG' else "red" if direction == 'SHORT' else "yellow"
            console.print(f"{symbol}: [{color}]{direction}[/{color}] ({signal['confidence']:.0f}%)")
        except Exception as e:
            console.print(f"[red]{symbol}: Error - {e}[/red]")
    
    return signals


def execute_trades(signals: dict):
    """Execute trades based on signals"""
    console.print("\n[bold cyan]Executing Trades[/bold cyan]")
    
    for symbol, signal in signals.items():
        try:
            # Only trade on high-confidence signals
            if signal['confidence'] < 70:
                console.print(f"{symbol}: Skipping (low confidence)")
                continue
            
            if signal['direction'] == 'LONG':
                # Buy with fixed position size
                amount = 0.01  # Example: 0.01 BTC
                order = paper_broker.buy(symbol, amount)
                console.print(f"[green]✓ Bought {amount} {symbol} @ ${order['price']:.2f}[/green]")
            
            elif signal['direction'] == 'SHORT':
                # Check if we have position to sell
                positions = paper_broker.get_positions()
                if symbol in positions:
                    amount = positions[symbol]['amount']
                    order = paper_broker.sell(symbol, amount)
                    console.print(f"[green]✓ Sold {amount} {symbol} @ ${order['price']:.2f}[/green]")
                else:
                    console.print(f"{symbol}: No position to sell")
        
        except Exception as e:
            console.print(f"[red]{symbol}: Trade error - {e}[/red]")


def show_portfolio():
    """Display current portfolio"""
    console.print("\n[bold cyan]Portfolio Status[/bold cyan]")
    
    balance = paper_broker.get_balance()
    positions = paper_broker.get_positions()
    
    console.print(f"Cash: ${balance.get('USDT', 0):.2f}")
    
    if positions:
        console.print("\nPositions:")
        for symbol, pos in positions.items():
            console.print(f"  {symbol}: {pos['amount']:.4f} @ ${pos['entry_price']:.2f}")
    else:
        console.print("No open positions")


def paper_trading_session():
    """Run a complete paper trading session"""
    console.print("[bold yellow]═══════════════════════════════════[/bold yellow]")
    console.print("[bold yellow]   QuantCLI Paper Trading Session   [/bold yellow]")
    console.print("[bold yellow]═══════════════════════════════════[/bold yellow]")
    
    # Define symbols to trade
    symbols = ['BTC/USDT', 'ETH/USDT']
    
    # Step 1: Check prices
    check_prices(symbols)
    
    # Step 2: Generate signals
    signals = generate_signals(symbols, strategy='rsi')
    
    # Step 3: Execute trades
    execute_trades(signals)
    
    # Step 4: Show portfolio
    show_portfolio()
    
    console.print("\n[bold green]✓ Trading session complete[/bold green]")


if __name__ == "__main__":
    # Reset broker for clean demo (optional)
    # paper_broker.reset()
    
    # Run trading session
    paper_trading_session()
