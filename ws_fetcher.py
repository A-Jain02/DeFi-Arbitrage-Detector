# ws_fetcher.py
import json
import websocket
import threading

latest_prices = {}  # cache for live prices

def on_message(ws, message):
    data = json.loads(message)
    if "p" in data:   # trade event
        latest_prices["BTCUSDT"] = float(data["p"])
        print(f"BTC/USDT Live Price: {latest_prices['BTCUSDT']}")

def on_error(ws, error):
    print("Error:", error)

def on_close(ws, close_status_code, close_msg):
    print("WebSocket closed")

def on_open(ws):
    # Subscribe to BTCUSDT trades
    params = {
        "method": "SUBSCRIBE",
        "params": ["btcusdt@trade"],
        "id": 1
    }
    ws.send(json.dumps(params))

def start_ws():
    url = "wss://stream.binance.com:9443/ws"
    ws = websocket.WebSocketApp(url,
                                on_open=on_open,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.run_forever()

if __name__ == "__main__":
    # Run in a thread so it doesn't block your app
    t = threading.Thread(target=start_ws)
    t.start()
