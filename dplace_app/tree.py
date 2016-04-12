# coding: utf8
"""
We provide a customized alternative to ete2.Tree.prune to increase the speed of tree
pruning for the special case of
- nodes being specified by node name
- branch lengths always 1 for Glottolog trees
"""
from __future__ import unicode_literals
from collections import defaultdict


def prune(tree, nodes, const_depth=True, keep_root=False):
    to_keep = set(n for n in tree.traverse() if n.name in nodes)
    n2depth, n2count, visitors2nodes = {}, defaultdict(set), defaultdict(set)

    start, node2path = tree.get_common_ancestor(to_keep, get_path=True)
    if keep_root:
        to_keep.add(tree)

    for seed, path in node2path.items():
        for visited_node in path:
            if visited_node not in n2depth:
                n2depth[visited_node] = 1 if const_depth \
                    else visited_node.get_distance(start, topology_only=True)
            if visited_node is not seed:
                n2count[visited_node].add(seed)

    for node, visitors in n2count.items():
        if len(visitors) > 1:
            visitors2nodes[frozenset(visitors)].add(node)

    for visitors, nodes_ in visitors2nodes.items():
        if not (to_keep & nodes_):
            # to choose the closest ancestor for a node we want to keep:
            to_keep.add(sorted(nodes_, key=lambda n: -n2depth[n])[0])

    for n in tree.get_descendants('postorder'):
        if n not in to_keep:
            if len(n.children) == 1:
                n.children[0].dist += n.dist
            elif len(n.children) > 1 and n.up:
                n.up.dist += n.dist
            parent = n.up
            if parent:
                for ch in n.children:
                    parent.add_child(ch)
                parent.remove_child(n)
