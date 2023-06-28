import osmnx.distance
from heapq import heappop, heappush
import osmnx as ox

def nature_cords(location, biome, m2):
    '''
    This function call upon the osmnx library to get all polygons of a given biome.
    After that it strictly returns the centroids of the biomes polygons if they are
    larger than the minimal given square meters.

    :param location: The town or city                  (City, Country)
    :param biome:    a certain type of terrain         {type: type}
    :param m2:       minimal area int
    :return:         cords of centers                  [coördinate, coördinate, coördinate, ...]
    '''


    biome_cords = []

    biome_polygons = ox.geometries_from_place(location, biome)              # Fetch all polygons from desired location
    for idx, polygon in biome_polygons.iterrows():                          # Iterate over each polygon
        area = polygon["geometry"].area

        if area >= m2:                                                      # Check if the area is larger than the
            biome_centroid = polygon["geometry"].centroid                   # given minimal area in square meters
            biome_cords.append((biome_centroid.y, biome_centroid.x))

    return biome_cords

def encountered_cords(graphic, nature_cords, path, b, e, radius):
    '''
    This function takes the encountered centroids and original path
    it discovers the nearby forests by comapring the distance between the path and the forest
    If the forest is close enough, it will get added

    :param nature_cords: detected forests                                  [coördinate, coördinate, coördinate, ...]
    :param path:         shortest path between two points, the vanilla way [coördinate, coördinate, coördinate, ...]
    :param b:            start point, this is added to return a complete path (lat, lon)
    :param e:            end point, this is added to return a complete path   (lat, lon)
    :param radius:       A given maximal distance to detect forests at int
    :return:             Encountered forests along the original path       [coördinate, coördinate, coördinate, ...]
    '''

    encountered_centroids = []

    for path_node in path:                                                  # Iterate through the nodes of original path

        for centroid_cord in nature_cords:                                  # Iterate through all encountered centroids

            distance = ox.distance.great_circle_vec(path_node[0], path_node[1],
                       centroid_cord[0], centroid_cord[1])                  # Calculate the distance between these two

            if distance < radius and centroid_cord not in encountered_centroids:
                encountered_centroids.append(centroid_cord)                 # If the distance is shorter than the given
                                                                            # radius, it gets appended
    encountered_centroids.insert(0, (b[1], b[0]))
    encountered_centroids.append((e[1], e[0]))                              # add to complete the path start to finish

    return encountered_centroids

def path_maker(encountered_centroids, location, b, e):
    '''
    This is where all points come together.
    Once the forests from start to end have been collected,
    a for loop will construct one big route with all coördinates for each seperate instance
    Each of these instances are basically shortest paths between the coördinates in a list
    It doesn't only use a shortest_path algorithm, when the algorithm is comparing nodes
    the nodes that are located in a forest have edges that have weights wich are set to '1'
    That makes it even more accurate than if you would use a normal one.
    Since the dijkstra algorithm in the paths.py already has been documented, I will keep this as is.

    :param encountered_centroids: Encountered forests along the original path  [coördinate, coördinate, coördinate, ...]
    :param b: Start coördinate as tuple                                        (lat, lon)
    :param e: End coördinate as tuple                                          (lat, lon)
    :param location: name of location                                          (City, Country)
    :return: [coördinate, coördinate, coördinate, ...]
    '''

    graphic = ox.graph_from_place(location, network_type="all")

    # Retrieve forest polygons in the specified location
    forest_polygons = ox.geometries_from_place(location, {"landuse": "forest"})
    forest_multi_polygon = forest_polygons.unary_union

    # Generate a graph from the forest polygons
    forested_graphic = ox.graph_from_polygon(forest_multi_polygon, network_type='all')

    forested_edges = []
    # Extract the OSM IDs of edges that belong to forests
    for u, v, data in forested_graphic.edges(data=True):
        forested_edges.append(data['osmid'])

    final_path = []

    # Iterate over the encountered centroids
    for i in range(len(encountered_centroids)):
        current_coord = encountered_centroids[i - 1]
        next_coord = encountered_centroids[i]

        # Find the shortest path between the current coordinate and the next coordinate
        begin_node = ox.distance.nearest_nodes(graphic, current_coord[1], current_coord[0])
        end_node = ox.distance.nearest_nodes(graphic, next_coord[1], next_coord[0])

        dist = {node: float('inf') for node in graphic.nodes}
        prev = {b: None}
        eval = [(0, begin_node)]

        while eval:
            source_distance, source_node = heappop(eval)

            if source_node == end_node:
                break

            # Check if the edge is part of a forest and set its length to 1
            for target_node, target_edge in graphic[source_node].items():
                for target_2_node, target_2_edge in graphic[target_node].items():
                    if target_2_edge[0]['osmid'] in forested_edges:
                        target_2_edge[0]['length'] = 1
                        target_edge[0]['length'] = 1
                    for target_3_node, target_3_edge in graphic[target_2_node].items():
                        if target_3_edge[0]['osmid'] in forested_edges:
                            target_3_edge[0]['length'] = 1
                        for target_4_node, target_4_edge in graphic[target_3_node].items():
                            if target_4_edge[0]['osmid'] in forested_edges:
                                target_4_edge[0]['length'] = 1

                source_target_dist = source_distance + target_edge[0]['length']

                if source_target_dist < dist[target_node]:
                    dist[target_node] = source_target_dist
                    prev[target_node] = source_node
                    heappush(eval, (source_target_dist, target_node))

        path = []
        current_node = end_node

        # Reconstruct the shortest path
        while current_node != begin_node:
            path.append(current_node)
            current_node = prev.get(current_node)

        path = list(reversed(path))  # Reverse the path to start from the beginning node
        path.insert(0, begin_node)

        return_list = []
        for node in path:
            return_list.append((graphic.nodes[node]['y'], graphic.nodes[node]['x']))

        if current_coord == encountered_centroids[-1] and next_coord == encountered_centroids[0]:
            'niks'
        else:
            # Append the shortest path to the route
            final_path.extend(return_list[1:])  # Exclude the first coordinate since it's already in the route

    # Add the last coordinate to the route
    final_path.append(encountered_centroids[-1])

    return final_path