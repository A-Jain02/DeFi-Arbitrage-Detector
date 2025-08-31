# ws_multi.py
import json
import websocket
import threading

# Shared dict of latest prices
latest_prices = {
    "binance": {}, "coinbase": {}, "kraken": {}, "bitfinex": {}, "okx": {}
}

# ------------------ BINANCE ------------------
def binance_ws():
    url = "wss://stream.binance.com:9443/ws"

    def on_message(ws, message):
        data = json.loads(message)
        if "s" in data and "p" in data:
            symbol = data["s"]
            price = float(data["p"])
            latest_prices["binance"][symbol] = price

    def on_open(ws):
        params = {
            "method": "SUBSCRIBE",
            "params": [
                "btcusdt@trade", "ethusdt@trade", "adausdt@trade",
                "solusdt@trade", "dogeusdt@trade"
            ],
            "id": 1
        }
        ws.send(json.dumps(params))

    ws = websocket.WebSocketApp(url, on_open=on_open, on_message=on_message)
    ws.run_forever()

# ------------------ COINBASE ------------------
def coinbase_ws():
    url = "wss://ws-feed.exchange.coinbase.com"

    def on_message(ws, message):
        data = json.loads(message)
        if data.get("type") == "ticker":
            product = data["product_id"]  # e.g. BTC-USD
            price = float(data["price"])
            latest_prices["coinbase"][product.replace("-", "")] = price

    def on_open(ws):
        params = {
            "type": "subscribe",
            "channels": [{
                "name": "ticker",
                "product_ids": [
                    "BTC-USD", "ETH-USD", "ADA-USD", "SOL-USD", "DOGE-USD"
                ]
            }]
        }
        ws.send(json.dumps(params))

    ws = websocket.WebSocketApp(url, on_open=on_open, on_message=on_message)
    ws.run_forever()

# ------------------ KRAKEN ------------------
def kraken_ws():
    url = "wss://ws.kraken.com"

    def on_message(ws, message):
        data = json.loads(message)
        if isinstance(data, list) and len(data) > 1 and isinstance(data[1], dict):
            price = float(data[1]["c"][0])  # last trade
            pair = data[-1]  # e.g. XBT/USD
            latest_prices["kraken"][pair.replace("/", "").upper()] = price

    def on_open(ws):
        params = {
            "event": "subscribe",
            "pair": ["XBT/USD", "ETH/USD", "ADA/USD", "SOL/USD", "DOGE/USD"],
            "subscription": {"name": "ticker"}
        }
        ws.send(json.dumps(params))

    ws = websocket.WebSocketApp(url, on_open=on_open, on_message=on_message)
    ws.run_forever()

# ------------------ BITFINEX ------------------
def bitfinex_ws():
    url = "wss://api-pub.bitfinex.com/ws/2"
    bitfinex_pairs = {}

    def on_message(ws, message):
        data = json.loads(message)
        if isinstance(data, dict) and data.get("event") == "subscribed":
            bitfinex_pairs[data["chanId"]] = data["symbol"]
        elif isinstance(data, list) and len(data) > 1 and isinstance(data[1], list):
            price = float(data[1][6])
            chan_id = data[0]
            if chan_id in bitfinex_pairs:
                symbol = bitfinex_pairs[chan_id]
                latest_prices["bitfinex"][symbol] = price

    def on_open(ws):
        pairs = ["tBTCUSD", "tETHUSD", "tADAUSD", "tSOLUSD", "tDOGEUSD"]
        for p in pairs:
            ws.send(json.dumps({"event": "subscribe", "channel": "ticker", "symbol": p}))

    ws = websocket.WebSocketApp(url, on_open=on_open, on_message=on_message)
    ws.run_forever()

# ------------------ OKX ------------------
def okx_ws():
    url = "wss://ws.okx.com:8443/ws/v5/public"

    def on_message(ws, message):
        data = json.loads(message)
        if "arg" in data and "data" in data:
            inst = data["arg"]["instId"]  # e.g. BTC-USDT
            price = float(data["data"][0]["last"])
            latest_prices["okx"][inst.replace("-", "")] = price

    def on_open(ws):
        subs = {
            "op": "subscribe",
            "args": [{"channel": "tickers", "instId": p} for p in
                     ["BTC-USDT", "ETH-USDT", "ADA-USDT", "SOL-USDT", "DOGE-USDT"]]
        }
        ws.send(json.dumps(subs))

    ws = websocket.WebSocketApp(url, on_open=on_open, on_message=on_message)
    ws.run_forever()

# ------------------ START ALL ------------------
def launch_all_ws():
    threading.Thread(target=binance_ws, daemon=True).start()
    threading.Thread(target=coinbase_ws, daemon=True).start()
    threading.Thread(target=kraken_ws, daemon=True).start()
    threading.Thread(target=bitfinex_ws, daemon=True).start()
    threading.Thread(target=okx_ws, daemon=True).start()
