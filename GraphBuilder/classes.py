from abc import ABC
from typing import Dict, Optional
import numpy as np

## Set generation for person nodes
def randGen() -> int:
    return np.random.choice(np.arange(0, 3), size = 1, p = np.array([.2, .4, .4]))[0]

# Relation class
class relation:
    """
    Class for relations, for internal use only.
    """
    # Hyperparameters
    defaultmax = 10

    # Method definitions
    def __init__(self, name:str):
        self.name = name
        self.subj_class = None
        self.obj_class = None
        self.recip = list()
        self.share = list()
        self.onehop = list(tuple[relation, relation])
        self.no = list()
        self.max = int()
        self.gen = int()
    
    def specify(self, subj:ABC, obj:ABC, recip:list = [], 
                share:list = [], onehop:list = [], no:list = [], 
                max:int = defaultmax, gen:int = None):
        """
        Specifies the properties of a given relation.

        :param subj: Node type of the subject
        :param obj: Node type of the object
        :param recip: Reciprocal relations
        :param share: Shared relations
        :param onehop: List of pairs, each with a hopped relation and the relation to implement.
        """
        self.subj_class = subj
        self.obj_class = obj
        self.recip = recip
        self.share = share
        self.onehop = onehop
        self.no = no
        self.max = max
        self.gen = gen
    
    def getName(self) -> str:
        return self.name
    
    def getClasses(self) -> tuple[ABC, ABC]:
        return self.subj_class, self.obj_class
    
    def getRecip(self) -> list:
        return self.recip
    
    def getNots(self) -> list:
        return self.no
    
    def getShare(self) -> list:
        return self.share
    
    def getOneHop(self) -> list:
        return self.onehop
    
    def getMax(self) -> int:
        return self.max
    
    def getGen(self) -> int:
        return self.gen
    
# Base type for nodes
class node(ABC):
    """
    Basic interface for a node in the knowledge graph.
    """
    def __init__(self, name:str):
        self.properties: Dict[str, ] = dict()
        self.relations: Dict[relation, set] = dict()
        self.setProp('Name', name)
        self.setProp('Generation', None)
    
    # def __call__(self):
    #     print("This is a node, of type" + self.__class__)

    def getProp(self, prop:str):
        """
        Get the value for the specified property.
        """
        return self.properties.get(prop, 'Property not present')

    def setProp(self, prop:str, val):
        """
        Sets the specified property to the specified value.

        :param prop: Name of the property to be set
        :param val: Value to be given to the property
        """
        self.properties[prop] = val

    def getRel(self, rel) -> tuple[set, set]:
        """
        Get the set of nodes for which this node stands in a specified relation.
        
        :param rel: The name of a relation
        :return nodes: The set of nodes 
        :return names: The set of the names of the nodes in that relation
        """
        objects = self.relations.get(rel, set())
        if isinstance(objects, set):
            names = set(obj.getProp('Name') for obj in objects)
            return objects, names
        else:
            return objects, set()
    
    def addRel(self, rel:relation, obj):
        """
        Add a relation to a node
        """
        if rel in self.relations:
            self.relations[rel].add(obj)
        else:
            self.relations[rel] = set([obj])

    def getAllRels(self) -> list[tuple]:
        rel_list = []
        for rel in self.relations:
            for obj in self.getRel(rel)[0]:
                rel_list.append((self, obj, {'Rel': rel.getName()}))
        return rel_list

    def getClass(self):
        return self.__class__
    
    def isEmpty(self) -> bool:
        return bool(self.relations)
    
# Person node class
class person(node):
    def __init__(self, name: str):
        """
        Creates a node for a person.
        
        :param name: A string, the name of the person.
        """
        super().__init__(name)
        # self.setProp('Name', name)
        self.setProp('Generation', randGen())