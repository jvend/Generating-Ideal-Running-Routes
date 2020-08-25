#ifndef DIJKSTRA_HPP
#define DIJKSTRA_HPP

// Modified from https://ide.geeksforgeeks.org/Do157gzJig
// see also https://www.geeksforgeeks.org/dijkstras-shortest-path-algorithm-using-priority_queue-stl/

// Program to find Dijkstra's shortest path using priority_queue in STL
#include <iostream>
#include <list>
#include <utility>
#include <vector>
#include <queue>
#include <limits>

using namespace std;
double INF = 1e307;

typedef pair<int, int> iiPair;
typedef pair<int, double> idPair;
typedef pair<double, int> diPair;

// This class represents a directed graph using
// adjacency list representation
class Graph
{
	int V; // No. of vertices

	// In a weighted graph, we need to store vertex
	// and weight pair for every edge
	list< std::tuple<int, double, double> > *adj;

public:
	Graph(int V); // Constructor
    ~Graph();     // Destructor

	// function to add an edge to graph
	void addEdge(int u, int v, double l, double w);

	// prints shortest path from s
	void shortestPath(int s);
    void reset_obj(); // resets dist and predecessor for reuse
    std::vector<double> cost;
    std::vector<double> dist;
    std::vector<int> predecessor;
    std::vector<int> get_shortest_path(int source, int end);
};

// Allocates memory for adjacency list
Graph::Graph(int V):
cost(V,INF),
dist(V,INF),
predecessor(V,-1)
{
	this->V = V;
	adj = new list<std::tuple<int,double,double> > [V];
}

Graph::~Graph(){delete[] adj;}

void Graph::addEdge(int u, int v, double l, double w)
{
	//adj[u].push_back(make_pair(v, w));
	//adj[v].push_back(make_pair(u, w));
    adj[u].push_back(std::make_tuple(v,l,w));
    adj[v].push_back(std::make_tuple(u,l,w));
}

// Gets shortest paths from src to all other vertices
void Graph::shortestPath(int src)
{
	// Create a priority queue to store vertices that
	// are being preprocessed. This is weird syntax in C++.
	// Refer below link for details of this syntax
	// https://www.geeksforgeeks.org/implement-min-heap-using-stl/
	priority_queue< diPair, vector <diPair> , greater<diPair> > pq;

	// Insert source itself in priority queue and initialize
	// its distance as 0.
	pq.push(make_pair(0, src));
    cost[src] = 0;
	dist[src] = 0;
	
	vector<bool> f(V, false);

	/* Looping till priority queue becomes empty (or all
	distances are not finalized) */
	while (!pq.empty())
	{
		// The first vertex in pair is the minimum distance
		// vertex, extract it from priority queue.
		// vertex label is stored in second of pair (it
		// has to be done this way to keep the vertices
		// sorted distance (distance must be first item
		// in pair)
		int u = pq.top().second;
		pq.pop();
		f[u] = true;

		// 'i' is used to get all adjacent vertices of a vertex
		list< std::tuple<int, double, double> >::iterator i;
		for (i = adj[u].begin(); i != adj[u].end(); ++i)
		{
			// Get vertex label and weight of current adjacent
			// of u.
			int v = std::get<0>(*i);
            double length = std::get<1>(*i);
			double weight = std::get<2>(*i);

			// If there is shorted path to v through u.
			if (f[v] == false && cost[v] > cost[u] + weight)
			{
				// Updating distance of v
                cost[v] = cost[u] + weight;
				dist[v] = dist[u] + length;
                // Updating predecessor of v;
                predecessor[v] = u;
				pq.push(make_pair(cost[v], v));
			}
		}
	}

}

void Graph::reset_obj(){
std::fill(predecessor.begin(),predecessor.end(),-1);
std::fill(cost.begin(),cost.end(),INF);
std::fill(dist.begin(),dist.end(),INF);
}

std::vector<int> Graph::get_shortest_path(int source, int end){
    std::vector<int> shortest_path;
    int p = end;
    while ( p != source ){
        shortest_path.push_back(p);
        p = predecessor[p];
    }
    shortest_path.push_back(source);

    // Reverse order
    for(unsigned long i=0; i<shortest_path.size()/2; i++){
        std::swap(shortest_path[i],shortest_path[shortest_path.size()-1-i]);
    }  

    return shortest_path;
}

std::vector<int> get_shortest_path(int source, int end, std::vector<int> predecessor){
    std::vector<int> shortest_path;
    int p = end;
    while ( p != source ){
        shortest_path.push_back(p);
        p = predecessor[p];
    }
    shortest_path.push_back(source);

    // Reverse order
    for(unsigned long i=0; i<shortest_path.size()/2; i++){
        std::swap(shortest_path[i],shortest_path[shortest_path.size()-1-i]);
    }

    return shortest_path;
}


#endif /* DIJKSTRA_HPP */
