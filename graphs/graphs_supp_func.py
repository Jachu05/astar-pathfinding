from scipy.sparse import csr_matrix
import numpy as np
from scipy.sparse.csgraph import shortest_path


def create_clean_dist_map(n, m=None):
    """

    :param n: n rows
    :param m: m columns
    :return:
    """
    if m is None:
        m = n
    nodes = n * m
    auto_graph = np.zeros((nodes, nodes))

    for node_idx in range(nodes):
        # next node
        if node_idx % m != m - 1:
            auto_graph[node_idx][node_idx + 1] = 1
        # previous node
        if node_idx % m != 0:
            auto_graph[node_idx][node_idx - 1] = 1
        # upper node
        if node_idx >= m:
            auto_graph[node_idx][node_idx - m] = 1
        # lower node
        if node_idx + m < nodes:
            auto_graph[node_idx][node_idx + m] = 1
    return auto_graph


def mark_node_as_barrier(node_i, csr_graph):
    csr_graph[:, node_i] = 0
    csr_graph[node_i, :] = 0


def eg_with_two_separate_paths(csr_graph, first_group, second_group, common_dists, common_predecessors):
    """
    example of for one pathfinding but split by two 'threads' that might be calculate separately
    for grid 4x4 with node marked as:
    0 - 1 - 2 - 3
    |   |   |   |
    4 - 5 - 6 - 7

    path from node 0 to 3 will be calculated but node 2 will be marked as obstacle

    we take as first group:
    [0, 1, 2, 4, 5, 6]
    and second:
    [2, 3, 6, 7]
    :return:
    """

    def merge_partial_graph_to_expected(nodes_arr, group_predecessors, predecessors, group_dist, dists):
        # TODO handle this indexes replacement
        a = np.argwhere(group_predecessors != -9999)
        group_predecessors = np.choose(group_predecessors, nodes_arr, mode='wrap')
        di = np.diag_indices(group_predecessors.shape[0])
        group_predecessors[di] = -9999
        predecessors[nodes_arr.reshape((-1, 1)), nodes_arr] = group_predecessors
        dists[nodes_arr.reshape((-1, 1)), nodes_arr] = group_dist

    def merge_uncommon_groups_to_expected(a_uncommon_nodes, b_uncommon_nodes, expected, common, dists):
        uncommon_idx = a = np.array((np.repeat(a_uncommon_nodes, b_uncommon_nodes.shape[0]),
                                     np.tile(b_uncommon_nodes, a_uncommon_nodes.shape[0]))).T  # uncommon paths
        uncommon_dist = dists[uncommon_idx[:, 0]][:, common] + dists[uncommon_idx[:, 1]][:, common]  # per common node
        min_dist, arg_min_dist = np.min(uncommon_dist, axis=1), np.argmin(uncommon_dist, axis=1)
        chosen_common_nodes = np.choose(arg_min_dist, common)
        # move from 0 idx to 1 idx
        expected[uncommon_idx[:, 1], uncommon_idx[:, 0]] = expected[chosen_common_nodes, uncommon_idx[:, 0]]
        dists[uncommon_idx[:, 1], uncommon_idx[:, 0]] = min_dist
        # move from 1 idx to 0 idx
        expected[uncommon_idx[:, 0], uncommon_idx[:, 1]] = expected[chosen_common_nodes, uncommon_idx[:, 1]]
        dists[uncommon_idx[:, 0], uncommon_idx[:, 1]] = min_dist

    common_group = np.intersect1d(first_group, second_group)
    first_uncommon_nodes = np.setdiff1d(first_group, common_group)
    second_uncommon_nodes = np.setdiff1d(second_group, common_group)

    first_graph_group = csr_graph[first_group, :][:, first_group]
    second_graph_group = csr_graph[second_group, :][:, second_group]

    first_dist, first_predecessors = shortest_path(csgraph=first_graph_group, method='D',
                                                   directed=False, return_predecessors=True)
    second_dist, second_predecessors = shortest_path(csgraph=second_graph_group, method='D',
                                                     directed=False, return_predecessors=True)

    merge_partial_graph_to_expected(first_group, first_predecessors, common_predecessors, first_dist, common_dists)
    merge_partial_graph_to_expected(second_group, second_predecessors, common_predecessors, second_dist, common_dists)

    merge_uncommon_groups_to_expected(first_uncommon_nodes, second_uncommon_nodes,
                                      common_predecessors, common_group, common_dists)

    return common_dists, common_predecessors


if __name__ == "__main__":
    n = 7
    m = 7
    graph = create_clean_dist_map(n, m)
    mark_node_as_barrier(17, graph)
    graph = csr_matrix(graph)

    a_group = np.array((9, 10, 16, 17))
    b_group = np.array((16, 17, 23, 24))

    ab_dists = np.full((n * m, n * m), -5000, dtype=float)
    ab_predecessors = np.full((n * m, n * m), -5000, dtype=float)

    eg_with_two_separate_paths(graph, a_group, b_group, ab_dists, ab_predecessors)

    all_dist, all_predecessors = shortest_path(csgraph=graph, method='D',
                                               directed=True, return_predecessors=True)

    print('Merged dist calc equal:', np.all(np.equal(ab_dists, all_dist)))
    print('Merged predecessors calc equal:', np.all(np.equal(ab_predecessors, all_predecessors)))
