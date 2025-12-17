"""
Example: Generate and analyze signals

This script shows how to generate trading signals
for multiple strategies and symbols.
"""

from quantcli.signals.engine import SignalEngine
from rich.console import Console
from rich.table import Table

console = Console()


def generate_signal(strategy: str, symbol: str):
    """
    Generate a signal for a strategy and symbol
    
    Args:
        strategy: Strategy name
        symbol: Trading pair
    """
    engine = SignalEngine()
    signal = engine.generate(strategy, symbol)
    
    # Color based on direction
    if signal['direction'] == 'LONG':
        color = "green"
    elif signal['direction'] == 'SHORT':
        color = "red"
    else:
        color = "yellow"
    
    console.print(f"\n[bold {color}]{strategy.upper()} - {symbol}[/bold {color}]")
    console.print(f"Direction: {signal['direction']}")
    console.print(f"Confidence: {signal['confidence']:.1f}%")
    console.print(f"Reason: {signal['reason']}")
    
    if signal['entry_price']:
        console.print(f"Entry: ${signal['entry_price']:.2f}")
    if signal['stop_loss']:
        console.print(f"Stop Loss: ${signal['stop_loss']:.2f}")
    if signal['take_profit']:
        console.print(f"Take Profit: ${signal['take_profit']:.2f}")
    
    return signal


def multi_strategy_analysis(symbol: str):
    """
    Analyze signals from all strategies for a symbol
    
    Args:
        symbol: Trading pair
    """
    console.print(f"\n[bold cyan]Multi-Strategy Analysis: {symbol}[/bold cyan]\n")
    
    engine = SignalEngine()
    signals = engine.generate_multiple(symbol)
    
    table = Table(title=f"Signals for {symbol}")
    table.add_column("Strategy", style="cyan")
    table.add_column("Direction", style="yellow")
    table.add_column("Confidence", style="green")
    table.add_column("Reason")
    
    for strategy, signal in signals.items():
        # Color direction
        direction = signal['direction']
        if direction == 'LONG':
            direction = f"[green]{direction}[/green]"
        elif direction == 'SHORT':
            direction = f"[red]{direction}[/red]"
        else:
            direction = f"[yellow]{direction}[/yellow]"
        
        table.add_row(
            strategy.upper(),
            direction,
            f"{signal['confidence']:.0f}%",
            signal['reason'][:50]  # Truncate long reasons
        )
    
    console.print(table)
    
    # Consensus analysis
    directions = [s['direction'] for s in signals.values()]
    longs = directions.count('LONG')
    shorts = directions.count('SHORT')
    flats = directions.count('FLAT')
    
    console.print(f"\n[bold]Consensus:[/bold]")
    console.print(f"  LONG: {longs}")
    console.print(f"  SHORT: {shorts}")
    console.print(f"  FLAT: {flats}")
    
    if longs > shorts and longs > flats:
        console.print("\n[bold green]→ Bullish consensus[/bold green]")
    elif shorts > longs and shorts > flats:
        console.print("\n[bold red]→ Bearish consensus[/bold red]")
    else:
        console.print("\n[bold yellow]→ No clear consensus[/bold yellow]")


if __name__ == "__main__":
    # Example 1: Generate single signal
    console.print("[bold]Example 1: Single Signal[/bold]")
    generate_signal('rsi', 'BTC/USDT')
    
    # Example 2: Multi-strategy analysis
    console.print("\n[bold]Example 2: Multi-Strategy Analysis[/bold]")
    multi_strategy_analysis('BTC/USDT')
    
    # Example 3: Multiple symbols
    console.print("\n[bold]Example 3: Multiple Symbols (RSI Strategy)[/bold]")
    symbols = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT']
    
    for symbol in symbols:
        try:
            generate_signal('rsi', symbol)
        except Exception as e:
            console.print(f"[red]Error with {symbol}: {e}[/red]")
