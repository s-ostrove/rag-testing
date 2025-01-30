from abc import ABC, abstractmethod
# from typing import Dict, Optional
# import numpy as np
# import scipy.stats as ss


from classes import relation, node

## Print the list of relations being checked
def printChecking(checking:list[tuple]):
    for i in checking:
        print(i[1].getProp('Name'), i[0].getName(), i[2].getProp('Name'))

def tryRelation(subj:node, obj:node, rel:relation) -> bool:
    """
    Interface for adding a relation between two nodes.
    """
    # Check that the subject and object are not the same node
    if subj is obj:
        print('Subject is same as object')
        return False
    
    # Check the generation requirement
    if rel.getGen() is not None:
        if obj.getProp('Generation') - subj.getProp('Generation') != rel.getGen():
            print('Generational mismatch')
            return False

    # Initialize the relation-checking buffer (a list of valid relations 
    # that would be put in place to satisfy creating this relation)
    checking = [(rel, subj, obj)]

    # Check that the relation is not already in place
    rel_set = subj.getRel(rel)[0]
    if obj in rel_set:
        print('Relation already in place')
        return False

    # Check the type requirements of the relation
    if (rel.getClasses()) != (subj.getClass(), obj.getClass()):
        print(subj.getClass(), obj.getClass())
        print('Classes incorrect')
        return False

    # Check the share requirements of the relation
    if checkShare(rel, subj, obj, checking) is False:
        print('Share check failed')
        return False

    # Check the reciprocal requirements of the relation
    if checkRecip(rel, subj, obj, checking) is False:
        print('Reciprocity check failed')
        return False
    
    # Check the one-hop properties
    if checkOneHop(rel, subj, obj, checking) is False:
        print('One-hop check failed')
        return False

    # Check the not requirements of the relation
    for i in rel.getNots():
        ## Check if relation exists
        if obj in subj.getRel(i)[0]:
            print('Blocking relation present')
            return False
        ## Check if relation would be needed
        elif (i, subj, obj) in checking:
            print('Would require blocking relation')
            return False

    # Check the max requirement of the relation
    ## Count the number of instances for this relation and subject
    rel_count = len(rel_set)
    for i in checking:
        if (i[0] == rel) and (i[1] == subj):
            rel_count += 1
    ## Check the max requirement
    if rel_count > rel.getMax():
        print('Too many instances of relation', rel.getName())
        return False

    # Add the relations from “checking”, and print the relations being added
    printChecking(checking)
    for tup in checking:
        tup[1].addRel(tup[0], tup[2])
    
    # Return True if the relation was implemented, otherwise return False
    return True

def checkRecip(rel:relation, subj:node, obj:node, checking:list) -> bool:
    """
    Checks whether a relation can be implemented as a reciprocal.

    :param rel: The original relation
    :param subj: The subject of the original relation
    :param obj: The object of the original relation
    :param checking: The buffer of assumed relations
    """
    print(f'Call to checkRecip for relation {rel.getName()} between {subj.getProp("Name")} and {obj.getProp("Name")}')
    # Iterate over the reciprocal requirements
    for recip in rel.getRecip():
        # print('Checking reciprocal relation', recip.getName(), 'between nodes', obj.getProp('Name'), 'and', subj.getProp('Name'))
        # If reciprocal exists, check requirements and then move to next reciprocal
        if subj in obj.getRel(recip)[0]:
            continue
        # If reciprocal has already been checked, move to next reciprocal
        elif (recip, obj, subj) in checking:
            continue
        else:
            # We assume that the type requirements of the reciprocal are the inverse
            # of that of the original: no need for a type check.

            # We assume that the only reciprocals of the reciprocals are the original
            # relation and its reciprocals, so no need for a reciprocal check on the
            # reciprocal.

            # Temporarily add to checking to avoid infinite loops
            checking.append((recip, obj, subj))
            # Check the share requirements of the reciprocal
            if checkShare(recip, obj, subj, checking) is False:
                print('Share check on reciprocal failed')
                checking.remove((recip, obj, subj))
                return False
            # Check the one-hop requirements of the reciprocal
            print(f'Checking reciprocal’s onehop.')
            if checkOneHop(recip, obj, subj, checking) is False:
                print('One-hop check failed')
                checking.remove((recip, obj, subj))
                return False

            # Check the not requirements of the reciprocal
            for i in recip.getNots():
                ## Check if relation exists
                if subj in obj.getRel(i)[0]:
                    print('Blocking relation present')
                    checking.remove((recip, obj, subj))
                    return False
                ## Check if relation would be needed
                elif (i, obj, subj) in checking:
                    print('Would require blocking relation')  
                    checking.remove((recip, obj, subj))
                    return False
            
            # Check the max requirement of the reciprocal
            ## Count the number of instances for the reciprocal from the object
            recip_count = len(obj.getRel(recip)[0])
            for i in checking:
                if (i[0] == recip) and (i[1] == obj):
                    recip_count += 1
            ## Check the max requirement
            if recip_count > recip.getMax():
                # printChecking(checking)
                # print(obj.getRel(recip)[1])
                # print(recip_count)
                print('Too many instances of reciprocal relation', recip.getName())
                return False
            
            # Check the gen requirement on the reciprocal
            if recip.getGen() is not None:
                if subj.getProp('Generation') - obj.getProp('Generation') != recip.getGen():
                    # print('Generational mismatch between', subj.getProp('Name'), 'and', obj.getProp('Name'), 'for relation', rel.getName())
                    return False
        checking.append((recip, obj, subj))
    return True

