# ws_fetcher.py
import json
import websocket
import threading
import time

# Shared cache for Streamlit
latest_prices = {}
last_update_time = 0
UPDATE_INTERVAL = 2   # update every 2 seconds

def on_message(ws, message):
    global last_update_time
    data = json.loads(message)

    if "p" in data:  # trade event
        token = data["s"]   # e.g. "BTCUSDT"
        price = float(data["p"])
        current_time = time.time()

        # Only update once per interval
        if current_time - last_update_time >= UPDATE_INTERVAL:
            latest_prices[token] = price
            last_update_time = current_time

def on_error(ws, error):
    print("Error:", error)

def on_close(ws, close_status_code, close_msg):
    print("WebSocket closed")

def on_open(ws):
    # Subscribe to multiple tokens here
    params = {
        "method": "SUBSCRIBE",
        "params": ["btcusdt@trade", "ethusdt@trade", "adausdt@trade"],
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

# Helper to start background thread (used in Streamlit)
def launch_ws_in_background():
    t = threading.Thread(target=start_ws, daemon=True)
    t.start()
