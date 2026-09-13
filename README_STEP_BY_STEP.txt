
TRADINGVIEW ROMAN URDU AI ANALYST — DEMO v2

What this package does
----------------------
1) Receives structured TradingView alert data through /webhook/tradingview.
2) Calculates a simple educational market-analysis bias using EMA, RSI, MACD,
   trend and market structure.
3) Shows a mobile-friendly dashboard.
4) Provides Roman Urdu "Why?" explanations and a Roman Urdu chat box.
5) Shows possible bullish/bearish scenarios.
6) Includes a Pine Script bridge that sends indicator data in JSON.

Important limitation
--------------------
This is a DEMO / PAPER-ANALYSIS tool. It does NOT place broker orders,
does not contain broker passwords, and has no live-money execution code.
Signals are not guaranteed predictions or financial advice.

PC setup
--------
1) Install Python 3.11+ on Windows.
2) Open this folder in Command Prompt.
3) Run:
       pip install -r requirements.txt
4) Start:
       python app.py
5) On the same PC open:
       http://127.0.0.1:5000

TradingView connection
---------------------
TradingView webhooks POST alert messages to your public HTTPS endpoint.
TradingView requires 2FA for webhooks, and webhook requests use ports 80/443.
The receiving server should respond quickly.

For a real connection you need a public HTTPS URL for:
       https://YOUR-DOMAIN/webhook/tradingview

Then:
1) Open TradingView.
2) Add the Pine script from pine/roman_urdu_bridge.pine.
3) Create an alert for that script.
4) Choose the script's alert() function calls.
5) Add your HTTPS webhook URL.
6) Use "Once Per Bar Close" behavior from the script.
7) Do NOT put passwords, broker credentials, API keys or other secrets in
   the TradingView alert message.

Testing without TradingView
---------------------------
POST JSON to:
       http://127.0.0.1:5000/api/demo

Example:
{
  "symbol":"XAUUSD",
  "timeframe":"15m",
  "price":4349.42,
  "trend":"Bullish",
  "market_structure":"Higher High / Higher Low",
  "rsi":58.4,
  "macd":12.3,
  "macd_signal":8.4,
  "ema20":4346.1,
  "ema50":4340.2,
  "ema200":4315.6,
  "atr":12.3,
  "pattern":"Ascending Triangle (possible breakout)",
  "support":"4330-4320",
  "resistance":"4355-4380"
}

The dashboard is designed to be opened from a phone browser when the PC/server
is reachable. A public HTTPS deployment is required for TradingView webhooks.

No trading execution
--------------------
Keep this package for learning, chart analysis and paper/demo scenarios.