def checkShare(rel:relation, subj:node, obj:node, checking:list) -> bool:
    """
    Check wether the sharing requirements on a relation can be implemented

    :param rel: The original relation
    :param subj: The subject of the original relation
    :param obj: The object of the original relation
    :param checking: The buffer of assumed relations
    """
    print(f'Call to checkShare for relation {rel.getName()} between {subj.getProp("Name")} and {obj.getProp("Name")}')
    # Iterate over shared relations
    for shared in rel.getShare():
        # print('> Shared relation being checked:', shared.getName())
        # If the shared relation is the same as the original one,
        # then check for transitivity
        if shared == rel:
            # Iterate over those who stand in the relation with
            # the original object except for the original subject,
            # and check if the relation can be implemented between
            # the original subject and that node
            for node in obj.getRel(shared)[0]:
                # print('>> Name of object of shared relation:', node.getProp('Name'))
                # Get list of nodes that stand in the shared relation with the subject
                rel_set = subj.getRel(shared)[0]
                # Move to next node if the node is the subject of the
                # original relation, or if the relation is already in place
                if node in rel_set:
                    continue
                # Check the not requirements of the relation
                elif node == subj:
                    continue
                # Check if shared relation has been checked
                elif (shared, subj, node) in checking:
                    continue
                # Check the type requirements of the relation
                elif (shared.getClasses()) != (subj.getClass(), node.getClass()):
                    print(subj.getClass(), node.getClass())
                    print('Classes incorrect')
                    return False
                # Check the generation requirement
                elif shared.getGen() is not None:
                    if node.getProp('Generation') - subj.getProp('Generation') != shared.getGen():
                        # print(print('Generational mismatch between', subj.getProp('Name'), 'and', node.getProp('Name'), 'for relation', shared.getName()),
                        #       subj.getProp('Generation'), '-', node.getProp('Generation'), 'is not', shared.getGen())
                        return False
                # Temporarily add to the checking list, to avoid
                # infinite loops
                checking.append((shared, subj, node))
                # Check the share requirements of the relation
                if checkShare(shared, subj, node, checking) is False:
                    print('Share check failed')
                    checking.remove((shared, subj, node))
                    return False
                # Check the reciprocal requirements of the relation
                elif checkRecip(shared, subj, node, checking) is False:
                    print('Reciprocity check failed')
                    checking.remove((shared, subj, node))
                    return False
                if checkOneHop(shared, subj, node, checking) is False:
                    print('One-hop check failed')
                    checking.remove((shared, subj, node))
                    return False
                # Check the not requirements of the relation
                for block in shared.getNots():
                    ## Check if relation exists
                    if node in subj.getRel(block)[0]:
                        print('Blocking relation present')
                        checking.remove((shared, subj, node))
                        return False
                    ## Check if relation would be needed
                    elif (block, subj, node) in checking:
                        print('Would require blocking relation')
                        checking.remove((shared, subj, node))
                        return False
                # Check the max requirement of the relation
                ## Count the number of instances for this relation and subject
                rel_count = len(rel_set)
                for i in checking:
                    if (i[0] == shared) and (i[1] == subj):
                        rel_count += 1
                ## Check the max requirement
                if rel_count >= rel.getMax():
                    print('Too many instances of relation')
                    checking.remove((shared, subj, node))
                    return False
        else:
            for node in obj.getRel(shared)[0]:
                # Get list of nodes that stand in the shared relation with the subject
                rel_set = subj.getRel(shared)[0]
                # Move to next node if the node is the subject of the
                # original relation, or if the relation is already in place
                if node in rel_set:
                    continue
                elif node == subj:
                    continue
                # Check if shared relation has been checked
                elif (shared, subj, node) in checking:
                    continue
                # Check the type requirements of the relation
                elif (shared.getClasses()) != (subj.getClass(), node.getClass()):
                    print(subj.getClass(), node.getClass())
                    print('Classes incorrect')
                    return False
                # Temporarily add to the checking list, to avoid
                # infinite loops
                checking.append((shared, subj, node))
                # Check the share requirements of the relation
                if checkShare(shared, subj, node, checking) is False:
                    print('Share check failed')
                    return False
                # Check the reciprocal requirements of the relation
                elif checkRecip(shared, subj, node, checking) is False:
                    print('Reciprocity check failed')
                    return False
                checking.remove((shared, subj, node))
                # Check the not requirements of the relation
                for block in shared.getNots():
                    ## Check if relation exists
                    if node in subj.getRel(block)[0]:
                        print('Blocking relation present')
                        return False
                    ## Check if relation would be needed
                    elif (block, subj, node) in checking:
                        print('Would require blocking relation')
                        return False
                # Check the max requirement of the relation
                ## Count the number of instances for this relation and subject
                rel_count = len(rel_set)
                for i in checking:
                    if (i[0] == shared) and (i[1] == subj):
                        rel_count += 1
                ## Check the max requirement
                if rel_count >= shared.getMax():
                    print('Too many instances of relation')
                    return False
                # Check the generation requirement
                if shared.getGen() is not None:
                    if node.getProp('Generation') - subj.getProp('Generation') != shared.getGen():
                        # print('Generational mismatch between', subj.getProp('Name'), 'and', node.getProp('Name'), 'for relation', shared.getName(),
                        #       subj.getProp('Generation'), '-', node.getProp('Generation'), 'is not', shared.getGen())
                        return False
                checking.append((shared, subj, node))
    return True

