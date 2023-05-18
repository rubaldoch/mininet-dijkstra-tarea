import random
from namedlist import namedlist
from collections import deque
from math import ceil
import graphviz
import os

random.seed(7)

class Connection(namedlist("Connection", ["node", "weight"])):
    def __hash__(self):
        return hash((self.node, self.weight))


class Node:
    def __init__(self, name):
        self.name = name
        self.children = {}

    def traverse(self):
        unvisited = deque([self])
        ans = set()
        while unvisited:
            u = unvisited.pop()
            ans.add(u)
            for children in u:
                if children.node not in ans:
                    unvisited.append(children.node)
        return ans

    def __iadd__(self, node):
        assert isinstance(node, Node)

        self.children[node] = Connection(node=node, weight=-1)
        return self

    def __getitem__(self, node):
        return self.children[node]

    def __iter__(self):
        return iter(self.children.values())

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"Node({self.name})"

    def __hash__(self):
        return hash(str(self))

    def has_children(self):
        return bool(self.children)


class DijDist(namedlist("DijDist", [("known", False), ("cost", float("inf")), ("path", -1)])):
    pass


class DijTree:
    """Dijkstra tree
Args:
            virtual_topo (VirtualTop): graph to use
            src_index (int): starting node index
Attributes:
    graph (graphviz.Graph): Graphviz graph
    pairs (list): list containing tuples of (src_index,weight,dest_index)
    """

    def __init__(self, virtual_topo, src_index):
        nodes = virtual_topo.nodes
        n = len(nodes)
        dist = [DijDist() for _ in range(n)]
        dist[src_index].cost = 0
        for _ in range(n):
            u = DijTree.min_dist(dist)
            du = dist[u]
            nu = nodes[u]
            du.known = True
            for conn in nu:
                i = nodes.index(conn.node)
                di = dist[i]
                if di.cost > du.cost+conn.weight:
                    di.cost = du.cost+conn.weight
                    di.path = u
        # --------------------end dijsktra--------------------
        self.graph = graphviz.Graph()
        self.graph.attr('node', shape='tripleoctagon',
                        color='lightblue2', style='filled')
        self.pairs = []
        for i, d in enumerate(dist):
            if d.path == -1:
                continue
            u = nodes[i]
            v = nodes[d.path]
            weight = u[v].weight
            self.pairs.append((i, weight, d.path))
            self.graph.edge(u.name, v.name, label=str(weight))

    def min_dist(dist):
        m = float("inf")
        for i, e in enumerate(dist):
            if e.known:
                continue
            if e.cost < m:
                ans = i
                m = e.cost
        return ans

    def view(self, name="dij"):
        self.graph.view(name, cleanup=True, quiet_view=True)

    def savefig(self, fname="dij"):
        """saves graph's pdf
        Args:
                fname(str): pdf file's name to save, default "dij"
        """
        self.graph.format = "pdf"
        self.graph.render(fname)
        os.unlink(fname)


class VirtualTopo:
    """Create torus 1d or 2D undirected graph  with n nodes
    Args:
            n (int): Number of nodes
            nodes_prefix (str,optional): prefix of the name of each node, default='v' 
            torus_type (str,optional): type of torus, could be '1D' or '2D', default:1D.
            min_weight (int,optional) minimal value of the weight
            max_weight (int,optional) maximum value of the weight
    Attributes:
            nodes (list): list containing all the nodes
            pairs (set): set containing frozenset of pairs of node indexes
            graphviz (graphviz.Graph): Graphviz graph
    """

    def __init__(self, n, nodes_prefix="v", torus_type="1D", min_weight=1, max_weight=20):
        self.nodes = [Node(f"{nodes_prefix}{i+1}") for i in range(n)]
        self.pairs = set()
        self.torus_type = torus_type

        if self.torus_type == "1D":
            self.__build_torus_1D(n)
        elif (self.torus_type == "2D"):
            self.__build_torus_2D(n)
        
        # Add pairs to node's children lists
        for i, j in self.pairs:
            u, v = self.nodes[i], self.nodes[j]
            u += v # overator overloaded
            v += u

        # set random weights
        for node in self.nodes:
            for conn in node:
                if conn.weight == -1:
                    a = random.randint(min_weight, max_weight)
                    conn.weight = a
                    conn.node[node].weight = a
        
        self.graphviz = self.__to_graphviz()

    def __build_torus_1D(self, n):
        """Create torus 1D undirected graph  with n nodes
        Args:
            n (int): Number of nodes
        """
        # Complete your code here
        # TODO
        #self.pairs.add(frozenset((i, j)))

    def __build_torus_2D(self, n):
        """Create torus 2D undirected graph  with n nodes
        Args:
            n (int): Number of nodes
        """
        n_root = int(n**0.5)
        # Complete your code here
        # TODO

    def view(self, name="virtual_topo"):
        """opens default pdf binary to show the graph, and saves as pdf
        Args:
                name(str): pdf file's name to save, default "virtual_topo"
        """
        self.graphviz.view(name, cleanup=True, quiet_view=True)

    def savefig(self, fname="virtual_topo"):
        """saves graph's pdf
        Args:
                fname(str): pdf file's name to save, default "virtual_topo"
        """
        fname += f"_{self.torus_type}"
        self.graphviz.format = "pdf"
        self.graphviz.render(fname)
        os.unlink(fname)

    def __to_graphviz(self, *args, **kwargs):
        graph = graphviz.Graph(*args, **kwargs)
        graph.attr('node', shape='tripleoctagon',
                   color='lightblue2', style='filled')
        for i, j in self.pairs:
            u, v = self.nodes[i], self.nodes[j]
            assert u[v].weight == v[u].weight
            graph.edge(u.name, v.name, label=str(u[v].weight))
        return graph


if __name__ == "__main__":
    import pickle
    topo = VirtualTopo(5, volume=.5)
    topo.savefig("virtual_topo")
    DijTree(topo, 0).savefig("dij_n1")
    DijTree(topo, 1).savefig("dij_n2")
    DijTree(topo, 2).savefig("dij_n3")
    DijTree(topo, 3).savefig("dij_n4")
    DijTree(topo, 4).savefig("dij_n5")
