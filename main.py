import osmnx as ox
import osmnx.distance
from heapq import heappop, heappush

def shortest_run(b, e, graphic):
    """
    Plots out a shortest run
    no further requirements

    :param graphic: OSMnx graph
    :return: [coördinate, coördinate, coördinate, ...]
    """

    begin_node = ox.distance.nearest_nodes(graphic, b[0], b[1])             # Fetches the node closest to the coördinate
    end_node = ox.distance.nearest_nodes(graphic, e[0], e[1])

    # Calculate shortest path
    list_nodes = osmnx.distance.shortest_path(graphic, begin_node, end_node, weight='length')

    return_list = []                                                        # Since the fucntion above only returns
    for node in list_nodes:                                                 # nodes, their corresponding coördinates
        return_list.append((graphic.nodes[node]['y'], graphic.nodes[node]['x']))  # get added and collected in a list

    return return_list

def dijkstra_run(b, e, location):
    '''
    Uses the Dijkstra algorithm to calculate the shortest distance between two points.

    :param b: Start coördinate as tuple                                     (lat, lon)
    :param e: End coördinate as tuple                                       (lat, lon)
    :param location: name of location                                       (City, Country)
    :return: [coördinate, coördinate, coördinate, ...]
    '''

    graphic = ox.graph_from_place(location, network_type="all")             # Fetch the graph

    begin_node = ox.distance.nearest_nodes(graphic, b[0], b[1])             # Fetches the node closest to the coördinate
    end_node = ox.distance.nearest_nodes(graphic, e[0], e[1])

    dist = {node: float('inf') for node in graphic.nodes}                   # Dictionary that keeps track of shortest
                                                                            # distance to a node, by default set to inf

    prev = {b: None}                                                        # Dictionary keeps track of all where each
                                                                            # node was approached from

    eval = [(0, begin_node)]                                                # Keeps track of which nodes are yet to be
                                                                            # taken through the algorithm and which are
                                                                            # prioritized first
    while eval:
        source_distance, source_node = heappop(eval)                        # As long as eval is not empty keep looking

        if source_node == end_node:                                         # Break when finisch is reached
            break

        for target_node, target_edge in graphic[source_node].items():       # Iterate through all neighbouring nodes

            source_target_dist = source_distance + target_edge[0]['length']

            if source_target_dist < dist[target_node]:                      # If the new distance is shorter than the
                dist[target_node] = source_target_dist                      # previously recorded distance, update dicts
                prev[target_node] = source_node
                heappush(eval, (source_target_dist, target_node))           # Uses a priority queue with heappush

    path = []
    current_node = end_node

    while current_node != begin_node:                                       # Reconstruct the path so by reversing
        path.append(current_node)                                           # through the prev dict
        current_node = prev.get(current_node)

    path = list(reversed(path))                                             # Reverse the path
    path.insert(0, begin_node)

    return_list = []                                                        # Since we've been working with nodes above
    for node in path:                                                       # we need to get their corresponding coörds
        return_list.append((graphic.nodes[node]['y'], graphic.nodes[node]['x']))

    return return_list

def radius_run2(b, e, location):
    '''
    This function uses three other functions, nature_cords, encountered_cords,
    and path_maker go to the functions themselves to find out how they work.
    This is a custom interpretation of the Dijkstra algorithm,
    it calculates a route with the maximum amount of nature along the way

    :param b: Start coördinate as tuple                                     (lat, lon)
    :param e: End coördinate as tuple                                       (lat, lon)
    :param location: name of location                                       (City, Country)
    :return: [coördinate, coördinate, coördinate, ...]
    '''
    from functions import nature_cords, encountered_cords, path_maker
    graphic = ox.graph_from_place(location, network_type="all")

    nature_cords_forest = nature_cords(location, {'landuse': 'forest'}, 0.00001)
    nature_cords_scrub = nature_cords(location, {'natural': 'scrub'}, 0.000005)
    nature_cords = nature_cords_forest + nature_cords_scrub

    path = dijkstra_run(b, e, location)

    encountered_centroids = encountered_cords(graphic, nature_cords, path, b, e, 800)

    print(encountered_centroids)

    final_path = path_maker(encountered_centroids, location, b, e)
    #
    print(final_path)

    return final_path