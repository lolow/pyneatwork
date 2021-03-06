#! /usr/bin/env python
# Name: PyNeatwork
# A portage of neatwork in Python
# Author: Laurent Drouet
# Copyright: 2010 Laurent Drouet

import networkx as nx
from cvxopt import matrix, spmatrix, sparse, solvers, spdiag

#Read Sample Network topography as a networkX graph

G=nx.DiGraph(name = 'Sample Network', orif_coef = 0.59, pipe_length = 6,
limit_budget = 1e9, watertemp=21.0, opentaps=0.4, servicequal=0.8,
faucetcoef=2.0e-8, seuil=0.1, target_flow=0.2)

G.add_node("Source",{"altitude":0,"type":"tank"})
G.add_node("A",{"altitude":-10,"type":"node"})
G.add_node("B",{"altitude":-15,"type":"node"})
G.add_node("C",{"altitude":-20,"type":"node"})
G.add_node("P1",{"altitude":-9,"type":"faucet","nb_faucets":3})
G.add_node("P2",{"altitude":-18,"type":"faucet","nb_faucets":2})
G.add_node("P3",{"altitude":-12,"type":"faucet","nb_faucets":1})
G.add_node("P4",{"altitude":-50,"type":"faucet","nb_faucets":1})

G.add_edge("Source","A",{"lenght":20})
G.add_edge("A","B",{"lenght":50})
G.add_edge("A","C",{"lenght":70})
G.add_edge("B","P2",{"lenght":8})
G.add_edge("C","P3",{"lenght":9})
G.add_edge("B","P1",{"lenght":12})
G.add_edge("C","P4",{"lenght":11})

nb_pipe = G.size()
nb_node = G.number_of_nodes()

#Test if the graph is connected
#if len(nx.connected_components(G.to_undirected())) > 1:
#	print "The graph is not connected"

