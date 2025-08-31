#include "graph.h"

bool detectArbitrage(Graph &g, int start) {
    vector<double> dist(g.V, 1e9);
    dist[start] = 0.0;

    // Relax edges V-1 times
    for (int i = 1; i < g.V; i++) {
        for (auto &edge : g.edges) {
            if (dist[edge.u] + edge.weight < dist[edge.v]) {
                dist[edge.v] = dist[edge.u] + edge.weight;
            }
        }
    }

    // Check for negative cycle
    for (auto &edge : g.edges) {
        if (dist[edge.u] + edge.weight < dist[edge.v]) {
            cout << "Arbitrage opportunity detected!\n";
            return true;
        }
    }
    cout << "No arbitrage found.\n";
    return false;
}
