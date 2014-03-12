import networkx as nx
import numpy as np
from cvxopt import spmatrix

def design_network(topography, diameters, verbose=True):
    """ builds the design problem and solves it
    """

    # expand the multi-faucets nodes
    topo = nx.DiGraph(topography)
    faucets = [n for n,d in topo.nodes_iter(data=True) if d['type']=="faucet"]
    for f in faucets:
        if topo.node[f]['nb_faucets'] > 1:
            for i in range(topo.node[f]['nb_faucets']):
                g = '%s_%d' % (f,i+1)
                topo.add_node(g,{'altitude':topo.node[f]['altitude'],
                                 'nb_faucets':1,
                                 'load_factor':1,
                                 'type':'dispatch'})
                topo.add_edge(f,g,{'length':1})

    # Number of non-zeros elements in A*
    # This part should be removed later
    #tank = [n for n,d in topo.nodes_iter(data=True) if d['type']=="tank"][0]
    #all_paths = [nx.shortest_path_length(topo,tank,n) for n in topo.nodes_iter()]
    #nb_pipes  = topo.number_of_edges()
    #nb_nodes  = topo.number_of_nodes()
    #nb_diams  = len(diameters)
    #nb_anz = ((sum(all_paths) + nb_pipes) * nb_diams + nb_nodes) - 1 + (nb_diams * nb_pipes)
    #print nb_anz

    # Useful values
    tank = [n for n,d in topo.nodes_iter(data=True) if d['type']=="tank"][0]
    nb_pipes  = topo.number_of_edges()
    nb_nodes  = topo.number_of_nodes()
    nb_diams  = len(diameters)
    pipes     = topo.edges(data=True)
    if verbose:
        print("Nb pipes: %d" % nb_pipes)
        print("Nb nodes: %d" % nb_nodes)
        print("Nb diameters: %d" % nb_diams)

    # Diameters temperature-dependant values
    a =  calcul_a(topo.graph['watertemp'])
    for diam in diameters:
        if diam['type']==1: # PVC
            diam['p']    =  2 - 0.219
            diam['q']    =  5 - 0.219
            diam['beta'] =  0.0826 * 0.235 * (a * 1e6)**(-0.219)
#TODO values for IRON pipes (source: DiameterVector)
#     elif diam['type']==2: # IRON
#        Double ironA = new Double(0);
#        Double ironB = new Double(0);
#        calculIron(rugosite / diameter, ironA, ironB);
#        p = 2 - ironB.doubleValue();
#        q = 5 - ironB.doubleValue();
#        beta = 0.0826 * ironA.doubleValue() * Math.pow(a * 1e6,
#            -ironB.doubleValue());

    # Vector c =
    #      nb_pipes * nb_diam             nb_pipes
    # [ diam_costs      ...        ,  very_high_cost ]
    diam_cost = [diam['cost'] for diam in diameters]
    #TODO check what is a very high cost
    #very_high_cost = max(diam_cost)
    very_high_cost = 6.86e+02
    c = diam_cost * nb_pipes + [very_high_cost] * nb_pipes

    #  Matrix A
    #                                    nb_pipes * nb_diam                 nb_pipes
    #              [ [1,1,1...]        0           0        ,                ]
    #  nb_pipes    [      0         [1,1,1...]     0        ,        0       ]
    #              [      0            0        [1,1,1...]  ,                ]
    values = [1] * (nb_pipes * nb_diams)
    rows   = sum([ [i] * nb_diams for i in range(nb_pipes)], [])
    cols   = range(nb_pipes * nb_diams)
    A = spmatrix(values,rows,cols,size=(nb_pipes,nb_pipes*nb_diams+nb_pipes))

    #  Vector b
    #    nb_pipes
    #  [ length ...]
    b = [ d['length'] for n1,n2,d in pipes ]

    #  Matrix G_up
    #                                    nb_pipes * nb_diam                      nb_pipes
    #              [ [f(d1),f(d2),...]           0                  0        ,              ]
    #  nb_pipes    [ [f(d1),f(d2),...]  [f(d1),f(d2),...]           0        ,      -I      ]
    #              [ [f(d1),f(d2),...]          0          [f(d1),f(d2),...] ,              ]
    #     1        [ [c(d1),c(d2),...]  [c(d1),c(d2),...]  [c(d1),c(d2),...] ,      0       ]
    values = []
    rows = []
    cols = []
    row = 0
    for n1,n2,d in pipes:

        # left part of matrix
        print(tank)
        print(n2)
        print(nx.shortest_path(topo,tank,n2))
        print(nx.to_edgelist(topo,nx.shortest_path(topo,tank,n2)))
        path = nx.shortest_path(topo,tank,n2)
        for idx in range(len(path))[1:]:

            for diam in diameters:
                value = ( topo.graph['targetflow'] * topo.node[path[idx]]['load_factor'] / 1000 ) ** diam['p']
                value /= diam['diam']**diam['q']
                value *= diam['beta']
                values.append(value)

            rows.extend( [row] * nb_diams )
            col = i_pipe(path[idx-1],path[idx],pipes) * nb_diams
            cols.extend( [i + col for i in range(nb_diams)] )

        # right part
        values.append(-1.0)
        rows.append(row)
        cols.append(nb_pipes * nb_diams + row)

        row += 1

    #TODO check if ok to add length constraint
    # length constraint
    #values.extend( [1.0] * nb_diams * nb_pipes )
    #rows.extend( [ nb_pipes ] * nb_diams * nb_pipes )
    #cols.extend( range(nb_diams * nb_pipes))

    # max cost constraint
    values.extend( [diam["cost"] for diam in diameters] * nb_pipes )
    rows.extend( [ nb_pipes ] * nb_diams * nb_pipes )
    cols.extend( range(nb_diams * nb_pipes))

    G_up = spmatrix(values,rows,cols,size=(nb_pipes+1,nb_pipes*nb_diams+nb_pipes))

    return (c, A, b, G_up)


def calcul_a(temperature):
    """
    Return the a coefficient (as in neatwork 3.x)
    """
    #transform celsius in fahrenheit
    temp = ((9.0 * (temperature)) / 5) + 32
    t = [32, 68, 77, 86, 104]
    a = [0.69, 1.27, 1.43, 1.59, 1.99]
    return np.interp(temp, t, a)

def i_pipe(n1,n2,pipes):
    """
    Return the index of pipe given end node
    """
    for index, item in enumerate(pipes):
        if (item[0]==n1) and (item[1]==n2):
            return index
