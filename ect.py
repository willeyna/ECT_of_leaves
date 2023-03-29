import numpy as np
import networkx as nx
import matplotlib as mpl
from itertools import combinations
from sklearn.neighbors import NearestNeighbors

def ect(G, angles, T):
    '''
    Naive computation of finite direction ECT the Euler Characteristic Transform for a (2D) embedded graph in networkx
    Computes (sometimes redundant) subgraphs at every threshold to count components

        Parameters:
            G (networkx graph): A networkx graph whose nodes have attribute 'pos' giving the (x,y) coordinates
            angles (float array): An array of angles (radian) along which to compute the Euler Characteristic Curve
            T (int): Resolution of ECCs; How many linearly spaced slices to take along each direction between the
                        first node and the last node

        Returns:
            ect (int array) [len(angles), T]:  Ect[i] gives the Euler Characteristic Curve along the ith direction.
                                            Use ect.flatten() to get the ECT in its usual presentation as a 1D vector
    '''

    if 'pos' not in G.nodes[0].keys():
        raise AttributeError("Graph G must have node attribute 'pos' for all nodes")

    # adds dir. dist. values as node attributes and returns names of attributes in a list
    direction_labels = set_directional_distances(G, angles)

    # will store full ECT as n_dir*resolution array for clarity; flatten to get old format
    ect = np.zeros([len(direction_labels), T])

    # loop over dir and slices to compute euler char.
    for i, direction in enumerate(direction_labels):

        d = nx.get_node_attributes(G, direction).values()
        m, M = min(d), max(d)

        # effectively a "startpoint=False" option; creates cross_section limits
        cs_lowerlims = np.linspace(M, m, T, endpoint=False)[::-1]

        for j, lim in enumerate(cs_lowerlims):
            # grab the node if the data v[dir] is < threshold
            cs_nodes = [n for n,v in G.nodes(data=True) if v[direction] <= lim]
            # take subgraph up to threshold
            cs_G = G.subgraph(cs_nodes)

            ect[i, j] = len(cs_G.nodes) - len(cs_G.edges)

    return ect.astype('int')

def contour_ect(node_pos, angles, T):
    '''
    Takes in a (N,2) array of node positions and computes the ECT assuming that each node connects to exactly
        its two direct neighbors by counting the # of breaks in the node index sequence
    _Much_ faster alternative to networkifying each array and then computing subgraphs at each threshold
    '''
    N = len(node_pos)

    # will store full ECT as n_dir*resolution array for code clarity
    ECT  = np.zeros([len(angles), T])

    # loop over dir and slices to compute euler char.
    for i, angle in enumerate(angles):

        v = np.array([np.cos(angle), np.sin(angle)])

        # computes a proxy for directional distance using the dot product
        height = [np.dot(v, d) for d in node_pos]

        m, M = min(height), max(height)

        # effectively a "startpoint=False" option; creates cross_section limits
        cs_lowerlims = np.linspace(M, m, T, endpoint=False)[::-1]

        # loop over threshold
        for j, lim in enumerate(cs_lowerlims):
            # mask for nodes above height threshold
            lower_nodes = np.argwhere(height <= lim).flatten()

            # compute ect by counting breaks in contour indices
            ECT[i,j] = count_breaks(lower_nodes, N-1)

    # transform into one integer vector
    ECT  = ECT.flatten().astype('int')

    return ECT

def ect_matrix(G, n_angles, resolutions, contour = True):
    '''
    Requires clean up/ documentation if to be used for anything

    G is a point cloud if contour and a networkwilleyna if not a contour
    '''
    A = np.zeros([len(n_angles), len(resolutions), np.max(n_angles)*np.max(resolutions)])
    # picking a 'value' that isn't obtainable through E.C.C. so it's obviously a placeholder value
    A[:] = np.nan

    for i, n in enumerate(n_angles):
        for j, T in enumerate(resolutions):
            thetas = np.linspace(0,2*np.pi, n, endpoint = False)
            if contour:
                A[i,j,:n*T] = contour_ect(G, thetas, T)
            else:
                A[i,j,:n*T] = ect(G, thetas, T).flatten()

    return A
