import os
import osmnx as ox
import networkx as nx
import numpy as np
import pandas as pd
import googlemaps
import matplotlib.pyplot as plt
import matplotlib as mpl
from reorder_polygons import *

def collect_data(center_point,dist,known_trail=None):
    filter_ = '["highway"]["area"!~"yes"]["highway"!~"service|motor|proposed|construction|abandoned|platform|raceway"]["foot"!~"no"]["service"!~"private"]'
    G = ox.graph_from_point(center_point=center_point,dist=dist,dist_type='bbox',custom_filter=filter_)
    G = G.to_undirected()
    
    # Add marked paths, cycleways, and user-specified trails
    edge_colors = []
    trail_color = '#F1C232' #'#674EA7'
    for edge in G.edges(data=True):
            try:
                name = edge[2]['name']
                if name in known_trail or (isinstance(name,list) and len(known_trail.intesection(name))!=0 ):
                    edge_colors.append(trail_color)
                    continue
            except:
                pass
            highway = edge[2]['highway']
            if highway == 'path' or (isinstance(highway,list) and 'path' in highway):
                edge_colors.append(trail_color)
            elif highway == 'cycleway' or (isinstance(highway,list) and 'cycleway' in highway):
                edge_colors.append(trail_color)
            else:
                edge_colors.append('#999999')


    # Get water features
    tags = {'natural':'water'}
    pois_water = ox.pois_from_point(center_point,tags,dist=dist)
    pois_water_list = list(pois_water['name'][pd.notna(pois_water['name'])])
    pois_water_list.sort()
    pois_water_list = [el for el in pois_water_list if 'Lake' in el] 

    # Get park features
    tags = {'leisure':'park'}
    park_pois = ox.pois_from_point(center_point,tags,dist=dist)

    # Add elevation data
    google_maps_api_key = os.environ.get('GOOGLEAPIKEY') # You'll need your own API key :)

    G = ox.add_node_elevations(G, api_key=google_maps_api_key)
    G = ox.add_edge_grades(G)

    grade_data = []
    for u,v, data in G.edges(keys=False, data=True):
        u_lat = G.nodes[u]['y']
        u_lng = G.nodes[u]['x']
        u_el  = G.nodes[u]['elevation']
        v_lat = G.nodes[v]['y']
        v_lng = G.nodes[v]['x']
        v_el  = G.nodes[v]['elevation']
        elevation_change = G.nodes[v]["elevation"] - G.nodes[u]["elevation"]
        center_lat = 0.5*(u_lat + v_lat)
        center_lng = 0.5*(u_lng + v_lng)
        grade_datum = np.array([data['length'],data['grade_abs'],data['length']*data['grade_abs']])
        grade_data.append(grade_datum)
        
    grade_data = np.vstack(grade_data)

    # Build edge data
    # https://stackoverflow.com/questions/639695/how-to-convert-latitude-or-longitude-to-meters
    import math
    def lat_lon_to_dist(lat1,lon1,lat2,lon2): # pt[0] = long, pt[1] = lat
        R = 6378.137
        dLat = lat2 * math.pi / 180 - lat1 * math.pi / 180
        dLon = lon2 * math.pi / 180 - lon1 * math.pi / 180
        a = math.sin(dLat/2) * math.sin(dLat/2) + math.cos(lat1 * math.pi / 180) * math.cos(lat2 * math.pi / 180) * math.sin(dLon/2) * math.sin(dLon/2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        d = R * c
        return d * 1000 # meters
        
    def get_min_dist(pt,pois_geom):
        pt_np = np.array(pt)
        min_ = float('inf')
        for obj in pois_geom:
            if isinstance(obj,Point) or isinstance(obj,tuple):
                obj_np = np.array(obj)
                dist = lat_lon_to_dist(pt_np[1],pt_np[0],obj_np[1],obj_np[0])
                if dist < min_:
                    min_ = dist
                    min_poi_pt = obj_np
            if isinstance(obj,Polygon):
                if obj.contains(pt) == True:
                    min_ = 0
                    return min_,None
                coords = list(obj.exterior.coords)
                dist,poi_pt = get_min_dist(pt,coords)
                if dist < min_:
                    min_ = dist
                    min_poi_pt = poi_pt
            if isinstance(obj,MultiPolygon):
                for poly in obj:
                    if poly.contains(pt) == True:
                        min_ = 0
                        return min_,None
                    coords = list(poly.exterior.coords)
                    dist,poi_pt = get_min_dist(pt,coords)
                    if dist < min_:
                        min_ = dist
                        min_poi_pt = poi_pt
        return min_,min_poi_pt

    # Get edge data for parks
    print('Getting park edge data')
    nature_dist_edge = []
    for edge in G.edges(data=True):
        edge_nodes = [edge[0],edge[1]]
        center = np.array( [sum([G.nodes[node_id]['x'] for node_id in edge_nodes])/2, sum([G.nodes[node_id]['y'] for node_id in edge_nodes])/2 ])
        pt = Point(center[0],center[1])
        dist,min_pt = get_min_dist(pt,park_pois['geometry'])
        nature_dist_edge.append((dist,np.array(pt),min_pt))

    # Get edge data for water
    print('Getting water edge data')
    water_dist_edge = []
    for edge in G.edges(data=True):
        edge_nodes = [edge[0],edge[1]]
        center = np.array( [sum([G.nodes[node_id]['x'] for node_id in edge_nodes])/2, sum([G.nodes[node_id]['y'] for node_id in edge_nodes])/2 ])
        pt = Point(center[0],center[1])
        dist,min_pt = get_min_dist(pt,pois_water['geometry'])
        water_dist_edge.append((dist,np.array(pt),min_pt))

    # Rescale edge data based on statistical analysis
    def sigma(x):
        return 1./(1+np.exp(-(x-200)/30))# - sigma(0)

    lengths = grade_data[:,0]
    impedence = 10*grade_data[:,2]
    water_dist_rescaled  = map(lambda x : sigma(x[0]), water_dist_edge)
    water_dist_impedence = [x*y for x,y in zip(water_dist_rescaled,lengths)]
    nature_dist_rescaled = map(lambda x : sigma(x[0]), nature_dist_edge)
    nature_dist_impedence = [x*y for x,y in zip(nature_dist_rescaled,lengths)]
    is_not_trail_penalty = [length*float(color != trail_color) for color,length in zip(edge_colors,lengths)]

    lengths = list(lengths)
    impedence = list(impedence)
    data = list(zip(lengths,impedence,water_dist_impedence,nature_dist_impedence,is_not_trail_penalty))
    
    edge_nodes = [ (u,v) for u,v, data in list(G.edges(keys=False, data=True)) ]
    all_data = [ (a[0],a[1],b[0],b[1],b[2],b[3],b[4]) for a,b in zip(edge_nodes, data) ]

    return G, all_data
