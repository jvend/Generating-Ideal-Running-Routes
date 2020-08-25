import osmnx as ox
import networkx as nx

import dijkstra
def Dijkstra(origin_geocoded,target_distance,G,edge_data,User_preferences=None):
    if not User_preferences:
        User_preferences = (0.25,0.25,0.25,0.25)
    edge_data = [ (edge[0],edge[1],edge[2], sum(w*edge_datum for w,edge_datum in zip(User_preferences,edge[3:])) ) for edge in edge_data ]
    
    nx_global_to_local = {}
    nx_local_to_global = {}
    for num, node in enumerate(G.nodes()):
        nx_global_to_local[node] = num
        nx_local_to_global[num]  = node
        
    edges = [(nx_global_to_local[edge[0]],nx_global_to_local[edge[1]],edge[2],edge[3]) for edge in edge_data]

    origin     = ox.get_nearest_node(G, origin_geocoded)
    origin     = nx_global_to_local[origin]

    node_number = len(nx_global_to_local)

    out_dist = dijkstra.print_list(node_number,origin,target_distance,edges)
    shortest_path = [ nx_local_to_global[pt] for pt in out_dist ] 
    
    return shortest_path
