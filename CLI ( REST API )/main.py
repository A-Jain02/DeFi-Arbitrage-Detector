from data_fetcher import fetch_prices
from graph import Graph

def main():
    prices_by_exchange = fetch_prices()
    print("\n--- Live Prices by Exchange ---")
    for ex, prices in prices_by_exchange.items():
        print(f"{ex}: {prices}")

    g = Graph(prices_by_exchange)

    print("\n--- Arbitrage Detection ---")
    for vertex in g.vertices:
        has_cycle, cycle, profit = g.bellman_ford(vertex)
        if has_cycle:
            print(f"🚨 Arbitrage opportunity: {cycle}")
            print(f"💰 Profit: {profit:.2f}%")
            break
    else:
        print("No arbitrage detected.")

if __name__ == "__main__":
    main()
