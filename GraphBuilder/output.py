import typing
import networkx as nx
import matplotlib.pyplot as plt
from classes import node, relation

def getTriples(nodes:list[node]) -> None:
    for node in nodes:
        for key in node.relations.keys():
            for pers in node.relations[key]:
                print(f'{node.getProp("Name")} {key.getName()} {pers.getProp("Name")}.')
    return

def printGraph(nodes) -> None:
    testgraph = nx.MultiDiGraph()
    testgraph.add_nodes_from(nodes)
    for person in nodes:
        testgraph.add_edges_from(person.getAllRels())
    edge_labels = nx.get_edge_attributes(testgraph, "Rel")
    try:
        pos = nx.planar_layout(testgraph, 3)
        nx.draw(testgraph, pos, labels={person:person.getProp('Name') for person in nodes}, connectionstyle='arc3, rad = 0.1')
        nx.draw_networkx_edge_labels(testgraph, pos=pos, edge_labels=edge_labels, connectionstyle='arc3, rad = 0.1', font_size=8)
        plt.show()
    except:
        pos=nx.spectral_layout(testgraph)
        nx.draw(testgraph, pos, labels={person:person.getProp('Name') for person in nodes}, connectionstyle='arc3, rad = 0.1')
        nx.draw_networkx_edge_labels(testgraph, pos=pos, edge_labels=edge_labels, connectionstyle='arc3, rad = 0.1', font_size=8)
        plt.show()
    return None