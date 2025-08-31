#include "graph.h"

Graph::Graph(int V, int E) {
    this->V = V;
    this->E = E;
}

void Graph::addEdge(int u, int v, double rate) {
    // convert rate -> -log(rate) for arbitrage detection
    edges.push_back({u, v, -log(rate)});
}