def checkOneHop(rel:relation, subj:node, obj:node, checking:list) -> bool:
    # Iterate over hopped relations
    print(f'Call to checkOneHop for relation {rel.getName()} between {subj.getProp("Name")} and {obj.getProp("Name")}')
    for pair in rel.getOneHop():
        onehop = pair[0]
        new_rel = pair[1]
        print(f'> Checking hopped relation {onehop.getName()}')
        # Check if the hopped relation is not present
        current = obj.getRel(onehop)[0]
        potential = True in [(tup[0] == onehop) & (tup[1] == obj) for tup in checking]
        if (current == set()) & (potential == False):
            print(f'>> Hopped relation {onehop.getName()} not present, continuing on')
            continue # Hopped relation not present, ignore.
        # Get all z such that objONEHOPz
        new_objs = obj.getRel(onehop)[0] # objONEHOPz in place
        for tup in checking: # objONEHOPz in checking
            if (tup[0] == onehop) & (tup[1] == obj):
                new_objs.add(tup[2])
        temp = new_objs.copy()
        for new_obj in temp:
            if new_obj == subj:
                new_objs.remove(new_obj)
        print(f'>> New objects to be tested: {list(map(lambda x: x.getProp("Name"), new_objs))} for {subj.getProp("Name")} {new_rel.getName()}.')
        # Attempt to implement subjREL2z for all z from above
        for new_obj in new_objs:
            if (new_obj in subj.getRel(new_rel)) | ((new_rel, subj, new_obj) in checking):
                print(f'>>> {subj.getProp("Name")} {new_rel.getName()} {new_obj.getProp("Name")} is present, moving on')
                continue
            elif ((new_rel, subj, new_obj) not in checking):
                checking.append((new_rel, subj, new_obj))
            elif checkShare(new_rel, subj, new_obj, checking) is False:
                print(f'>>> Share check failed for {subj.getProp("Name")} {new_rel.getName()} {new_obj.getProp("Name")}')
                if (new_rel, subj, new_obj) in checking:
                    checking.remove((new_rel, subj, new_obj))
                return False
            print(f'Checking reciprocal of relation {subj.getProp("Name")} {new_rel.getName()} {new_obj.getProp("Name")}')
            if checkRecip(new_rel, subj, new_obj, checking) is False:
                print(f'>>> Recip check failed for {subj.getProp("Name")} {new_rel.getName()} {new_obj.getProp("Name")}')
                if (new_rel, subj, new_obj) in checking:
                    checking.remove((new_rel, subj, new_obj))
                return False
            for i in new_rel.getNots(): # Check if blocking relations are present
                if (new_obj in subj.getRel(i)[0]) | ((i, subj, new_obj) in checking):
                    print('>>> Blocking relation present or required')
                    if (new_rel, subj, new_obj) in checking:
                        checking.remove((new_rel, subj, new_obj))
                    return False
            # For now, we say that the we will not check the onehops of the onehops. to be fixed later.
        # Check the max requirements on the new relation.
        counter = len(subj.getRel(new_rel)[0])
        for tup in checking:
            if (tup[0] == new_rel) & (tup[1] == subj):
                counter += 1
        if counter > new_rel.getMax():
            print(f'Maximum number of relations exceeded for {subj.getProp("Name")} {new_rel.getName()}')
            if (new_rel, subj, new_obj) in checking:
                checking.remove((new_rel, subj, new_obj))
            return False
        print(f'>> checkOneHop success for relation {onehop.getName()} in implementing relation {new_rel.getName()}')
        for new_obj in new_objs:
            if ((new_rel, subj, new_obj) not in checking):
                checking.append((new_rel, subj, new_obj))
    return True