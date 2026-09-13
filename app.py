
from flask import Flask, request, jsonify, render_template
from threading import Lock
from datetime import datetime, timezone

app = Flask(__name__)
state_lock = Lock()

STATE = {
    "symbol": "XAUUSD",
    "exchange": "TradingView",
    "timeframe": "15m",
    "price": None,
    "trend": "Unknown",
    "market_structure": "Unknown",
    "rsi": None,
    "macd": None,
    "ema20": None,
    "ema50": None,
    "ema200": None,
    "atr": None,
    "support": None,
    "resistance": None,
    "pattern": "No pattern received",
    "volume": None,
    "signal": "WAIT",
    "confidence": 0,
    "why": "TradingView se data ka wait ho raha hai.",
    "scenario_up": "Data aane ke baad scenario banega.",
    "scenario_down": "Data aane ke baad scenario banega.",
    "updated": "Never"
}

def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None

def analyze(d):
    price = num(d.get("price", d.get("close")))
    rsi = num(d.get("rsi"))
    macd = num(d.get("macd"))
    signal = num(d.get("macd_signal"))
    ema20 = num(d.get("ema20"))
    ema50 = num(d.get("ema50"))
    ema200 = num(d.get("ema200"))
    trend = str(d.get("trend", "")).lower()
    structure = str(d.get("market_structure", "")).lower()
    pattern = str(d.get("pattern", "No clear pattern"))

    bull = 0
    bear = 0
    reasons = []

    if price is not None and ema20 is not None:
        if price > ema20:
            bull += 1
            reasons.append("price EMA20 ke upar hai")
        else:
            bear += 1
            reasons.append("price EMA20 ke neeche hai")

    if ema20 is not None and ema50 is not None:
        if ema20 > ema50:
            bull += 1
            reasons.append("EMA20, EMA50 ke upar hai")
        else:
            bear += 1
            reasons.append("EMA20, EMA50 ke neeche hai")

    if ema50 is not None and ema200 is not None:
        if ema50 > ema200:
            bull += 1
            reasons.append("EMA50, EMA200 ke upar hai")
        else:
            bear += 1
            reasons.append("EMA50, EMA200 ke neeche hai")

    if rsi is not None:
        if 50 < rsi < 70:
            bull += 1
            reasons.append(f"RSI {rsi:.1f} bullish zone mein hai")
        elif rsi < 45:
            bear += 1
            reasons.append(f"RSI {rsi:.1f} weak zone mein hai")
        else:
            reasons.append(f"RSI {rsi:.1f} neutral/transition zone mein hai")

    if macd is not None and signal is not None:
        if macd > signal:
            bull += 1
            reasons.append("MACD signal line ke upar hai")
        else:
            bear += 1
            reasons.append("MACD signal line ke neeche hai")

    if "bull" in trend or "up" in trend:
        bull += 1
        reasons.append("overall trend bullish hai")
    elif "bear" in trend or "down" in trend:
        bear += 1
        reasons.append("overall trend bearish hai")

    if "higher high" in structure or "higher low" in structure:
        bull += 1
        reasons.append("market structure HH/HL side par hai")
    elif "lower high" in structure or "lower low" in structure:
        bear += 1
        reasons.append("market structure LH/LL side par hai")

    total = bull + bear
    if total == 0:
        sig, conf = "WAIT", 0
    elif bull >= bear + 2:
        sig, conf = "BUY BIAS", min(90, 50 + bull * 7)
    elif bear >= bull + 2:
        sig, conf = "SELL BIAS", min(90, 50 + bear * 7)
    else:
        sig, conf = "WAIT", 50 + min(15, abs(bull - bear) * 5)

    why = " | ".join(reasons[-5:]) if reasons else "Abhi enough data nahi mila."
    if sig == "BUY BIAS":
        why = "BUY bias ki wajah: " + why + ". Lekin ye confirmation nahi hai."
    elif sig == "SELL BIAS":
        why = "SELL bias ki wajah: " + why + ". Lekin ye confirmation nahi hai."
    else:
        why = "WAIT ki wajah: bullish aur bearish signals mixed hain. " + why

    res = d.get("resistance")
    sup = d.get("support")
    up = f"Agar resistance decisively break ho aur momentum support kare, bullish continuation possible ho sakti hai. Resistance: {res or 'unknown'}."
    down = f"Agar support decisively break ho aur selling momentum aaye, bearish continuation possible ho sakti hai. Support: {sup or 'unknown'}."

    return {
        "symbol": d.get("symbol", STATE["symbol"]),
        "exchange": d.get("exchange", "TradingView"),
        "timeframe": d.get("timeframe", STATE["timeframe"]),
        "price": price,
        "trend": d.get("trend", "Unknown"),
        "market_structure": d.get("market_structure", "Unknown"),
        "rsi": rsi,
        "macd": macd,
        "ema20": ema20,
        "ema50": ema50,
        "ema200": ema200,
        "atr": num(d.get("atr")),
        "support": sup,
        "resistance": res,
        "pattern": pattern,
        "volume": d.get("volume"),
        "signal": sig,
        "confidence": conf,
        "why": why,
        "scenario_up": up,
        "scenario_down": down,
        "updated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    }

@app.get("/")
def home():
    return render_template("index.html")

@app.get("/api/state")
def api_state():
    with state_lock:
        return jsonify(STATE)

@app.post("/webhook/tradingview")
def tradingview_webhook():
    # TradingView can POST valid JSON. Do not put passwords/API keys in alert messages.
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"ok": False, "error": "JSON body required"}), 400

    new_state = analyze(data)
    with state_lock:
        STATE.update(new_state)
    return jsonify({"ok": True, "signal": STATE["signal"]}), 200

@app.post("/api/demo")
def demo():
    data = request.get_json(silent=True) or {}
    new_state = analyze(data)
    with state_lock:
        STATE.update(new_state)
    return jsonify({"ok": True, "state": STATE})

@app.post("/api/chat")
def chat():
    body = request.get_json(silent=True) or {}
    q = str(body.get("question", "")).strip().lower()
    s = STATE

    if not q:
        return jsonify({"answer": "Sawal likho, jaise: 'Abhi WAIT kyun hai?'."})

    if "kyun" in q or "why" in q or "buy" in q or "sell" in q:
        ans = s["why"]
    elif "pattern" in q or "candle" in q:
        ans = f"Current pattern: {s['pattern']}. Pattern akela decision nahi hota; trend, momentum aur levels ke saath confirm karna hota hai."
    elif "rsi" in q:
        ans = f"RSI abhi {s['rsi'] if s['rsi'] is not None else 'available nahi'} hai. RSI ko context ke saath dekho; single indicator ko standalone signal na samjho."
    elif "scenario" in q or "next" in q:
        ans = f"Upar wala scenario: {s['scenario_up']} Neeche wala scenario: {s['scenario_down']}"
    elif "support" in q or "resistance" in q:
        ans = f"Support: {s['support'] or 'unknown'} | Resistance: {s['resistance'] or 'unknown'}."
    else:
        ans = f"Current state: {s['signal']} ({s['confidence']}%). {s['why']}"

    return jsonify({"answer": ans})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
