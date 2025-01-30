import yaml
from typing import Dict, Optional
import numpy as np
# import scipy.stats as ss
# import networkx as nx
# import matplotlib.pyplot as plt

from classes import relation, node, person
from checking import tryRelation

## Load the graph spec
def loadSpec(spec:str) -> list[node]:
    """
    Loads a graph spec from the given path

    :param spec: The filepath of the graph spec.
    :returns people: For now, just returns a list of person nodes with names from the spec.
    """
    with open(spec, 'r') as spec:
        docs = yaml.safe_load_all(spec)
        types, nodes, rels = docs
    people = []
    for name in nodes['person']:
        people.append(person(name))
    return people

## Draw a list of nodes
def drawNode(nodes: list[node], size:int = 1, names = False) -> list[node]:
    """
    Draw nodes from a list of nodes, with weights derived from the inverse of the number of relations of each node.

    :param nodes: A list of nodes.
    :param size: The number of nodes to be drawn.
    :return: A list of nodes drawn from the list, with specified probabilities, without replacement. If `names' is True, returns the names of the nodes.
    """
    weights = np.zeros(len(nodes))
    for i in range(len(nodes)):
        relcount = 0
        for rel in nodes[i].relations:
            relcount += len(nodes[i].getRel(rel)[0])
        if relcount == 0:
            weights[i] = 1
        else:
            weights[i] = 1 / relcount ** 2
    weights = np.exp(weights) / np.sum(np.exp(weights))
    if size > len(nodes):
        size = len(nodes)
    nodelist = np.random.choice(a=nodes, size=size, p = weights, replace=False)
    if names is True:
        nodelist = [i.getProp('Name') for i in nodelist]
    return nodelist

## Generate a graph
def newGraph(nodes:list[node], rels:list[relation], total_rels:int) -> list[node]:
    """
    Generates a relational graph from a list of nodes and a list of relations.

    :param nodes: A list of nodes on which to attempt to initialize relations.
    :param rels: A list of relations to attempt to instantiate betweeen the nodes.
    :param total_rels: The total number of relations.
    :return: A list of nodes with relations.
    """
    total = 0
    for subj in nodes:
        for _ in range(8):
            if total < total_rels:
                print(subj.getProp('Name'))
                rel = np.random.choice(rels, 1)[0]
                print(rel.getName())
                obj = drawNode(nodes, 1)[0]
                print(obj.getProp('Name'))
                if tryRelation(subj, obj, rel) is True:
                    total += 1
                    break
            else:
                break
    return nodes
