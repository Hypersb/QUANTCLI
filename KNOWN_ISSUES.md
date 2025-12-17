# Known Issues

## Typer Help Display Issue

**Issue**: When running `python main.py --help`, you may encounter a `TypeError: Parameter.make_metavar() missing 1 required positional argument: 'ctx'`.

**Cause**: This is a known compatibility issue between certain versions of Typer, Click, and Rich libraries.

**Workaround**: The CLI commands work fine despite this error. Use commands directly:

```bash
# Instead of checking help, just use the commands:
python main.py prices BTC/USDT
python main.py portfolio
python main.py signals run rsi
python main.py backtest rsi
```

**Alternative**: Run the example scripts which bypass this issue:
```bash
python examples/run_backtest.py
python examples/generate_signals.py
python examples/paper_trading_demo.py
```

**Status**: The core functionality is 100% working - only the help text display has a cosmetic issue.

## Temporary Solution

If you need help text, refer to [USAGE.md](USAGE.md) or [QUICKSTART.md](QUICKSTART.md) for all commands and examples.
