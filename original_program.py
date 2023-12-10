# Copyright 2020 D-Wave Systems Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Import networkx for graph tools
import networkx as nx

# Import dwave_networkx for d-wave graph tools/functions
import dwave_networkx as dnx

# Import dwave.system packages for the QPU
from dwave.system import DWaveSampler, EmbeddingComposite

from bokeh.io import output_file, show
from bokeh.models import (Circle, HoverTool,MultiLine, Plot, EdgesAndLinkedNodes, NodesAndLinkedEdges)
from bokeh.palettes import Spectral4
from bokeh.plotting import from_networkx
from bokeh.models import ColumnDataSource

# Define your data
data = {
    'x': [1, 2, 3, 4, 5],
    'y': [1, 2, 3, 4, 5],
    'color': ['red', 'blue', 'green', 'orange', 'purple']
}

# Create a ColumnDataSource from the data
source = ColumnDataSource(data)

# Set the solver we're going to use
def set_sampler():
    '''Returns a dimod sampler'''

    sampler = EmbeddingComposite(DWaveSampler())

    return sampler

def create_graph():
    # Create empty graph
    G = nx.Graph()

    # Add edges to graph - this also adds the nodes
    G.add_edges_from([(1, 2), (1, 3), (2, 3), (3, 4), (3, 5), 
                        (4, 5), (4, 6), (5, 6), (6, 7)])

    return G

def solve_problem(G, sampler):
    '''Returns a solution to to the minimum vertex cover on graph G using 
    the D-Wave QPU.

    Args:
        G(networkx.Graph): a graph representing a problem
        sampler(dimod.Sampler): sampler used to find solutions

    Returns:
        A list of nodes
    '''

    # Find the maximum independent set, S
    S = dnx.maximum_independent_set(G, sampler=sampler, num_reads=10)

    return S

## ------- Main program -------
if __name__ == "__main__":

    G = create_graph()

    sampler = set_sampler()

    S = solve_problem(G, sampler)

    # Print the solution for the user
    print('Maximum independent set size found is', len(S))
    print(S)

# Visualize the results
subset_1 = G.subgraph(S)
notS = list(set(G.nodes()) - set(S))
subset_0 = G.subgraph(notS)

# Add a color attribute to the nodes in the graph
for node in G.nodes():
    G.nodes[node]['color'] = 'red' if node in S else 'blue'

# Create a Bokeh plot with the spring layout
plot = Plot(width=400, height=400,
            x_range=Range1d(-1.1, 1.1), y_range=Range1d(-1.1, 1.1))
plot.title.text = "Graph Interaction Demonstration"

# Create a graph renderer from the networkx graph
graph_renderer = from_networkx(G, nx.spring_layout, scale=1, center=(0, 0))

# Get the node indices
node_indices = list(G.nodes)

# Add the node indices to the graph renderer's node data
graph_renderer.node_renderer.data_source.add(node_indices, 'index')

# Create a hover tool that only applies to the graph renderer
hover_tool = HoverTool(tooltips=[("index", "@index")], renderers=[graph_renderer.node_renderer])

# Add the hover tool to the plot
plot.add_tools(hover_tool)

graph_renderer = from_networkx(G, nx.spring_layout, scale=1, center=(0, 0))

# Provide node colors based on the solution
graph_renderer.node_renderer.glyph = Circle(size=15, fill_color='color')

graph_renderer.node_renderer.selection_glyph = Circle(size=15, fill_color=Spectral4[2])
graph_renderer.node_renderer.hover_glyph = Circle(size=15, fill_color=Spectral4[1])

graph_renderer.edge_renderer.glyph = MultiLine(line_color="#CCCCCC", line_alpha=0.8, line_width=1)
graph_renderer.edge_renderer.selection_glyph = MultiLine(line_color=Spectral4[2], line_width=2)
graph_renderer.edge_renderer.hover_glyph = MultiLine(line_color=Spectral4[1], line_width=2)

graph_renderer.selection_policy = NodesAndLinkedEdges()
graph_renderer.inspection_policy = EdgesAndLinkedNodes()

plot.renderers.append(graph_renderer)

output_file("interactive_graphs.html")
# show(plot)