# QuantCLI Quick Start Guide

## ⚡ 5-Minute Setup

### Step 1: Install Dependencies (1 min)

```bash
pip install -r requirements.txt
```

### Step 2: Check Installation (30 sec)

```bash
python main.py --help
```

You should see the QuantCLI help menu.

### Step 3: Your First Command (1 min)

Check Bitcoin price:

```bash
python main.py prices BTC/USDT
```

### Step 4: Generate a Signal (1 min)

Get a trading signal using RSI strategy:

```bash
python main.py signals run rsi
```

### Step 5: Run Your First Backtest (2 min)

Test the RSI strategy over 90 days:

```bash
python main.py backtest rsi
```

## 🎯 What's Next?

### Option 1: Paper Trade

```bash
# Buy some BTC
python main.py buy BTC/USDT 0.01

# Check your portfolio
python main.py portfolio

# Sell when ready
python main.py sell BTC/USDT 0.01
```

### Option 2: Compare Strategies

```bash
python examples/run_backtest.py
```

### Option 3: Multi-Strategy Analysis

```bash
python examples/generate_signals.py
```

## 📖 Learn More

- Read [USAGE.md](USAGE.md) for detailed documentation
- Check [README.md](README.md) for project overview
- Explore [roadmap.md](roadmap.md) for future plans

## 🆘 Need Help?

**Common Issues:**

1. **"No module found"** → Run `pip install -r requirements.txt`
2. **"Exchange error"** → Check internet connection
3. **"Config not found"** → Configs are in `configs/` folder

## 💡 Pro Tips

- Start with backtesting before paper trading
- Use multiple strategies for confirmation
- Customize configs in `configs/` folder
- Check performance regularly with `python main.py performance`

---

**Ready to dive deeper?** Check out [USAGE.md](USAGE.md) for comprehensive examples and tutorials.