#list of diameters [diameter,]
diameters = [ 
{'nominal':' 1/2" 1','sdr':13.5,'diam':0.0182 ,'cost':1.05	,'pressure':176.8	,'type':1,'roughness':0.0015},
{'nominal':' 3/4" ' ,'sdr':17.0,'diam':0.0235 ,'cost':1.44	,'pressure':140.8	,'type':1,'roughness':0.0015},
{'nominal':'1    "' ,'sdr':17.0,'diam':0.0295 ,'cost':2.52	,'pressure':140.8	,'type':1,'roughness':0.0015},
{'nominal':'1    "' ,'sdr':26.0,'diam':0.0304 ,'cost':1.87	,'pressure':89.6	,'type':1,'roughness':0.0015},
{'nominal':'1 1/4"' ,'sdr':17.0,'diam':0.0372 ,'cost':3.71	,'pressure':140.8	,'type':1,'roughness':0.0015},
{'nominal':'1 1/4"' ,'sdr':26.0,'diam':0.0389 ,'cost':2.46	,'pressure':89.6	,'type':1,'roughness':0.0015},
{'nominal':'1 1/4"' ,'sdr':32.5,'diam':0.0391 ,'cost':2.36	,'pressure':70.4	,'type':1,'roughness':0.0015},
{'nominal':'1 1/2"' ,'sdr':17.0,'diam':0.0426 ,'cost':4.84	,'pressure':140.8	,'type':1,'roughness':0.0015},
{'nominal':'1 1/2"' ,'sdr':26.0,'diam':0.0446 ,'cost':3.4	,'pressure':89.6	,'type':1,'roughness':0.0015}    ,
{'nominal':'1 1/2"' ,'sdr':32.5,'diam':0.0453 ,'cost':2.76	,'pressure':70.4	,'type':1,'roughness':0.0015},
{'nominal':'1 1/2"' ,'sdr':41.0,'diam':0.0459 ,'cost':2.45	,'pressure':56.32	,'type':1,'roughness':0.0015},
{'nominal':'2    "' ,'sdr':17.0,'diam':0.0532 ,'cost':7.71	,'pressure':140.8	,'type':1,'roughness':0.0015},
{'nominal':'2    "' ,'sdr':26.0,'diam':0.0557 ,'cost':5.35	,'pressure':89.6	,'type':1,'roughness':0.0015},
{'nominal':'2    "' ,'sdr':32.5,'diam':0.0566 ,'cost':4.37	,'pressure':70.4	,'type':1,'roughness':0.0015},
{'nominal':'2    "' ,'sdr':41.0,'diam':0.05739,'cost':3.68	,'pressure':56.32	,'type':1,'roughness':0.0015},
{'nominal':'2 1/2"' ,'sdr':17.0,'diam':0.06445,'cost':11.72	,'pressure':140.8	,'type':1,'roughness':0.0015},
{'nominal':'2 1/2"' ,'sdr':26.0,'diam':0.0674 ,'cost':7.75	,'pressure':89.6	,'type':1,'roughness':0.0015},
{'nominal':'2 1/2"' ,'sdr':32.5,'diam':0.06856,'cost':5.22	,'pressure':70.4	,'type':1,'roughness':0.0015},
{'nominal':'3    "' ,'sdr':17.0,'diam':0.0784 ,'cost':16.42	,'pressure':140.8	,'type':1,'roughness':0.0015},
{'nominal':'3    "' ,'sdr':26.0,'diam':0.082  ,'cost':10.84	,'pressure':89.6	,'type':1,'roughness':0.0015},
{'nominal':'3    "' ,'sdr':32.5,'diam':0.0834 ,'cost':9.27	,'pressure':70.4	,'type':1,'roughness':0.0015},
{'nominal':'3    "' ,'sdr':41.0,'diam':0.08456,'cost':7.74	,'pressure':56.32	,'type':1,'roughness':0.0015},
{'nominal':'4    "' ,'sdr':17.0,'diam':0.1008 ,'cost':28.24	,'pressure':140.8	,'type':1,'roughness':0.0015},
{'nominal':'4    "' ,'sdr':26.0,'diam':0.1055 ,'cost':18.69	,'pressure':89.6	,'type':1,'roughness':0.0015},
{'nominal':'4    "' ,'sdr':32.5,'diam':0.1073 ,'cost':14.6	,'pressure':70.4	,'type':1,'roughness':0.0015},
{'nominal':'4    "' ,'sdr':41.0,'diam':0.10872,'cost':12.51	,'pressure':56.32	,'type':1,'roughness':0.0015},
{'nominal':'4    "' ,'sdr':50.0,'diam':0.10972,'cost':9.47	,'pressure':56.32	,'type':1,'roughness':0.0015},
{'nominal':'6    "' ,'sdr':17.0,'diam':0.14846,'cost':61.19	,'pressure':140.8	,'type':1,'roughness':0.0015},
{'nominal':'6    "' ,'sdr':26.0,'diam':0.1553 ,'cost':40.96	,'pressure':89.6	,'type':1,'roughness':0.0015},
{'nominal':'6    "' ,'sdr':32.5,'diam':0.1579 ,'cost':33.23	,'pressure':70.4	,'type':1,'roughness':0.0015},
{'nominal':'8    "' ,'sdr':17.0,'diam':0.1933 ,'cost':100.98	,'pressure':140.8	,'type':1,'roughness':0.0015},
{'nominal':'8    "' ,'sdr':26.0,'diam':0.2022 ,'cost':65.36	,'pressure':89.6	,'type':1,'roughness':0.0015},
{'nominal':'8    "' ,'sdr':32.5,'diam':0.2056 ,'cost':54.87	,'pressure':70.4	,'type':1,'roughness':0.0015},
{'nominal':'10    "','sdr':17.0,'diam':0.2409 ,'cost':156.21	,'pressure':140.8	,'type':1,'roughness':0.0015},
{'nominal':'10    "','sdr':26.0,'diam':0.2521 ,'cost':106.03	,'pressure':89.6	,'type':1,'roughness':0.0015},
{'nominal':'10    "','sdr':32.5,'diam':0.2562 ,'cost':89.83	,'pressure':70.4	,'type':1,'roughness':0.0015},
{'nominal':'12    "','sdr':17.0,'diam':0.2858 ,'cost':224.51	,'pressure':140.8	,'type':1,'roughness':0.0015},
{'nominal':'12    "','sdr':26.0,'diam':0.299  ,'cost':149.35	,'pressure':89.6	,'type':1,'roughness':0.0015},
{'nominal':'12    "','sdr':32.5,'diam':0.3039 ,'cost':115.97	,'pressure':70.4	,'type':1,'roughness':0.0015},
{'nominal':'15    "','sdr':26.0,'diam':0.3587 ,'cost':212.67	,'pressure':89.6	,'type':1,'roughness':0.0015},
{'nominal':'15    "','sdr':32.5,'diam':0.3647 ,'cost':167.03	,'pressure':70.4	,'type':1,'roughness':0.0015}]
nb_diam = len(diameters)

