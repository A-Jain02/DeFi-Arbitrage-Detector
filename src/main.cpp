#include <"graph.h">

extern bool detectArbitrage(Graph &g, int start);

int main() {
    int V, E;
    cin >> V >> E;
    Graph g(V, E);

    for (int i = 0; i < E; i++) {
        int u, v;
        double rate;
        cin >> u >> v >> rate;
        g.addEdge(u, v, rate);
    }

    detectArbitrage(g, 0);
    return 0;
}
