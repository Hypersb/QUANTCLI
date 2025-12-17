# QuantCLI Usage Guide

## 🚀 Getting Started

### Installation

```bash
# Clone or navigate to the project directory
cd QuantCLI

# Install dependencies
pip install -r requirements.txt
```

### Verify Installation

```bash
# Check if CLI works
python main.py --help
```

## 📋 Command Reference

### 1. Check Prices

Get current price for a trading pair:

```bash
python main.py prices BTC/USDT
python main.py prices ETH/USDT
```

### 2. Portfolio Management

View your paper trading portfolio:

```bash
python main.py portfolio
```

### 3. Execute Trades (Paper Trading)

Buy:
```bash
python main.py buy BTC/USDT 0.01
```

Sell:
```bash
python main.py sell BTC/USDT 0.01
```

### 4. Generate Trading Signals

Generate a signal using a specific strategy:

```bash
python main.py signals run rsi
python main.py signals run ema
python main.py signals run breakout

# With custom symbol
python main.py signals run rsi --symbol ETH/USDT
```

### 5. Run Backtests

Backtest a strategy:

```bash
# Default: 90 days, BTC/USDT, $10k capital
python main.py backtest rsi

# Custom parameters
python main.py backtest ema --days 180 --symbol ETH/USDT --initial-capital 50000
```

### 6. View Performance

See performance analytics:

```bash
python main.py performance
```

### 7. Configuration

Show configuration:

```bash
python main.py config show
python main.py config show rsi_strategy
```

## 📚 Examples

### Example 1: Quick Price Check

```bash
python main.py prices BTC/USDT
```

Output:
```
┏━━━━━━━━━━━━━┳━━━━━━━━━━━┓
┃ Metric      ┃ Value     ┃
┡━━━━━━━━━━━━━╇━━━━━━━━━━━┩
│ Last Price  │ $43,250.00│
│ Bid         │ $43,248.50│
│ Ask         │ $43,251.50│
│ Volume (24h)│ 12,345.67 │
└─────────────┴───────────┘
```

### Example 2: Generate Signal

```bash
python main.py signals run rsi --symbol BTC/USDT
```

Output:
```
Signal: LONG
Strategy: rsi
Symbol: BTC/USDT
Confidence: 75.2%
Reason: RSI oversold: 28.5 < 30
```

### Example 3: Run Backtest

```bash
python main.py backtest rsi --days 90
```

Output:
```
┏━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┓
┃ Metric         ┃ Value     ┃
┡━━━━━━━━━━━━━━━━╇━━━━━━━━━━━┩
│ Total Return   │ 15.32%    │
│ Total Trades   │ 42        │
│ Win Rate       │ 58.5%     │
│ Max Drawdown   │ -8.45%    │
│ Sharpe Ratio   │ 1.23      │
│ Final Equity   │ $11,532.00│
└────────────────┴───────────┘
```

### Example 4: Paper Trading Workflow

```bash
# 1. Check current prices
python main.py prices BTC/USDT

# 2. Generate signal
python main.py signals run rsi --symbol BTC/USDT

# 3. If signal is bullish, buy
python main.py buy BTC/USDT 0.01

# 4. Check portfolio
python main.py portfolio

# 5. Later, when signal changes, sell
python main.py sell BTC/USDT 0.01
```

## 🔧 Advanced Usage

### Using Example Scripts

Run comprehensive examples:

```bash
# Compare all strategies
python examples/run_backtest.py

# Multi-strategy signal analysis
python examples/generate_signals.py

# Paper trading demo
python examples/paper_trading_demo.py
```

### Customizing Strategies

Edit configuration files in `configs/`:

- `rsi_strategy.yaml` - RSI parameters
- `ema_strategy.yaml` - EMA parameters
- `breakout_strategy.yaml` - Breakout parameters

Example customization:

```yaml
# configs/rsi_strategy.yaml
rsi_period: 14
oversold: 25      # More aggressive (was 30)
overbought: 75    # More aggressive (was 70)
stop_loss_pct: 1.5  # Tighter stop loss
```

## 💡 Tips

### Best Practices

1. **Start with Backtesting**: Always backtest strategies before paper trading
2. **Use Multiple Strategies**: Compare signals across strategies
3. **Monitor Performance**: Regularly check `python main.py performance`
4. **Adjust Configs**: Tune strategy parameters in config files
5. **Paper Trade First**: Never skip paper trading before going live

### Common Workflows

**Research Workflow:**
```bash
# 1. Backtest multiple strategies
python main.py backtest rsi --days 180
python main.py backtest ema --days 180
python main.py backtest breakout --days 180

# 2. Compare results
python examples/run_backtest.py

# 3. Choose best strategy
# 4. Fine-tune config
# 5. Re-test
```

**Daily Trading Workflow:**
```bash
# Morning routine
python main.py prices BTC/USDT
python main.py signals run rsi --symbol BTC/USDT
python main.py signals run ema --symbol BTC/USDT
python main.py portfolio

# Execute if signal is strong
python main.py buy BTC/USDT 0.01

# Evening check
python main.py portfolio
python main.py performance
```

## 🐛 Troubleshooting

### Issue: "No module named quantcli"

**Solution**: Make sure you're in the project root directory and have installed dependencies:
```bash
cd QuantCLI
pip install -r requirements.txt
```

### Issue: Exchange connection errors

**Solution**: Check your internet connection. CCXT requires internet access to fetch data.

### Issue: Insufficient data for backtesting

**Solution**: The exchange might not have enough historical data. Try:
- Using a different symbol
- Reducing the number of days
- Using a larger timeframe (e.g., 1h instead of 5m)

### Issue: Paper broker data persistence

**Solution**: Paper broker state is saved to `paper_broker_data.json`. To reset:
```python
from quantcli.broker.paper import paper_broker
paper_broker.reset()
```

## 📊 Understanding Results

### Backtest Metrics Explained

- **Total Return**: Percentage gain/loss from start to end
- **Win Rate**: Percentage of profitable trades
- **Max Drawdown**: Largest peak-to-trough decline
- **Sharpe Ratio**: Risk-adjusted return (>1 is good, >2 is excellent)
- **Profit Factor**: Gross profit / gross loss (>1.5 is good)

### Signal Confidence

- **70-100%**: Strong signal, high confidence
- **50-70%**: Moderate signal
- **0-50%**: Weak signal, low confidence

### Signal Directions

- **LONG**: Buy signal (expect price to go up)
- **SHORT**: Sell signal (expect price to go down)
- **FLAT**: No clear signal, stay in cash

## 🔐 Safety Notes

⚠️ **This is a research and learning tool**

- Paper trading by default
- No real money at risk
- Use for learning and strategy development
- Always backtest before live trading
- Past performance doesn't guarantee future results

## 📈 Next Steps

1. **Run Your First Backtest**: `python main.py backtest rsi`
2. **Explore Examples**: Check files in `examples/` directory
3. **Customize Strategies**: Edit configs in `configs/` directory
4. **Read the Code**: Understand how strategies work
5. **Experiment**: Try different parameters and symbols

Happy trading! 🚀
