# data_fetcher.py
import ccxt
import pprint
from typing import List, Dict

# Exchanges to use (you can add/remove)
EXCHANGE_IDS = ["binance", "coinbase", "bitfinex"]

# Tokens (base symbols) to check
TOKENS = ["BTC", "ETH", "ADA", "SOL", "DOGE", "DOT", "BNB", "USDT", "USDC"]

# Quotes to try (order matters)
CANDIDATE_QUOTES = ["USDT", "USD", "USDC"]

# Create exchange instances (no API keys needed for public endpoints)
EXCHANGES = {}
for eid in EXCHANGE_IDS:
    try:
        EXCHANGES[eid] = getattr(ccxt, eid)()
    except Exception as e:
        print(f"[WARN] could not init exchange {eid}: {e}")

def _normalize_for_exchange(base: str, exchange_id: str) -> str:
    # Kraken uses XBT instead of BTC
    if exchange_id == "kraken" and base == "BTC":
        return "XBT"
    return base

def _find_market_symbol(exchange, exchange_id: str, base: str) -> str | None:
    """
    Return market string like 'BTC/USDT' that exists on this exchange, or None.
    Requires exchange.load_markets() to have been called.
    """
    base_norm = _normalize_for_exchange(base, exchange_id)
    for quote in CANDIDATE_QUOTES:
        cand = f"{base_norm}/{quote}"
        if cand in exchange.markets:
            return cand
    return None

def fetch_prices(exchange_ids: List[str] = None, tokens: List[str] = None) -> Dict[str, Dict[str, float]]:
    """
    Returns: { "binance": {"BTC": 60234.5, "ETH": 4000.1, ...}, "kraken": {...}, ... }
    """
    exchange_ids = exchange_ids or EXCHANGE_IDS
    tokens = tokens or TOKENS

    out = {}
    for eid in exchange_ids:
        ex = EXCHANGES.get(eid)
        if ex is None:
            print(f"[WARN] skipping unknown exchange {eid}")
            continue

        try:
            # load_markets populates exchange.markets (sync)
            ex.load_markets()
        except Exception as e:
            print(f"[WARN] load_markets failed for {eid}: {e}")
            continue

        out[eid] = {}
        for base in tokens:
            market = _find_market_symbol(ex, eid, base)
            if not market:
                # market not available on this exchange
                continue
            try:
                ticker = ex.fetch_ticker(market)
                last = ticker.get("last")
                if last is None:
                    continue
                # return price quoted in quote currency (usually USD/USDT)
                out[eid][base] = float(last)
            except Exception as e:
                print(f"[WARN] fetch_ticker {market} on {eid} failed: {e}")
                continue

        # if an exchange ended up empty it's fine — consumer should handle it
    return out

# A tiny helper to print simple cross-exchange arbitrage (min vs max)
def find_cross_exchange_spreads(prices: Dict[str, Dict[str, float]], fee_pct: float = 0.001):
    """
    For each token find cheapest exchange and most expensive exchange and compute spread.
    fee_pct is expected round-trip fee estimate (0.001 -> 0.1%).
    Returns list of opportunities (token, buy_ex, buy_price, sell_ex, sell_price, spread_pct).
    """
    tokens = set()
    for exdata in prices.values():
        tokens.update(exdata.keys())

    opps = []
    for t in sorted(tokens):
        best_buy = (None, float("inf"))
        best_sell = (None, 0.0)
        for ex, exdata in prices.items():
            p = exdata.get(t)
            if p is None:
                continue
            if p < best_buy[1]:
                best_buy = (ex, p)
            if p > best_sell[1]:
                best_sell = (ex, p)

        if best_buy[0] and best_sell[0] and best_sell[1] > best_buy[1] * (1 + fee_pct):
            spread = (best_sell[1] - best_buy[1]) / best_buy[1]
            opps.append({
                "token": t,
                "buy_exchange": best_buy[0],
                "buy_price": best_buy[1],
                "sell_exchange": best_sell[0],
                "sell_price": best_sell[1],
                "spread_pct": round(spread * 100, 4)
            })
    return opps

if __name__ == "__main__":
    # quick run
    prices = fetch_prices()
    print("\n=== RAW PRICES ===")
    pprint.pprint(prices)
    print("\n=== SPREADS ===")
    opps = find_cross_exchange_spreads(prices, fee_pct=0.001)
    if not opps:
        print("No cross-exchange spreads above fee threshold.")
    else:
        pprint.pprint(opps)

