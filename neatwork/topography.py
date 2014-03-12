import networkx as nx
from networkx.algorithms.traversal.depth_first_search import dfs_tree
from scipy.stats import norm
from math import sqrt
import sys

class Topography(nx.DiGraph):
    """represents a water network topography.
    A Topography is a directed graph containing nodes and directed edges.
    To build a topography, you build a DiGraph from the library NetworkX (http://networkx.lanl.gov) and can
    use any proposed methods to add and modify nodes, edges and their properties.

    Node's properties:
     altitude: altitude in meter, can be relative to the tank
     type: 'tank' for the source, 'node' for an intermediate node, 'faucet' for a delivery node
     nb_faucets: number of faucets (integer). Required only for node of type 'faucet'

    Edge's properties:
     length: length in meter.

    Graph properties:
      faucetcoef
      limitbudget
      opentaps
      orifcoef
      pipelength
      servicequal
      seuil
      targetflow
      watertemp

    By convention, a Topography must have
     - only one node of type 'tank'
    """

    def load_tpo(self,filename):
        """ load and convert from neatwork 3.x topography file (*.tpo) """
        NODE_TYPE = {0: 'tank', 1: 'node', 2: 'faucet'}
        try:
            f = open(filename)
            for line in f:
                line = line.split(',')
                if len(line)==6: # nodes
                    self.add_node(line[0],{'altitude': float(line[1]),
                                           'type': NODE_TYPE[int(line[5])],
                                           'nb_faucets': int(line[4])})
                elif len(line)==3: # pipes
                    self.add_edge(line[0],line[1],{'length': float(line[2])})
                elif len(line)==2: # graph properties
                    self.graph[line[0]] = float(line[1])
            f.close()
        except:
            print('Something went wrong.')
            print("Unexpected error:", sys.exc_info()[0])
            raise

    def is_valid(self):
        """ Return True if the topography is valid """
        if len([n for n,d in self.nodes_iter(data=True) if d['type']=="tank"]) != 1:
            print('A topography must contain only one tank')
            return False
        return True

    #TODO check load_factors
    def set_load_factors(self):
        """ attributes to each node the theoretical load factor
        """
        tank = [n for n,d in self.nodes(data=True) if d['type']=="tank"][0]
        faucets = [n for n,d in self.nodes(data=True) if d['type']=="faucet"]
        # initialize attributes
        for n in self.node:
            self.node[n]['load_taps'] = 0
            self.node[n]['load_factor'] = 0
        # compute load taps per node
        for f in faucets:
            #path tank-faucet
            for n in nx.shortest_path(self,tank,f):
                self.node[n]['load_taps'] += self.node[f]['nb_faucets']
        # compute theoretical flow as a function of load taps
        flow = self.flow_for_load_taps(self.graph['targetflow'],self.graph['opentaps'],self.graph['servicequal'])
        # attributes load_factor
        for n in self.node:
            self.node[n]['load_factor'] = flow[self.node[n]['load_taps'] - 1] / self.graph['targetflow']

    def flow_for_load_taps(self, outflow, open_taps, service_quality):
        """ Return an array of probable flow where the index is the number of load taps - 1
        """
        nb_faucets = sum([self.node[n]['nb_faucets'] for n,d in self.nodes(data=True) if d['type']=="faucet"])
        proba = [outflow]
        for i in range(2,nb_faucets+1):
            p = (service_quality * (1-(1-open_taps)**i)) + (1-open_taps)**i
            res = (norm.ppf(p) * sqrt(i * open_taps * (1 - open_taps))) + (i * open_taps)
            proba.append( max(min(outflow*res,outflow*i),outflow) )
        return proba
