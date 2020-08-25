import numpy as np
from descartes import PolygonPatch
from shapely.geometry import Polygon, MultiPolygon, Point

def add_polygon(ax,multipolygon,color='blue'):
    for geometry in multipolygon:
        if isinstance(geometry, (Polygon, MultiPolygon)):
            if isinstance(geometry, Polygon):
                geometry = MultiPolygon([geometry])
            for polygon in geometry:
                patch = PolygonPatch(polygon, fc=color, ec=color, linewidth=1, alpha=0.5, zorder=-1)
                ax.add_patch(patch)

def OrderMultiPolygon(multipolygon):
    
    bdry = []
    for i in range(len(multipolygon)):
        coords = list(list(multipolygon)[i].exterior.coords)
        dist = np.linalg.norm(np.array(coords[0])-np.array(coords[-2]))
        bdry.append([coords[0],coords[-2]])
    
    connections = [None for i in bdry]
    for cnt1,coords_1 in enumerate(bdry):
        dists = []
        dists_head = []
        dists_tail = []
        for cnt2,coords_2 in enumerate(bdry):
            dist1 = np.linalg.norm(np.array(coords_1[1])-np.array(coords_2[0]))
            dist2 = np.linalg.norm(np.array(coords_1[1])-np.array(coords_2[1]))
            dist_tail = min(dist1,dist2)
            dist3 = np.linalg.norm(np.array(coords_1[0])-np.array(coords_2[0]))
            dist4 = np.linalg.norm(np.array(coords_1[0])-np.array(coords_2[1]))
            dist_head = min(dist3,dist4)
            dist = min(dist1,dist2,dist3,dist4)
            dists.append(dist)
            dists_head.append(dist_head)
            dists_tail.append(dist_tail)
            
    
        dists_head[cnt1] = 1
        dists_tail[cnt1] = 1
        num_zeros = np.sum((np.array(dists) < 1e-6))
        if num_zeros > 1:
            head = np.where(np.array(dists_head) < 1e-6)[0][0]
            tail = np.where(np.array(dists_tail) < 1e-6)[0][0]
            connections[cnt1] = [head,tail]
            
    if sum(connection is None for connection in connections) == len(connections):
        return multipolygon
    
    start_ind = None
    for cnt,connection in enumerate(connections):
        if connection != None:
            start_ind = cnt
            break
    
    prev = None
    ind = start_ind
    flag = False
    
    all_coords = []
    while True:
        if connections[ind][0] == prev or flag is False:
            coords = list(list(multipolygon)[ind].exterior.coords)
            all_coords = all_coords + coords[:-1]
            prev = ind
            ind = connections[ind][1]
        else:
            # Flip direction of polygon line
            coords = list(list(multipolygon)[ind].exterior.coords)
            all_coords = all_coords + coords[:-1][::-1]
            prev = ind
            ind = connections[ind][0]
        flag = True
        if ind == start_ind: break
    
    all_coords.append(all_coords[0])
    all_polygons = [Polygon(all_coords)]
    for cnt,el in enumerate(connections):
        if el is None:
#             all_polygons.append(Cayuga_polygon['geometry'].iloc[0][cnt])
            all_polygons.append(multipolygon[cnt])
    
    OrderedMultiPolygon = MultiPolygon(all_polygons)
    return OrderedMultiPolygon
