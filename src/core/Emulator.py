from mininet.topo import Topo as mininet_topo
from mininet.node import Node as mininet_node
from mininet.net import Mininet as mininet_Mininet
from mininet.cli import CLI as mininet_CLI
from mininet.link import TCLink as mininet_TCLink
import mininet.log
from namedlist import namedlist
from .VirtualTopo import DijTree
import graphviz
import os


class LinuxRouter(mininet_node):
    """A Node with IP forwarding enabled.
    Means that every packet that is in this node, comunicate freely with its interfaces."""

    def config(self, **params):
        super(LinuxRouter, self).config(**params)
        self.cmd('sysctl net.ipv4.ip_forward=1')

    def terminate(self):
        self.cmd('sysctl net.ipv4.ip_forward=0')
        super(LinuxRouter, self).terminate()


class Command(namedlist("Command", ["node", "cmd"])):
    pass


class Node():
    def __init__(self, name):
        self.name = name
        self.edges = []
    
    # Override += operator
    def __iadd__(self, obj):
        self.edges.append(obj)

    def __str__(self):
        return self.name

    def __repr__(self):
        return str(self)


class Edge(namedlist("Edge", ["ip", "dest", "delay"])):
    """ Easy way to define a data structure"""
    pass


class Topo(mininet_topo):
    def __init__(self, virtual_topo, *args, **kwargs):
        # Desired topology to build in mininet
        self.virtual_topo = virtual_topo
        # List to store nodes
        self.nodes_list = []
        self.cmds_dijs = []
        super(Topo, self).__init__(*args, **kwargs)

    def __add_node(self, name):
        # Add to mininet
        self.addNode(name, cls=LinuxRouter, ip=None)
        # Add to our extra nodes_list
        self.nodes_list.append(Node(name))

    def __add_edge(self, l, r, i, delay):
        edge1 = Edge(
            ip=f"10.0.{i}.1",
            dest=r,
            delay=delay
        )
        edge2 = Edge(
            ip=f"10.0.{i}.2",
            dest=l,
            delay=delay
        )

        # Add the link in mininet
        self.addLink(
            l.name,
            r.name,
            params1={"ip": f"{edge1.ip}/24"},
            params2={"ip": f"{edge2.ip}/24"},
            delay=f"{delay}ms"
        )
        
        # Add edge to node's edge list
        l += edge1
        r += edge2

    # Build the topology desired in mininet
    def build(self, **kwargs):

        for node in self.virtual_topo.nodes:
            self.__add_node(node.name.replace("v", "s"))

        for i, (li, ri) in enumerate(self.virtual_topo.pairs):
            l = self.nodes_list[li]
            r = self.nodes_list[ri]
            weight = self.virtual_topo.nodes[li][self.virtual_topo.nodes[ri]].weight
            self.__add_edge(l, r, i, weight)
            
        # --------------------DIJKSTRA--------------------
        for i in range(len(self.virtual_topo.nodes)):
            node_name = self.nodes_list[i].name
            for ip1, ip2 in self.__routing_table(i):
                self.cmds_dijs.append(
                    Command(node_name, f"ip route add {ip1} via {ip2}"))

    def __routing_table(self, src_index):
        def get_ip_between(i1, i2):
            n1, n2 = (self.nodes_list[i] for i in (i1, i2))
            return next((edge.ip for edge in n2.edges if edge.dest == n1))
        
        node = self.nodes_list[src_index]
        node_ip = node.edges[0].ip
        neighbors = {self.nodes_list.index(
            edge.dest): set() for edge in node.edges}
        
        # Executes dijstra algorithm starting from src_index
        dij = DijTree(self.virtual_topo, src_index)
        dij.savefig(f"dij_n{src_index+1}_{self.virtual_topo.torus_type}")
        pairs = {l: r for l, _, r in dij.pairs}
        for i in range(len(self.virtual_topo.nodes)):
            aux_act = i
            aux_next = None
            s = set()
            while True:
                aux_next = pairs.get(aux_act)
                if aux_next == None:
                    break
                # s.add(get_ip_between(aux_next,aux_act))
                s.add(self.nodes_list[aux_act])
                if aux_next == src_index:
                    neighbors[aux_act] |= s
                    break
                aux_act = aux_next
        for neight, s in neighbors.items():
            neight_ip = get_ip_between(src_index, neight)
            for dest_node in s:
                for edge in dest_node.edges:
                    alias = edge.ip
                    yield alias, neight_ip


class Emulator():
    def __init__(self, virtual_topo):
        self.torus_type = virtual_topo.torus_type
        max_nodes = 23
        if len(virtual_topo.nodes) > max_nodes:
            raise RuntimeError(
                f"Network cant have more than {max_nodes} nodes")
        
        # create all mininet stuff and configure route tables
        mininet.log.setLogLevel('info')
        topo = Topo(virtual_topo)
        self.net = mininet_Mininet(topo=topo, link=mininet_TCLink)
        self.net.start()
        self.graphviz = self.__to_graphviz(self.net.topo)
        def exec_cmd(cmd): return mininet.log.info(
            self.net[cmd.node].cmd(cmd.cmd))

        print("-"*16, "DIJKISTRA TREE COMMANDS", "-"*16)
        for cmd in self.net.topo.cmds_dijs:
            print(cmd.node, cmd.cmd)
            exec_cmd(cmd)
        print("-"*32)
        print("-"*16, "NODE IPS", "-"*16)

        for node in self.net.topo.nodes_list:
            print(f"{node.name}={[edge.ip for edge in node.edges]}")

    def __to_graphviz(self, topo):
        ans = graphviz.Graph()
        ans.attr('node', color='transparent', image='switch.png')
        edges = set()
        for node in topo.nodes_list:
            for edge in node.edges:
                pair = frozenset((node, edge.dest))
                if pair in edges:
                    continue
                edges.add(pair)
                ip_splitted = edge.ip.split(".")
                ans.edge(
                    node.name,
                    edge.dest.name,
                    taillabel=f"{ip_splitted[0]}.{ip_splitted[1]}.{ip_splitted[2]}.{ip_splitted[3]}",
                    label=f"{edge.delay}ms",
                    headlabel=f"{ip_splitted[0]}.{ip_splitted[1]}.{ip_splitted[2]}.{1 if ip_splitted[3]=='2' else 2}",
                    color='tomato'
                )
        return ans

    def savefig(self, fname="map"):
        """saves graph's pdf
        Args:
                fname(str): pdf file's name to save, default "map"
        """
        self.graphviz.format = "pdf"
        fname += f"_{self.torus_type}"
        self.graphviz.render(fname)
        os.unlink(fname)

    def pingAll(self, timeout=10):
        self.net.pingAll(timeout)

    def start(self):
        mininet_CLI(self.net)

    def __del__(self):
        self.net.stop()


if __name__ == "__main__":
    from VirtualTopo import VirtualTopo
    virtual_topo = VirtualTopo(9, torus_type="2D")
    virtual_topo.savefig()
    emu = Emulator(virtual_topo)
    emu.savefig("map")
    emu.net.pingAll()
    emu.start()
