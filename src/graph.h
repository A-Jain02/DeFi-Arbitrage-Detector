#ifndef GRAPH_H
#define GRAPH_H

#include <bits/stdc++.h>
using namespace std;

struct Edge {
    int u, v;
    double weight;
};

class Graph {
public:
    int V, E;
    vector<Edge> edges;
    Graph(int V, int E);
    void addEdge(int u, int v, double rate);
};

#endif
