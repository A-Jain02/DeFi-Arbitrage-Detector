# ws_multi.py
import json
import websocket
import threading
import gzip

# Shared dict of latest prices
latest_prices = {
    "binance": {}, "coinbase": {}, "bitfinex": {}, "huobi": {}
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

# ------------------ BITFINEX ------------------
def bitfinex_ws():
    url = "wss://api-pub.bitfinex.com/ws/2"
    bitfinex_pairs = {}

    def on_message(ws, message):
        data = json.loads(message)
        if isinstance(data, dict) and data.get("event") == "subscribed":
            bitfinex_pairs[data["chanId"]] = data["symbol"]
        elif isinstance(data, list) and len(data) > 1 and isinstance(data[1], list):
            price = float(data[1][6])  # last price index
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

# ------------------ HUOBI ------------------
def huobi_ws():
    url = "wss://api.huobi.pro/ws"

    def on_message(ws, message):
        # Huobi sends gzip compressed messages
        data = json.loads(gzip.decompress(message).decode())
        if "tick" in data and "ch" in data:
            # e.g. ch: market.btcusdt.trade.detail
            symbol = data["ch"].split(".")[1].upper()  # BTCUSDT
            price = float(data["tick"]["data"][0]["price"])
            latest_prices["huobi"][symbol] = price

    def on_open(ws):
        subs = [
            {"sub": f"market.{p}.trade.detail", "id": p}
            for p in ["btcusdt", "ethusdt", "adausdt", "solusdt", "dogeusdt"]
        ]
        for s in subs:
            ws.send(json.dumps(s))

    ws = websocket.WebSocketApp(url, on_open=on_open, on_message=on_message)
    ws.run_forever()


# ------------------ START ALL ------------------
def launch_all_ws():
    threading.Thread(target=binance_ws, daemon=True).start()
    threading.Thread(target=coinbase_ws, daemon=True).start()
    threading.Thread(target=bitfinex_ws, daemon=True).start()
    threading.Thread(target=huobi_ws, daemon=True).start()

