import math

class Graph:
    def __init__(self, prices_by_exchange):
        self.edges = []
        self.vertices = set()

        # Build graph from price data
        for exchange, prices in prices_by_exchange.items():
            for token, price in prices.items():
                self.vertices.add(f"{token}_{exchange}")

        exchanges = list(prices_by_exchange.keys())
        tokens = list(next(iter(prices_by_exchange.values())).keys())

        for token in tokens:
            for i in range(len(exchanges)):
                for j in range(len(exchanges)):
                    if i != j:
                        ex1, ex2 = exchanges[i], exchanges[j]
                        if token in prices_by_exchange[ex1] and token in prices_by_exchange[ex2]:
                            price1 = prices_by_exchange[ex1][token]
                            price2 = prices_by_exchange[ex2][token]

                            if price1 > 0 and price2 > 0:
                                rate = price2 / price1
                                weight = -math.log(rate)
                                self.edges.append((f"{token}_{ex1}", f"{token}_{ex2}", weight))

    def bellman_ford(self, start):
        dist = {v: float("inf") for v in self.vertices}
        parent = {v: None for v in self.vertices}
        dist[start] = 0

        for _ in range(len(self.vertices) - 1):
            for u, v, w in self.edges:
                if dist[u] + w < dist[v]:
                    dist[v] = dist[u] + w
                    parent[v] = u

        for u, v, w in self.edges:
            if dist[u] + w < dist[v]:
                cycle = [v, u]
                while parent[u] and parent[u] not in cycle:
                    u = parent[u]
                    cycle.append(u)
                cycle.reverse()

                # --- PROFIT CALC ---
                profit = self.calculate_profit(cycle)
                return True, cycle, profit

        return False, None, None

    def calculate_profit(self, cycle):
        """Given a cycle, calculate net profit if we start with 1 unit"""
        amount = 1.0
        for i in range(len(cycle) - 1):
            token1, ex1 = cycle[i].split("_")
            token2, ex2 = cycle[i + 1].split("_")

            # find price ratio
            for u, v, w in self.edges:
                if u == cycle[i] and v == cycle[i + 1]:
                    rate = math.exp(-w)  # since w = -log(rate)
                    amount *= rate
                    break

        profit_pct = (amount - 1) * 100
        return profit_pct
