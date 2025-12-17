"""
Example: Run a backtest with different strategies

This script demonstrates how to run backtests programmatically
and compare strategy performance.
"""

from quantcli.backtest.engine import BacktestEngine
from rich.console import Console
from rich.table import Table

console = Console()


def run_backtest(strategy_name: str, symbol: str = 'BTC/USDT', days: int = 90):
    """
    Run a backtest for a strategy
    
    Args:
        strategy_name: Name of strategy (rsi, ema, breakout)
        symbol: Trading pair
        days: Number of days to backtest
    """
    console.print(f"\n[cyan]Running backtest: {strategy_name}[/cyan]")
    
    engine = BacktestEngine(
        strategy_name=strategy_name,
        symbol=symbol,
        initial_capital=10000.0
    )
    
    results = engine.run(days=days)
    
    # Display results
    table = Table(title=f"{strategy_name.upper()} Backtest Results")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Total Return", f"{results['total_return']:.2f}%")
    table.add_row("Total Trades", str(results['total_trades']))
    table.add_row("Win Rate", f"{results['win_rate']:.1f}%")
    table.add_row("Max Drawdown", f"{results['max_drawdown']:.2f}%")
    table.add_row("Sharpe Ratio", f"{results['sharpe_ratio']:.2f}")
    table.add_row("Profit Factor", f"{results['profit_factor']:.2f}")
    table.add_row("Final Equity", f"${results['final_equity']:.2f}")
    
    console.print(table)
    
    return results


def compare_strategies(symbol: str = 'BTC/USDT', days: int = 90):
    """
    Compare multiple strategies
    
    Args:
        symbol: Trading pair
        days: Number of days to backtest
    """
    strategies = ['rsi', 'ema', 'breakout']
    results_all = {}
    
    console.print("\n[bold yellow]Strategy Comparison[/bold yellow]")
    console.print(f"Symbol: {symbol}")
    console.print(f"Period: {days} days")
    console.print(f"Initial Capital: $10,000\n")
    
    for strategy in strategies:
        try:
            results = run_backtest(strategy, symbol, days)
            results_all[strategy] = results
        except Exception as e:
            console.print(f"[red]Error with {strategy}: {e}[/red]")
    
    # Summary comparison
    if results_all:
        console.print("\n[bold cyan]Summary Comparison[/bold cyan]")
        
        comparison_table = Table()
        comparison_table.add_column("Strategy", style="cyan")
        comparison_table.add_column("Return %", style="green")
        comparison_table.add_column("Sharpe", style="yellow")
        comparison_table.add_column("Trades", style="blue")
        comparison_table.add_column("Win Rate %", style="magenta")
        
        for strategy, results in results_all.items():
            comparison_table.add_row(
                strategy.upper(),
                f"{results['total_return']:.2f}",
                f"{results['sharpe_ratio']:.2f}",
                str(results['total_trades']),
                f"{results['win_rate']:.1f}"
            )
        
        console.print(comparison_table)
        
        # Find best strategy
        best_strategy = max(results_all.items(), key=lambda x: x[1]['total_return'])
        console.print(f"\n[bold green]Best Strategy: {best_strategy[0].upper()} "
                     f"({best_strategy[1]['total_return']:.2f}% return)[/bold green]")


if __name__ == "__main__":
    # Example 1: Run single backtest
    console.print("[bold]Example 1: Single Strategy Backtest[/bold]")
    run_backtest('rsi', 'BTC/USDT', 90)
    
    # Example 2: Compare all strategies
    console.print("\n[bold]Example 2: Compare All Strategies[/bold]")
    compare_strategies('BTC/USDT', 90)
