# QuantCLI

A transparent, research-focused CLI trading toolkit for learning and experimentation.

## 🎯 Goals

- **Real, not hype**: No fake AI, no guaranteed returns
- **Learning-first**: Understand what's happening under the hood
- **Paper trading by default**: Safe experimentation
- **Reproducible research**: Config-driven strategies

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Check current price
python main.py prices BTC/USDT

# Run a backtest
python main.py backtest rsi

# View portfolio
python main.py portfolio
```

## 📋 Commands

- `prices SYMBOL` - Get current price
- `portfolio` - View current portfolio
- `buy SYMBOL AMOUNT` - Execute buy order (paper trading)
- `sell SYMBOL AMOUNT` - Execute sell order (paper trading)
- `signals run STRATEGY` - Generate trading signals
- `backtest STRATEGY` - Backtest a strategy
- `performance` - View performance metrics
- `config show` - Show current configuration

## 🧩 Features

### Market Data
- Real-time price fetching via CCXT
- Historical OHLCV data
- Multiple exchange support
- Data caching

### Strategies
- **RSI Mean Reversion**: Buy oversold, sell overbought
- **EMA Trend Following**: Follow moving average crossovers
- **Breakout**: Trade range breakouts

### Backtesting
- Bar-by-bar simulation
- Realistic fees & slippage
- Metrics: return, win rate, drawdown, Sharpe ratio
- Equity curve tracking

### Risk Management
- Fixed % position sizing
- ATR-based stop loss
- Max daily loss limits
- Risk per trade controls

### Paper Trading
- Simulated broker with realistic fills
- Track balances & positions
- Same interface as live broker (when added)

## 📁 Project Structure

```
quantcli/
├── quantcli/           # Core package
│   ├── cli.py          # CLI commands
│   ├── data/           # Market data
│   ├── strategies/     # Trading strategies
│   ├── signals/        # Signal generation
│   ├── backtest/       # Backtesting engine
│   ├── risk/           # Risk management
│   ├── broker/         # Broker abstraction
│   ├── performance/    # Analytics
│   └── utils/          # Utilities
├── configs/            # Strategy configs
├── examples/           # Usage examples
└── main.py             # Entry point
```

## ⚠️ Disclaimer

This is a **research and learning tool**. Paper trading by default. Use at your own risk.

## 🔮 Future Enhancements

- Light ML (logistic regression)
- TradingView webhooks
- Discord alerts
- Web dashboard

## 📄 License

MIT - Use freely, learn openly
