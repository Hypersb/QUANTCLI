"""
CLI interface for QuantCLI
Command-line interface using Typer
"""

import typer
from rich.console import Console
from rich.table import Table
from typing import Optional

app = typer.Typer(help="QuantCLI - Trading Research & Execution Toolkit")
console = Console()


@app.command()
def prices(
    symbol: str = typer.Argument(..., help="Trading pair symbol (e.g., BTC/USDT)")
):
    """Get current price for a symbol"""
    from quantcli.data.prices import get_current_price
    
    try:
        price_data = get_current_price(symbol)
        
        table = Table(title=f"Price Data: {symbol}")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Last Price", f"${price_data['last']:.2f}")
        table.add_row("Bid", f"${price_data['bid']:.2f}")
        table.add_row("Ask", f"${price_data['ask']:.2f}")
        table.add_row("Volume (24h)", f"{price_data['volume']:.2f}")
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]Error fetching price: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def portfolio():
    """View current portfolio"""
    from quantcli.broker.paper import paper_broker
    
    try:
        positions = paper_broker.get_positions()
        balance = paper_broker.get_balance()
        
        console.print(f"\n[bold cyan]Cash Balance:[/bold cyan] ${balance['USDT']:.2f}")
        
        if positions:
            table = Table(title="Open Positions")
            table.add_column("Symbol", style="cyan")
            table.add_column("Amount", style="green")
            table.add_column("Entry Price", style="yellow")
            table.add_column("Current PnL", style="magenta")
            
            for symbol, pos in positions.items():
                # TODO: Calculate current PnL
                table.add_row(
                    symbol,
                    f"{pos['amount']:.4f}",
                    f"${pos['entry_price']:.2f}",
                    "N/A"
                )
            
            console.print(table)
        else:
            console.print("[yellow]No open positions[/yellow]")
            
    except Exception as e:
        console.print(f"[red]Error fetching portfolio: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def buy(
    symbol: str = typer.Argument(..., help="Trading pair symbol"),
    amount: float = typer.Argument(..., help="Amount to buy")
):
    """Execute a buy order (paper trading)"""
    from quantcli.broker.paper import paper_broker
    
    try:
        order = paper_broker.buy(symbol, amount)
        
        console.print(f"[green]✓ Buy order executed[/green]")
        console.print(f"Symbol: {order['symbol']}")
        console.print(f"Amount: {order['amount']:.4f}")
        console.print(f"Price: ${order['price']:.2f}")
        console.print(f"Total: ${order['total']:.2f}")
        
    except Exception as e:
        console.print(f"[red]Error executing buy order: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def sell(
    symbol: str = typer.Argument(..., help="Trading pair symbol"),
    amount: float = typer.Argument(..., help="Amount to sell")
):
    """Execute a sell order (paper trading)"""
    from quantcli.broker.paper import paper_broker
    
    try:
        order = paper_broker.sell(symbol, amount)
        
        console.print(f"[green]✓ Sell order executed[/green]")
        console.print(f"Symbol: {order['symbol']}")
        console.print(f"Amount: {order['amount']:.4f}")
        console.print(f"Price: ${order['price']:.2f}")
        console.print(f"Total: ${order['total']:.2f}")
        
    except Exception as e:
        console.print(f"[red]Error executing sell order: {e}[/red]")
        raise typer.Exit(1)


# Signals sub-application
signals_app = typer.Typer(help="Signal generation commands")
app.add_typer(signals_app, name="signals")


@signals_app.command("run")
def signals_run(
    strategy: str = typer.Argument(..., help="Strategy name (rsi, ema, breakout)"),
    symbol: str = typer.Option("BTC/USDT", help="Trading pair symbol")
):
    """Generate trading signals using a strategy"""
    from quantcli.signals.engine import SignalEngine
    
    try:
        engine = SignalEngine()
        signal = engine.generate(strategy, symbol)
        
        # Color based on signal direction
        color = "green" if signal['direction'] == 'LONG' else "red" if signal['direction'] == 'SHORT' else "yellow"
        
        console.print(f"\n[bold {color}]Signal: {signal['direction']}[/bold {color}]")
        console.print(f"Strategy: {signal['strategy']}")
        console.print(f"Symbol: {signal['symbol']}")
        console.print(f"Confidence: {signal['confidence']:.1f}%")
        console.print(f"Reason: {signal['reason']}")
        
    except Exception as e:
        console.print(f"[red]Error generating signal: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def backtest(
    strategy: str = typer.Argument(..., help="Strategy name (rsi, ema, breakout)"),
    symbol: str = typer.Option("BTC/USDT", help="Trading pair symbol"),
    days: int = typer.Option(90, help="Number of days to backtest"),
    initial_capital: float = typer.Option(10000.0, help="Initial capital in USDT")
):
    """Backtest a strategy"""
    from quantcli.backtest.engine import BacktestEngine
    
    try:
        console.print(f"[cyan]Running backtest: {strategy} on {symbol}...[/cyan]\n")
        
        engine = BacktestEngine(
            strategy_name=strategy,
            symbol=symbol,
            initial_capital=initial_capital
        )
        
        results = engine.run(days=days)
        
        # Display results
        table = Table(title="Backtest Results")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Total Return", f"{results['total_return']:.2f}%")
        table.add_row("Total Trades", str(results['total_trades']))
        table.add_row("Win Rate", f"{results['win_rate']:.1f}%")
        table.add_row("Max Drawdown", f"{results['max_drawdown']:.2f}%")
        table.add_row("Sharpe Ratio", f"{results['sharpe_ratio']:.2f}")
        table.add_row("Final Equity", f"${results['final_equity']:.2f}")
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]Error running backtest: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def performance():
    """View performance analytics"""
    from quantcli.performance.analytics import PerformanceAnalytics
    
    try:
        analytics = PerformanceAnalytics()
        stats = analytics.get_summary()
        
        table = Table(title="Performance Summary")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Total Trades", str(stats['total_trades']))
        table.add_row("Total PnL", f"${stats['total_pnl']:.2f}")
        table.add_row("Win Rate", f"{stats['win_rate']:.1f}%")
        table.add_row("Avg Win", f"${stats['avg_win']:.2f}")
        table.add_row("Avg Loss", f"${stats['avg_loss']:.2f}")
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]Error fetching performance: {e}[/red]")
        raise typer.Exit(1)


# Config sub-application
config_app = typer.Typer(help="Configuration commands")
app.add_typer(config_app, name="config")


@config_app.command("show")
def config_show(
    name: Optional[str] = typer.Argument(None, help="Config name to show")
):
    """Show configuration"""
    from quantcli.utils.config import config_manager
    import json
    
    try:
        if name:
            config = config_manager.load(name)
            console.print(f"\n[bold cyan]Config: {name}[/bold cyan]")
            console.print(json.dumps(config, indent=2))
        else:
            console.print("[yellow]Available configs:[/yellow]")
            # TODO: List available configs
            console.print("- rsi_strategy")
            
    except Exception as e:
        console.print(f"[red]Error showing config: {e}[/red]")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
