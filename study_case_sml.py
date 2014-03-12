"""
This script runs neatwork to perform a design and a simulation
on a small sample water network
"""

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


#for n in topo.node:
#    print(topo.node[n]['load_factor']*0.0002)

#print(topo.calcul_proba(topo.graph['targetflow']/1000,7,topo.graph['opentaps'], topo.graph['servicequal']))

#print(topo.calcul_proba(0.2/1000,7,0.4,0.6))