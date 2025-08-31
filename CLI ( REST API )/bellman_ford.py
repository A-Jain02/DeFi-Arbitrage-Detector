def detect_arbitrage(graph):
    """
    graph: Graph instance (has .vertices and .get_edges())
    Returns a cycle list if arbitrage exists, else None.
    """
    V = list(graph.vertices)
    if not V:
        return None

    dist = {v: float("inf") for v in V}
    pred = {v: None for v in V}
    start = V[0]
    dist[start] = 0.0

    edges = graph.get_edges()

    # Relax edges up to |V|-1 times
    for _ in range(len(V) - 1):
        updated = False
        for u, v, w in edges:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                pred[v] = u
                updated = True
        if not updated:
            break

    # Check for negative cycles and reconstruct one if found
    for u, v, w in edges:
        if dist[u] + w < dist[v]:
            # Move v backwards |V| steps to land inside the cycle
            x = v
            for _ in range(len(V)):
                x = pred[x]
            # Collect the cycle
            cycle = [x]
            cur = pred[x]
            while cur != x:
                cycle.append(cur)
                cur = pred[cur]
            cycle.append(x)
            cycle.reverse()
            return cycle

    return None
