# Dijkstra based routing in mininet

> **Credits**: based on [Dijkstra based routing in mininet](https://github.com/giuliano-oliveira/rc2t1) created by Giuliano Oliviera.

Creates torus 1D or 2D topology in mininet with random edge weights applied to links delay, and use dijikstra algorithm to create minimal cost routes to every node.

## Prerequisites

- python 3.7 (3.5 won't work, some source files have literal string interpolation)
- pip
- mininet

## Installing

### Mininet

We strongly recommend to install mininet via the prebuild VM image. Please follow the mininet official [instructions](http://mininet.org/download/) about that.

### Source code dependencies

```
sudo apt install python3-pip
sudo apt install graphviz
```

Install all dependecies described in `requirements.txt` using pip

```bash
sudo pip3 install -r requirements.txt
```

## Usage

cd to the src directory

```bash
cd src
```

and run `main.py` with root priveleges. For example to run a torus 1D with 2 nodes, execute:

```bash
sudo python main.py -n 2 -t 1D
```

> The first time it only joins two nodes. You must modify `__build_torus_1D()` and `__build_torus_2D()` to create the 1D and 2D torus for `n` nodes.

see `./main.py --help` for more options
after executing, you will have a mininet CLI, and the program will save in the same folder the following files

- `virtual_topo_1D.pdf` : the graph
- `map_1D.pdf`: the network topology
- `dij_ni_1D.pdf`: being i the node index, the minimal cost tree for each node
