from scipy.sparse import csr_matrix
import numpy as np
from scipy.sparse.csgraph import shortest_path


def create_clean_dist_map(n):
    nodes = n ** 2
    auto_graph = np.zeros((nodes, nodes))

    for node_idx in range(nodes):
        # next node
        if node_idx + 1 < nodes and (node_idx + 1) % n:
            auto_graph[node_idx][node_idx + 1] = 1
        # previous node
        if node_idx - 1 >= 0 and node_idx % n:
            auto_graph[node_idx][node_idx - 1] = 1
        # upper node
        if node_idx - n >= 0:
            auto_graph[node_idx][node_idx - n] = 1
        # lower node
        if node_idx + n < nodes:
            auto_graph[node_idx][node_idx + n] = 1
    return auto_graph


def mark_node_as_barrier(node_i, graph):
    graph[:, node_i] = 0
    graph[node_i, :] = 0


if __name__ == "__main__":
    graph = create_clean_dist_map(3)
    # removing 5th node from connection
    # mark_node_as_barrier(5, graph)

    print(graph, '\n')

    graph = csr_matrix(graph)

    dist_matrix, predecessors = shortest_path(csgraph=graph, directed=False, return_predecessors=True)

    print(dist_matrix)
    print(predecessors)
