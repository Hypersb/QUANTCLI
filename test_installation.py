"""
Installation test script
Verifies that QuantCLI is properly installed and configured
"""

import sys
from rich.console import Console
from rich.panel import Panel

console = Console()


def test_imports():
    """Test that all modules can be imported"""
    console.print("\n[cyan]Testing imports...[/cyan]")
    
    tests = [
        ("quantcli", "Core package"),
        ("quantcli.cli", "CLI module"),
        ("quantcli.data.prices", "Price service"),
        ("quantcli.data.history", "History service"),
        ("quantcli.strategies.rsi", "RSI strategy"),
        ("quantcli.strategies.ema", "EMA strategy"),
        ("quantcli.strategies.breakout", "Breakout strategy"),
        ("quantcli.signals.engine", "Signal engine"),
        ("quantcli.backtest.engine", "Backtest engine"),
        ("quantcli.broker.paper", "Paper broker"),
        ("quantcli.risk.position", "Risk manager"),
        ("quantcli.performance.analytics", "Performance analytics"),
    ]
    
    failed = []
    for module_name, description in tests:
        try:
            __import__(module_name)
            console.print(f"  ✓ {description}: [green]OK[/green]")
        except ImportError as e:
            console.print(f"  ✗ {description}: [red]FAILED[/red]")
            failed.append((module_name, str(e)))
    
    return len(failed) == 0, failed


def test_dependencies():
    """Test that required dependencies are installed"""
    console.print("\n[cyan]Testing dependencies...[/cyan]")
    
    deps = [
        "typer",
        "rich",
        "pandas",
        "numpy",
        "yaml",
        "ccxt",
    ]
    
    failed = []
    for dep in deps:
        try:
            __import__(dep)
            console.print(f"  ✓ {dep}: [green]OK[/green]")
        except ImportError:
            console.print(f"  ✗ {dep}: [red]MISSING[/red]")
            failed.append(dep)
    
    return len(failed) == 0, failed


def test_configs():
    """Test that config files exist"""
    console.print("\n[cyan]Testing configuration files...[/cyan]")
    
    from pathlib import Path
    
    configs = [
        "configs/rsi_strategy.yaml",
        "configs/ema_strategy.yaml",
        "configs/breakout_strategy.yaml",
    ]
    
    failed = []
    for config_file in configs:
        path = Path(config_file)
        if path.exists():
            console.print(f"  ✓ {config_file}: [green]OK[/green]")
        else:
            console.print(f"  ✗ {config_file}: [red]MISSING[/red]")
            failed.append(config_file)
    
    return len(failed) == 0, failed


def test_basic_functionality():
    """Test basic functionality"""
    console.print("\n[cyan]Testing basic functionality...[/cyan]")
    
    tests_passed = True
    
    # Test 1: Can create signal engine
    try:
        from quantcli.signals.engine import SignalEngine
        engine = SignalEngine()
        console.print(f"  ✓ Signal engine creation: [green]OK[/green]")
    except Exception as e:
        console.print(f"  ✗ Signal engine creation: [red]FAILED[/red] - {e}")
        tests_passed = False
    
    # Test 2: Can create paper broker
    try:
        from quantcli.broker.paper import PaperBroker
        broker = PaperBroker(initial_capital=10000.0, data_file="test_broker.json")
        console.print(f"  ✓ Paper broker creation: [green]OK[/green]")
        
        # Cleanup
        import os
        if os.path.exists("test_broker.json"):
            os.remove("test_broker.json")
    except Exception as e:
        console.print(f"  ✗ Paper broker creation: [red]FAILED[/red] - {e}")
        tests_passed = False
    
    # Test 3: Can load strategies
    try:
        from quantcli.strategies.rsi import RSIStrategy
        from quantcli.strategies.ema import EMAStrategy
        from quantcli.strategies.breakout import BreakoutStrategy
        
        rsi = RSIStrategy()
        ema = EMAStrategy()
        breakout = BreakoutStrategy()
        console.print(f"  ✓ Strategy loading: [green]OK[/green]")
    except Exception as e:
        console.print(f"  ✗ Strategy loading: [red]FAILED[/red] - {e}")
        tests_passed = False
    
    return tests_passed


def main():
    """Run all tests"""
    console.print(Panel.fit(
        "[bold yellow]QuantCLI Installation Test[/bold yellow]\n"
        "Verifying installation and configuration",
        border_style="yellow"
    ))
    
    all_passed = True
    
    # Test imports
    imports_ok, import_failures = test_imports()
    if not imports_ok:
        all_passed = False
        console.print("\n[red]Import failures:[/red]")
        for module, error in import_failures:
            console.print(f"  - {module}: {error}")
    
    # Test dependencies
    deps_ok, dep_failures = test_dependencies()
    if not deps_ok:
        all_passed = False
        console.print("\n[red]Missing dependencies:[/red]")
        for dep in dep_failures:
            console.print(f"  - {dep}")
        console.print("\n[yellow]Run: pip install -r requirements.txt[/yellow]")
    
    # Test configs
    configs_ok, config_failures = test_configs()
    if not configs_ok:
        all_passed = False
        console.print("\n[red]Missing config files:[/red]")
        for config in config_failures:
            console.print(f"  - {config}")
    
    # Test functionality
    func_ok = test_basic_functionality()
    if not func_ok:
        all_passed = False
    
    # Final result
    console.print("\n" + "="*50)
    if all_passed:
        console.print(Panel.fit(
            "[bold green]✓ All tests passed![/bold green]\n"
            "QuantCLI is properly installed and ready to use.\n\n"
            "Next steps:\n"
            "  • python main.py --help\n"
            "  • python main.py prices BTC/USDT\n"
            "  • python main.py backtest rsi",
            border_style="green"
        ))
        return 0
    else:
        console.print(Panel.fit(
            "[bold red]✗ Some tests failed[/bold red]\n"
            "Please check the errors above and fix them.\n\n"
            "Common fixes:\n"
            "  • pip install -r requirements.txt\n"
            "  • Make sure you're in the project root",
            border_style="red"
        ))
        return 1


if __name__ == "__main__":
    sys.exit(main())
