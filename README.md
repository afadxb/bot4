# Adaptive SP100 Scoring Hold Bot

Adaptive, regime-aware trading bot for the S&P 100. The bot scans hourly, scores entries on blended daily/4H factors, confirms exits with 1H acceleration, and manages orders with profit targets and trails.

```
Scan → Score → Sentiment → Support → Order → Manage
```

## Components

* `scheduler.py` – schedules hourly runs and 4H tasks
* `scoring/` – entry, exit and regime scoring logic
* `risk/` – position sizing and stop helpers
* `alerts/` – optional push notifications
* `bot.py` – ties data fetching, scoring and order placement together

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
cp .env.example .env
```

Configure the `.env` then launch the Interactive Brokers TWS/Gateway. The default configuration uses SQLite; switch `DB_URL` to a MySQL URL if desired.

## Universe

By default the bot loads `sp100.csv`. Update this file to refresh the S&P 100 list.

## Running

```
python -m main
```

This launches the main trading loop. The bot loads the configured
universe, pulls market data, evaluates entry and exit signals and sends
orders through the broker stub while tracking position state.

## Dashboard

```bash
streamlit run dashboard.py
```

## Backtests

```
python -m backtest.engine
```

## Safety

The project is paper-trade ready. Review code and run in a simulated account before any live deployment.

## Troubleshooting

* Ensure TWS/Gateway is running and API is enabled.
* Check time zone alignment and market hours.
* Beware IBKR pacing limits when requesting large amounts of data.
