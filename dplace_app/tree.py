# coding: utf8
"""
We provide a customized alternative to ete2.Tree.prune to increase the speed of tree
pruning for the special case of
- nodes being specified by node name
- branch lengths always 1 for Glottolog trees
"""
from __future__ import unicode_literals


def prune(tree, nodes, const_depth=True, keep_root=False):
    to_keep = set(n for n in tree.traverse() if n.name in nodes)
    n2count, n2depth, visitors2nodes = {}, {}, {}

    start, node2path = tree.get_common_ancestor(to_keep, get_path=True)
    if keep_root:
        to_keep.add(tree)

    for seed, path in node2path.iteritems():
        for visited_node in path:
            if visited_node not in n2depth:
                if const_depth:
                    n2depth[visited_node] = 1
                else:
                    depth = visited_node.get_distance(start, topology_only=True)
                    n2depth[visited_node] = depth
            if visited_node is not seed:
                n2count.setdefault(visited_node, set()).add(seed)

    for node, visitors in n2count.iteritems():
        if len(visitors) > 1:
            visitor_key = frozenset(visitors)
            visitors2nodes.setdefault(visitor_key, set()).add(node)

    for visitors, nodes in visitors2nodes.iteritems():
        if not (to_keep & nodes):
            # to choose the closest ancestor for a node we want to keep:
            to_keep.add(sorted(nodes, key=lambda n: -n2depth[n])[0])

    for n in [n for n in tree.iter_descendants(strategy='postorder', is_leaf_fn=None)]:
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