def faucets():
    """returns faucets names in an array"""
    return [n for n,d in G.nodes_iter(data=True) if d['type']=="faucet"]

# Compute the size of the matrix A
tank = [n for n,d in G.nodes_iter(data=True) if d['type']=="tank"][0]
path_lengths = [nx.shortest_path_length(G,tank,n) - 1 for n in G.nodes_iter()]

l = ((sum(path_lengths) + nb_pipe) * nb_diam + nb_node) - 1 + (nb_diam * nb_pipe)

# Define the sparse matrix A
for pipe in G.edges():
    for diam in diameters:
        for node in G.nodes():
            path = nx.shortest_path_length(G,tank,node) - 1

#MAKEDESIGN

#public native void mainlp(int NbNodes, int cont, int numvar, int numanz,
#		int[] bkc, double[] blc, double[] buc, int[] bkx, double[] blx,
#		double[] bux, int[] ptrb, int[] ptre, int[] sub, double[] val,
#		double[] xx, double[] c, int[] MOSEKKEY);
# selection of the 5 first diameters
nb_nodes = 13  # number of nodes
cont     = 25  # number of constraints
numvar   = 72  # number of variables
numanz   = 317 # number of non-zero-values
# bkc type of constraint
# MSK_BK_UP=1
# MSK_BK_FX=2
bkc      = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1]
blc      = [-1.0E30, -1.0E30, -1.0E30, -1.0E30, -1.0E30, -1.0E30, -1.0E30, -1.0E30, -1.0E30, -1.0E30, -1.0E30, -1.0E30, 20.0, 50.0, 70.0, 8.0, 9.0, 1.0, 1.0, 1.0, 1.0, 1.0, 12.0, 11.0, -1.0E30]
buc      = [10.0, 15.0, 20.0, 9.0, 18.0, 7.0, 7.0, 7.0, 16.0, 16.0, 10.0, 48.0, 20.0, 50.0, 70.0, 8.0, 9.0, 1.0, 1.0, 1.0, 1.0, 1.0, 12.0, 11.0, 1.0E9]
# bkc type of bound
# MSK_BK_LO=0
# MSK_BK_RA=4
bkx      = [4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
blx      = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
bux      = [20.0, 20.0, 20.0, 20.0, 20.0, 50.0, 50.0, 50.0, 50.0, 50.0, 70.0, 70.0, 70.0, 70.0, 70.0, 8.0, 8.0, 8.0, 8.0, 8.0, 9.0, 9.0, 9.0, 9.0, 9.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 12.0, 12.0, 12.0, 12.0, 12.0, 11.0, 11.0, 11.0, 11.0, 11.0, 1.0E30, 1.0E30, 1.0E30, 1.0E30, 1.0E30, 1.0E30, 1.0E30, 1.0E30, 1.0E30, 1.0E30, 1.0E30, 1.0E30]
ptrb     = [0, 14, 28, 42, 56, 70, 78, 86, 94, 102, 110, 117, 124, 131, 138, 145, 151, 157, 163, 169, 175, 180, 185, 190, 195, 200, 203, 206, 209, 212, 215, 218, 221, 224, 227, 230, 233, 236, 239, 242, 245, 248, 251, 254, 257, 260, 263, 266, 269, 272, 275, 278, 281, 284, 287, 290, 293, 296, 299, 302, 305, 306, 307, 308, 309, 310, 311, 312, 313, 314, 315, 316]
ptre     = [14, 28, 42, 56, 70, 78, 86, 94, 102, 110, 117, 124, 131, 138, 145, 151, 157, 163, 169, 175, 180, 185, 190, 195, 200, 203, 206, 209, 212, 215, 218, 221, 224, 227, 230, 233, 236, 239, 242, 245, 248, 251, 254, 257, 260, 263, 266, 269, 272, 275, 278, 281, 284, 287, 290, 293, 296, 299, 302, 305, 306, 307, 308, 309, 310, 311, 312, 313, 314, 315, 316, 317]
sub      = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 24, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 24, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 24, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 24, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 24, 1, 3, 5, 6, 7, 10, 13, 24, 1, 3, 5, 6, 7, 10, 13, 24, 1, 3, 5, 6, 7, 10, 13, 24, 1, 3, 5, 6, 7, 10, 13, 24, 1, 3, 5, 6, 7, 10, 13, 24, 2, 4, 8, 9, 11, 14, 24, 2, 4, 8, 9, 11, 14, 24, 2, 4, 8, 9, 11, 14, 24, 2, 4, 8, 9, 11, 14, 24, 2, 4, 8, 9, 11, 14, 24, 3, 5, 6, 7, 15, 24, 3, 5, 6, 7, 15, 24, 3, 5, 6, 7, 15, 24, 3, 5, 6, 7, 15, 24, 3, 5, 6, 7, 15, 24, 4, 8, 9, 16, 24, 4, 8, 9, 16, 24, 4, 8, 9, 16, 24, 4, 8, 9, 16, 24, 4, 8, 9, 16, 24, 5, 17, 24, 5, 17, 24, 5, 17, 24, 5, 17, 24, 5, 17, 24, 6, 18, 24, 6, 18, 24, 6, 18, 24, 6, 18, 24, 6, 18, 24, 7, 19, 24, 7, 19, 24, 7, 19, 24, 7, 19, 24, 7, 19, 24, 8, 20, 24, 8, 20, 24, 8, 20, 24, 8, 20, 24, 8, 20, 24, 9, 21, 24, 9, 21, 24, 9, 21, 24, 9, 21, 24, 9, 21, 24, 10, 22, 24, 10, 22, 24, 10, 22, 24, 10, 22, 24, 10, 22, 24, 11, 23, 24, 11, 23, 24, 11, 23, 24, 11, 23, 24, 11, 23, 24, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
val      = [0.5473868405992253, 0.5473868405992253, 0.5473868405992253, 0.5473868405992253, 0.5473868405992253, 0.5473868405992253, 0.5473868405992253, 0.5473868405992253, 0.5473868405992253, 0.5473868405992253, 0.5473868405992253, 0.5473868405992253, 1.0, 1.05, 0.1612947415688276, 0.1612947415688276, 0.1612947415688276, 0.1612947415688276, 0.1612947415688276, 0.1612947415688276, 0.1612947415688276, 0.1612947415688276, 0.1612947415688276, 0.1612947415688276, 0.1612947415688276, 0.1612947415688276, 1.0, 1.44, 0.05438468283844068, 0.05438468283844068, 0.05438468283844068, 0.05438468283844068, 0.05438468283844068,
 0.05438468283844068, 0.05438468283844068, 0.05438468283844068, 0.05438468283844068, 0.05438468283844068, 0.05438468283844068, 0.05438468283844068, 1.0, 2.52, 0.04710608976237816, 0.04710608976237816, 0.04710608976237816, 0.04710608976237816, 0.04710608976237816, 0.04710608976237816, 0.04710608976237816, 0.04710608976237816, 0.04710608976237816, 0.04710608976237816, 0.04710608976237816, 0.04710608976237816, 1.0, 1.87, 0.017944438070566896, 0.017944438070566896, 0.017944438070566896, 0.017944438070566896, 0.017944438070566896, 0.017944438070566896, 0.017944438070566896, 0.017944438070566896, 0.017944438070566896,
 0.017944438070566896, 0.017944438070566896, 0.017944438070566896, 1.0, 3.71, 0.24982670991514738, 0.24982670991514738, 0.24982670991514738, 0.24982670991514738, 0.24982670991514738, 0.24982670991514738, 1.0, 1.05, 0.07361473024934678, 0.07361473024934678, 0.07361473024934678, 0.07361473024934678, 0.07361473024934678, 0.07361473024934678, 1.0, 1.44, 0.02482110525059934, 0.02482110525059934, 0.02482110525059934, 0.02482110525059934, 0.02482110525059934, 0.02482110525059934, 1.0, 2.52, 0.021499163935727244, 0.021499163935727244, 0.021499163935727244, 0.021499163935727244, 0.021499163935727244, 0.021499163935727244,
 1.0, 1.87, 0.008189820419391695, 0.008189820419391695, 0.008189820419391695, 0.008189820419391695, 0.008189820419391695, 0.008189820419391695, 1.0, 3.71, 0.1732521927172711, 0.1732521927172711, 0.1732521927172711, 0.1732521927172711, 0.1732521927172711, 1.0, 1.05, 0.0510510402843698, 0.0510510402843698, 0.0510510402843698, 0.0510510402843698, 0.0510510402843698, 1.0, 1.44, 0.01721317513164661, 0.01721317513164661, 0.01721317513164661, 0.01721317513164661, 0.01721317513164661, 1.0, 2.52, 0.01490944380894231, 0.01490944380894231, 0.01490944380894231, 0.01490944380894231, 0.01490944380894231, 1.0, 1.87,
 0.005679554224214926, 0.005679554224214926, 0.005679554224214926, 0.005679554224214926, 0.005679554224214926, 1.0, 3.71, 0.1732521927172711, 0.1732521927172711, 0.1732521927172711, 0.1732521927172711, 1.0, 1.05,  0.0510510402843698, 0.0510510402843698, 0.0510510402843698, 0.0510510402843698, 1.0, 1.44, 0.01721317513164661, 0.01721317513164661, 0.01721317513164661, 0.01721317513164661, 1.0, 2.52, 0.01490944380894231, 0.01490944380894231, 0.01490944380894231, 0.01490944380894231, 1.0, 1.87, 0.005679554224214926, 0.005679554224214926, 0.005679554224214926, 0.005679554224214926, 1.0, 3.71, 0.10923693316294816,
 0.10923693316294816, 0.10923693316294816, 1.0, 1.05, 0.032188100987230704, 0.032188100987230704, 0.032188100987230704, 1.0, 1.44, 0.01085304856398714, 0.01085304856398714, 0.01085304856398714, 1.0, 2.52, 0.009400527008116794, 0.009400527008116794, 0.009400527008116794, 1.0, 1.87, 0.003581005674187106, 0.003581005674187106, 0.003581005674187106, 1.0, 3.71, 0.04782788984936741, 1.0, 1.05, 0.01409311762882556, 1.0, 1.44, 0.0047518581510697065, 1.0, 2.52, 0.004115891551070336, 1.0, 1.87, 0.0015678941176378055, 1.0, 3.71, 0.04782788984936741, 1.0, 1.05, 0.01409311762882556, 1.0, 1.44, 0.0047518581510697065, 1.0, 2.52, 0.004115891551070336,
 1.0, 1.87, 0.0015678941176378055, 1.0, 3.71, 0.04782788984936741, 1.0, 1.05, 0.01409311762882556, 1.0, 1.44, 0.0047518581510697065, 1.0, 2.52, 0.004115891551070336, 1.0, 1.87, 0.0015678941176378055, 1.0, 3.71, 0.04782788984936741, 1.0, 1.05, 0.01409311762882556, 1.0, 1.44, 0.0047518581510697065, 1.0, 2.52, 0.004115891551070336, 1.0, 1.87, 0.0015678941176378055, 1.0, 3.71, 0.04782788984936741, 1.0, 1.05, 0.01409311762882556, 1.0, 1.44, 0.0047518581510697065, 1.0, 2.52, 0.004115891551070336, 1.0, 1.87, 0.0015678941176378055, 1.0, 3.71, 0.04782788984936741, 1.0, 1.05, 0.01409311762882556, 1.0, 1.44, 0.0047518581510697065, 1.0, 2.52,
 0.004115891551070336, 1.0, 1.87, 0.0015678941176378055, 1.0, 3.71, 0.04782788984936741, 1.0, 1.05, 0.01409311762882556, 1.0, 1.44, 0.0047518581510697065, 1.0, 2.52, 0.004115891551070336, 1.0, 1.87, 0.0015678941176378055,
 1.0, 3.71, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0]
xx       = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
c     = [1.05, 1.44, 2.52, 1.87, 3.71, 1.05, 1.44, 2.52, 1.87, 3.71, 1.05, 1.44, 2.52, 1.87, 3.71, 1.05, 1.44, 2.52, 1.87, 3.71, 1.05, 1.44, 2.52, 1.87, 3.71, 1.05, 1.44, 2.52, 1.87, 3.71, 1.05, 1.44, 2.52, 1.87, 3.71, 1.05, 1.44, 2.52, 1.87, 3.71, 1.05, 1.44, 2.52, 1.87, 3.71, 1.05, 1.44, 2.52, 1.87, 3.71, 1.05, 1.44, 2.52, 1.87, 3.71, 1.05, 1.44, 2.52, 1.87, 3.71, 686.35, 686.35, 686.35, 686.35, 686.35, 686.35, 686.35, 686.35, 686.35, 686.35, 686.35, 686.35]

###conversion
# h & b
h = [buc[i] for i in range(0,len(bkc)) if bkc[i]==1] # MSK_BK_UP
b = [buc[i] for i in range(0,len(bkc)) if bkc[i]==2] # MSK_BK_FX

h_i = [i for i in range(0,len(bkc)) if bkc[i]==1] # MSK_BK_UP
b_i = [i for i in range(0,len(bkc)) if bkc[i]==2] # MSK_BK_FX

# G & A
G_val = []
G_col = []
G_row = []
A_val = []
A_col = []
A_row = []
for col in range(0,numvar):
    for ptr in range(ptrb[col],ptre[col]):
        row = sub[ptr]
        nz  = val[ptr]
        if bkc[row] == 1: # MSK_BK_UP
            G_row.append(row)
            G_col.append(col)
            G_val.append(nz)
        if bkc[row] == 2: # MSK_BK_FX
            A_row.append(row)
            A_col.append(col)
            A_val.append(nz)

Gup = spmatrix(G_val, G_row, G_col,tc='d')[h_i,:]
G_val = []
G_col = []
G_row = []
row=0
for col in range(0,numvar):
   if bkx[col] == 4: # MSK_BK_RA
       G_row.append(row)
       row+=1
       G_col.append(col)
       G_val.append(-1.)
       h.append(-blx[col])
       G_row.append(row)
       row+=1
       G_col.append(col)
       G_val.append(1.)
       h.append(bux[col])
   if bkx[col] == 0: # MSK_BK_LO
       G_row.append(row)
       row+=1
       G_col.append(col)
       G_val.append(-1.)
       h.append(-blx[col])
Glo = spmatrix(G_val, G_row, G_col,tc='d')
cvx_c = matrix(c,tc='d')
cvx_G = sparse([Gup,Glo])
cvx_h = matrix(h,tc='d')
cvx_A = spmatrix(A_val, A_row, A_col,(max(A_row)+1,numvar),tc='d')[b_i,:]
cvx_b = matrix(b,tc='d')

#solver
sol = solvers.lp(cvx_c, cvx_G, cvx_h, cvx_A, cvx_b,solver='glpk')
#sol = solvers.lp(cvx_c, cvx_G, cvx_h, cvx_A, cvx_b)
print(sol['status'])

#compare results
xx = [1.0030293214248066E-10, 16.63268981443864, 1.586409999317768E-10, 3.367310185236658, 6.209368877984813E-11, 9.614756651563536E-10, 49.999999998359655, 1.2110479851006636E-10, 4.930874299888298E-10, 5.431117108450093E-11, 69.99999999948493, 2.6846650630771025E-10, 6.871228356028613E-11, 1.2184889340117833E-10, 3.8498714023366686E-11, 0.17709369905114694, 7.822906300387782, 1.1388531447280754E-10, 3.948951751563742E-10, 5.116219534180286E-11, 8.999999999505745, 2.5597657807487433E-10, 7.168462736481486E-11, 1.2496336527877475E-10, 3.992374309754019E-11, 0.9999999994078325, 3.2981130190933414E-10, 7.75011238047531E-11, 1.43947408955755E-10, 4.245452501253013E-11, 0.9999999994078168, 3.2982292495440136E-10, 7.750199092965994E-11, 1.4395041812464637E-10, 4.245480328188924E-11, 0.9999999994078325, 3.298113027692958E-10, 7.750112384783852E-11, 1.4394740909374477E-10, 4.245452503072499E-11, 0.9999999994874915, 2.701167330842692E-10, 7.313821723471396E-11, 1.2995247436108075E-10, 4.084825308384569E-11, 0.9999999994874949, 2.701143627923687E-10, 7.313799132796649E-11, 1.299517322885445E-10, 4.084818102028087E-11, 11.999999999478977, 2.7505502850281407E-10, 7.276303556170973E-11, 1.303157009168878E-10, 4.030080381603956E-11, 10.999999999479911, 2.746752325976377E-10, 7.269073379536456E-11, 1.301235928689343E-10, 4.027827951110438E-11, 1.5913122618989565E-13, 1.5939943830415639E-13, 1.589488831793831E-13, 1.5945653940172133E-13, 1.5870476284704192E-13, 1.5740581911333014E-13, 1.5740590407856902E-13, 1.574058191158542E-13, 1.585583715044462E-13, 1.585583472412238E-13, 1.6013358499622995E-13, 0.0]
diff = matrix(xx) - matrix(sol['x'])
print(diff)


################################


from neatwork.topography import Topography
from neatwork.designer import design_network


# load topography
topo = Topography(name = 'Sample Network')
topo.load_tpo('projects/base_example_sml.tpo')
topo.set_load_factors()

# load diameters
import csv
diameters = []
csv_reader = csv.reader(open('neatwork/diameters.csv', 'r'), delimiter=',')
for row in csv_reader:
    diameters.append({'nominal':   row[0],
                      'sdr':       float(row[1]),
                      'diam':      float(row[2]),
                      'cost':      float(row[3]),
                      'pressure':  float(row[4]),
                      'type':      int(row[5]),
                      'roughness': float(row[6])})

diam5 = diameters[:5]

(c, A, b, G_up) = design_network(topo,diam5)

rows = Gup.size[0]
cols = Gup.size[1]
filename = "comp_g_up.txt"
file = open(filename, "w")
file.write("G_up\n")
for i in range(rows):
    for j in range(cols):
        file.write("%10.5f " % G_up[i,j])
    file.write("\n")
file.write("Gup\n")
for i in range(rows):
    for j in range(cols):
        file.write("%10.5f " % Gup[i,j])
    file.write("\n")
file.close()








##################################


def makesimulation():
    #MAKESIMULATION
    #public void mainnlp(int cont, int numvar, int numanz, int NbPipes,
    #			int[] bkc, double[] blc, double[] buc, int[] bkx, int[] ptrb,
    #			int[] ptre, double[] blx, double[] bux, double[] x, double[] y,
    #			double[] c, int[] sub, double[] val, double[] PipesConst,
    #			double[] TapsConst1, double[] TapsConst2, double[] oprfo,
    #			double[] oprgo, double[] oprho, int[] opro, int[] oprjo) {
    # case MSK_OPR_POW:
    #      if ( fxj )
    #        fxj[0] = f*pow(xj,g);
    #
    #      if ( grdfxj )
    #        grdfxj[0] = f*g*pow(xj,g-1.0);
    #
    #       if ( hesfxj )
    #        hesfxj[0] = f*g*(g-1)*pow(xj,g-2.0);
    #      break;
    #    default:
    cont=14
    numvar=21
    numanz=34
    NbPipes=13
    bkc=[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] #modified later
    blc=[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] #modified later
    buc=[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] #modified later
    ptrb = [0, 1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 28, 29, 30, 31, 32, 33]
    ptre = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 28, 29, 30, 31, 32, 33, 34]
    blx = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    bux = [140.0, 140.0, 140.0, 140.0, 140.0, 140.0, 140.0, 140.0, 140.0, 140.0, 140.0, 140.0, 140.0, 140.0, 140.0, 140.0, 140.0, 140.0, 140.0, 140.0, 140.0]
    x = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    y = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    c = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0] #modified later
    sub = [0, 0, 1, 1, 2, 2, 3, 2, 4, 3, 5, 4, 6, 3, 7, 5, 8, 5, 9, 5, 10, 6, 11, 6, 12, 4, 13, 7, 8, 9, 10, 11, 12, 13]
    val = [1.0, -1.0, 1.0, -1.0, 1.0, -1.0, 1.0, -1.0, 1.0, -1.0, 1.0, -1.0, 1.0, -1.0, 1.0, -1.0, 1.0, -1.0, 1.0, -1.0, 1.0, -1.0, 1.0, -1.0, 1.0, -1.0, 1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0]
    PipesConst = [0.1560557453662784, 1.2468083477323857, 4.452886956187092, 21.156501311195587, 0.7124619129899348, 2.7201215971537183, 3.6268287962049577, 0.30223573301707984, 0.30223573301707984, 0.30223573301707984, 0.30223573301707984, 0.30223573301707984, 3.324593063187878]
    TapsConst1 = [-12.0, -9.0, -9.0, -9.0, -18.0, -18.0, -50.0]
    TapsConst2 = [47.83271862139916, 16.666666666666664, 16.666666666666664, 16.666666666666664, 16.666666666666664, 16.666666666666664, 174.44480468749992]
    oprfo = [0.1560557453662784, 1.2468083477323857, 4.452886956187092, 21.156501311195587, 0.7124619129899348, 2.7201215971537183, 3.6268287962049577, 0.30223573301707984, 0.30223573301707984, 0.30223573301707984, 0.30223573301707984, 0.30223573301707984, 3.324593063187878, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    oprgo = [2.7809999999999997, 2.7809999999999997, 2.7809999999999997, 2.7809999999999997, 2.7809999999999997, 2.7809999999999997, 2.7809999999999997, 2.7809999999999997, 2.7809999999999997, 2.7809999999999997, 2.7809999999999997, 2.7809999999999997, 2.7809999999999997, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    oprho = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0] #modified later
    opro  = [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 0, 0, 0, 0, 0, 0, 0] #modified later
    oprjo = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 0, 0, 0, 0, 0, 0, 0] #modified later

    #conversion
    numcon=cont
    numopro = numvar - 1
    for j in range(NbPipes,numvar-1):
        # f(x_j+h)^g
        opro[j]  = 3 # MSK_OPR_POW
        oprjo[j] = j+1 # variable index (col)
        oprfo[j] = TapsConst2[j - NbPipes] # coeff
        oprgo[j] = 3.0 # exponent
        oprho[j] = 0.0

    numoprc  = 0;
    for j in range(0,NbPipes + 1):
        c[j] = 0

    for j in range(NbPipes + 1, numvar):
        c[j] = TapsConst1[j - NbPipes - 1]

    for j in range(0,numcon):
        bkc[j] = 2 # MSK_BK_FX
        blc[j] = 0
        buc[j] = 0


    for j in range(0,numvar):
        bkx[j] = 4 #MSK_BK_RA

    b = [buc[i] for i in range(0,len(bkc)) if bkc[i]==2] # MSK_BK_FX
    b_i = [i for i in range(0,len(bkc)) if bkc[i]==2] # MSK_BK_FX
    A_val = []
    A_col = []
    A_row = []
    for col in range(0,numvar):
        for ptr in range(ptrb[col],ptre[col]):
            row = sub[ptr]
            nz  = val[ptr]
            if bkc[row] == 2: # MSK_BK_FX
                A_row.append(row)
                A_col.append(col)
                A_val.append(nz)
    cvx_A = spmatrix(A_val, A_row, A_col,(cont,numvar),tc='d')[b_i,:]
    cvx_b = matrix(b,tc='d')

    #Define a function for cvx_opt
    # Returns
    # F() : starting point
    # F(x) : value of F and dF
    # F(x,z) : value of F and dF and hessien

    def F(x=None, z=None):
        if x is None: return 0, matrix(1.,(numvar,1))
        #print(x.T)
        if min(x) < 0.0: return None # F domain
        f = sum([c[j]*x[j] for j in range(0,numvar)] + [oprfo[j]*x[j+1]**oprgo[j] for j in range(0,numvar-1)])
        Df1 = matrix(c).T
        Df2 = matrix([0] + [oprgo[j]*oprfo[j]*x[j+1]**(oprgo[j]-1) for j in range(0,numvar-1)]).T
        Df = Df1 + Df2
        if z is None: return f, Df
        #print([0] + [(oprgo[j]-1)*oprgo[j]*oprfo[j]*x[j+1]**(oprgo[j]-2) for j in range(0,numvar-1)])
        H = spdiag([0] + [(oprgo[j]-1)*oprgo[j]*oprfo[j]*x[j+1]**(oprgo[j]-2) for j in range(0,numvar-1)])
        #print(H)
        return f, Df, H

    sol = solvers.cp(F, A=cvx_A, b=cvx_b)

    flows = [0.9748586431385673, 0.9748586431385673, 0.9748586431385673, 0.5386406143048615, 0.43621802883370586, 0.37669788557581124, 0.1886468466046585, 0.16194272872905033, 0.12556596185860375, 0.12556596185860375, 0.12556596185860375, 0.09432342330232925, 0.09432342330232925, 0.24757118222904734, 0.16194272872905033, 0.12556596185860375, 0.12556596185860375, 0.12556596185860375, 0.09432342330232925, 0.09432342330232925, 0.24757118222904734, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    flows = matrix(flows)[range(0,numvar)]
    #diff = matrix(flows) - matrix(sol['x'])

    y = [0.0, 0.4147494536942568, 3.7283927966062573, 7.842601791791739, 17.154712030642827, 8.190783936278457, 17.542613256354226, 8.236696667202539, 8.21165947036742, 8.21165947036742, 8.21165947036742, 17.555154598066633, 17.555154598066633, 17.924053855319045]
    print(matrix(y) + sol['y'])

    #returns
    #X = sol['x']
    #Y = -sol['y']
    #print(X)

    #return solvers.cp(F, A=A, b=b)['x']

    #http://abel.ee.ucla.edu/cvxopt/userguide/coneprog.html?highlight=lp#cvxopt.solvers.lp
    #c = matrix([-4., -5.])
    #G = matrix([[2., 1., -1., 0.], [1., 2., 0., -1.]])
    #h = matrix([3., 3., 0., 0.])
    #sol = solvers.lp(c, G, h,solver='glpk')
    #print sol['x']