#################################### HELPER FUNCTIONS / UTILS ##########################################################

def set_directional_distances(G, angles):
    '''
    Given an embedded graph G and a list of directions adds an attribute "dir_i" to each node acting as a proxy
        for the height of the node along angle i.
    Helper function for computing ECT.
    '''

    # makes sure angles is iterable
    angles = np.atleast_1d(angles)

    # for ease of calling in ECT function
    direction_labels = []

    for i, angle in enumerate(angles):
        # 2d only implementation of angle unit vector
        v = np.array([np.cos(angle), np.sin(angle)])

        # computes a proxy for directional distance using the dot product
        directional_dist = [np.dot(v, d) for d in nx.get_node_attributes(G, 'pos').values()]
        # puts directional distance/node index information into dict for graph node input
        dd = dict(enumerate(directional_dist))
        label = 'dir_' + str(i)
        nx.set_node_attributes(G, dd, label)

        direction_labels.append(label)
    return direction_labels

def count_breaks(L, connecting_index=0):
    '''
    Takes in an array-like possibly-broken integer sequence and counts the number of times the sequence breaks
    "connecting_index" is the largest index possible in the sequence and connects to 0 to turn the sequence into
        a loop. Connecting_index = 0 assumes tree structure rather than closed countour
    e.g. [0,1,2,5,6,7,8] with maxind 10 has 2 breaks (at 2 and 8 since 10 connects to 0, not 8)
    '''
    # check for breaks in sequence; add 1 assuming end points dont connect
    n = np.sum(L[:-1]+1 != L[1:]) + 1

    # checks if loop is connected at endpoint; connecting_index is largest so will always be at the end (-1)
    if L[-1] == connecting_index and L[0] == 0:
        # subtract one for closing the loop
        n -= 1

    return n

def twoNN_graph(points):
    '''
    Returns a networkx graph whose nodes are the pointcloud and each node is connected to its 2 nearest neighbors
    '''
    G = nx.Graph()
    inds = np.arange(len(points))
    # create dict of node indices and positions
    pos = {k:v for k,v in zip(inds ,points)}
    G.add_nodes_from(inds)
    nx.set_node_attributes(G, pos, 'pos')

    knn = NearestNeighbors(n_neighbors=2)
    knn.fit(points)
    NN = knn.kneighbors(return_distance = False)

    edge_matrix = np.vstack([inds, NN.T, inds]).T
    edges = np.vstack([edge_matrix[:, :2], edge_matrix[:, 2:]])

    G.add_edges_from(edges)
    return G 

def contour_order(leaf):
    # create 2 nearest neighbor subgraph
    G = twoNN_graph(leaf)
    
    # get largest component graph (leaf without inner holes or other bits)
    component_subgraphs = [G.subgraph(c) for c in nx.connected_components(G)]
    j = np.argmax([len(cc) for cc in component_subgraphs])
    leaf_graph = component_subgraphs[j]
    
    
    contour = []
    l = 0
    maxl = len(leaf)
    # loop makes sure that starting point isnt too close together s.t. our path wont span the leaf
    # increasing by small iterate s.t. our starting point is consistently near the left of the leaf when possible
    while len(contour) <= maxl/2:
        contour = []
        # make directed graph by removing one direction along an edge
        H = leaf_graph.to_directed()
        edges = np.array(H.edges)

        directed_edge = edges[l]
        H.remove_edge(*directed_edge)
        # now find the shortest path between those two points (should follow most of the contour)
        path = nx.shortest_path(H, source = directed_edge[0], target = directed_edge[1])
        # grab the nodes ultimately used in the shortest path
        contour = H.subgraph(path)

        # relabel nodes in contour ordering
        contour_labels = dict(zip(path, np.arange(len(path))))
        contour = nx.relabel_nodes(contour, contour_labels)
        # create matrix with original data ordered correctly
        final_leaf = np.array([contour.nodes()[i]['pos'] for i in range(len(contour.nodes()))] )
        l += 10

        if l > len(edges):
            print("No walk able to cover at least 50% of leaf")
            return None

    return final_leaf
