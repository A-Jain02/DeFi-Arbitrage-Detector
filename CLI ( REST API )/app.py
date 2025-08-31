from flask import Flask, jsonify, render_template
from data_fetcher import fetch_prices
from graph import prices_to_graph, Graph
from bellman_ford import detect_arbitrage

app = Flask(__name__)

def sanitize_prices(raw):
    # Keep only numeric positive prices
    return {k: v for k, v in (raw or {}).items()
            if isinstance(v, (int, float)) and v and v > 0}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/prices")
def prices():
    raw = fetch_prices()
    cleaned = sanitize_prices(raw)
    return jsonify(cleaned)

@app.route("/arbitrage")
def arbitrage():
    raw = fetch_prices()
    cleaned = sanitize_prices(raw)
    if len(cleaned) < 2:
        return jsonify({"cycle": None, "error": "insufficient tokens"}), 200

    adjacency = prices_to_graph(cleaned)   # dict -> adjacency dict (rates)
    g = Graph(adjacency)                   # adjacency -> Graph object
    cycle = detect_arbitrage(g)            # run Bellman–Ford

    return jsonify({"cycle": cycle})
    
if __name__ == "__main__":
    app.run(debug=True)

