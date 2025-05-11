
import osmnx as ox
import networkx as nx

def create_subgraph_from_nodes(graph, node_list):
    """
    יוצר תת-גרף המבוסס על רשימת צמתים.
    
    :param graph: גרף NetworkX
    :param node_list: רשימת צמתים (Node IDs)
    :return: תת-גרף NetworkX
    """
    subgraph = graph.subgraph(node_list).copy()
    return subgraph

