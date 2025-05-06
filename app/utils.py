from .schemas import Node, Edge
from itertools import chain
from collections import deque
import re


def validate_nodes(data):
    if type(data.nodes) is not list:  # type checking
        return False
    for node in data.nodes:
        if type(node) is not Node:  # type checking
            return False
        if not bool(re.fullmatch(r'^[A-Za-z]+$', node.name)) or len(node.name) > 255:  # validate format
            return False
    used = []
    for node in data.nodes:  # uniqueness checking
        if node in used:
            return False
        used.append(node)
    return True


def validate_edges(data):
    if type(data.edges) is not list:  # type checking
        return False
    for edge in data.edges:
        if type(edge) is not Edge:  # type checking
            return False
        if edge.target not in map(lambda x: x.name, data.nodes) or edge.source not in map(lambda x: x.name, data.nodes):
            return False
    return True


def adjacency_list_from_graph(data):
    adj_lst = {}
    for edge in data.edges:
        if edge.source not in adj_lst:
            adj_lst[edge.source] = [edge.target]
        else:
            adj_lst[edge.source].append(edge.target)
    for node in data.nodes:
        if node.name not in adj_lst:
            adj_lst[node.name] = []
    return adj_lst


def incoming_rate(adj_list):
    in_degree = {}
    for node in adj_list:
        in_degree[node] = 0
    for source in adj_list:
        for destination in adj_list[source]:
            in_degree[destination] += 1
    return in_degree


def reversed_adjacency_list_from_graph(data):
    adjacency_list = adjacency_list_from_graph(data)
    transposed_adjacency_list = {}
    for name in adjacency_list:
        for adjacency in adjacency_list[name]:
            if adjacency not in transposed_adjacency_list:
                transposed_adjacency_list[adjacency] = [name]
            else:
                transposed_adjacency_list[adjacency].append(name)
    for name in adjacency_list:
        if name not in transposed_adjacency_list:
            transposed_adjacency_list[name] = []
    return transposed_adjacency_list

def is_DAG(data):
    adj_lst = adjacency_list_from_graph(data)
    incoming_degree = incoming_rate(adj_lst)
    queue = deque()
    for name, degree in incoming_degree.items():
        if degree == 0:
            queue.append(name)
    visited_cnt = 0
    while queue:
        current = queue.popleft()
        visited_cnt += 1

        for vertex in adj_lst[current]:
            incoming_degree[vertex] -= 1
            if incoming_degree[vertex] == 0:
                queue.append(vertex)
    return visited_cnt == len(data.nodes)


def validate_graph(data):
    for node in data.nodes:
        if node.name not in chain.from_iterable(
                list(map(lambda x: [x.source, x.target], data.edges))):  # node accordance
            return False
    for edge in data.edges:
        if (edge.source not in map(lambda x: x.name, data.nodes) or
                edge.target not in map(lambda x: x.name, data.nodes)):  # edge accordance
            return False
    return True
