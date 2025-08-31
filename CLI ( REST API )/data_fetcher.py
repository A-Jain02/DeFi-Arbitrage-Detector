# data_fetcher.py
import ccxt
from concurrent.futures import ThreadPoolExecutor

EXCHANGE_IDS = ["binance", "coinbase", "bitfinex"]
TOKENS = ["BTC", "ETH", "USDT", "BNB", "ADA", "DOGE", "SOL", "DOT"]

# Initialize exchange instances
EXCHANGES = {eid: getattr(ccxt, eid)() for eid in EXCHANGE_IDS}

def fetch_from_exchange(eid, tokens=TOKENS):
    """Fetch prices for given tokens from one exchange"""
    ex = EXCHANGES[eid]
    try:
        ex.load_markets()
    except Exception as e:
        print(f"[WARN] load_markets failed for {eid}: {e}")
        return {}

    prices = {}
    for token in tokens:
        market = f"{token}/USDT"
        if market in ex.markets:
            try:
                ticker = ex.fetch_ticker(market)
                prices[token] = ticker["last"]
            except Exception as e:
                print(f"[WARN] fetch_ticker failed on {eid} for {market}: {e}")
    return prices

def fetch_prices():
    """Fetch prices from all exchanges in parallel"""
    results = {}
    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(fetch_from_exchange, eid): eid for eid in EXCHANGE_IDS}
        for future in futures:
            eid = futures[future]
            try:
                results[eid] = future.result()
            except Exception as e:
                print(f"[ERROR] fetching from {eid}: {e}")
                results[eid] = {}
    return results

if __name__ == "__main__":
    import pprint
    prices = fetch_prices()
    pprint.pprint(prices)

