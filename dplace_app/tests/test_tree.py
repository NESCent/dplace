# coding: utf8
from __future__ import unicode_literals

from ete3 import Tree
from django.test import TestCase

from dplace_app.tree import prune


class Tests(TestCase):
    def _compare(self, newick, nodes):
        nodes = [str(node) for node in nodes]
        t1 = Tree(newick, format=1)
        t1.prune(nodes, preserve_branch_length=True)
        t2 = Tree(newick, format=1)
        prune(t2, nodes, const_depth=False, keep_root=True)
        self.assertEqual(t1.write(format=1), t2.write(format=1))

    def test_prune(self):
        #                /-A
        #          /D /C|
        #       /F|      \-B
        #      |  |
        #    /H|   \-E
        #   |  |                        /-A
        # -root  \-G                 -root
        #   |                           \-B
        #   |   /-I
        #    \K|
        #       \-J
        self._compare('(((((A,B)C)D,E)F,G)H,(I,J)K)root;', ['A', 'B'])

        #                /-A
        #          /D /C|
        #       /F|      \-B
        #      |  |
        #    /H|   \-E
        #   |  |                              /-A
        # -root  \-G                  -root- C|
        #   |                                 \-B
        #   |   /-I
        #    \K|
        #       \-J
        self._compare('(((((A,B)C)D,E)F,G)H,(I,J)K)root;', ['A', 'B', 'C'])

        #             /-A
        #          /C|
        #       /F|   \-B
        #      |  |
        #    /H|   \-E                    /-I
        #   |  |                      -root
        # -root  \-G                      |   /-A
        #   |                             \C|
        #   |   /-I                          \-B
        #    \K|
        #       \-J
        self._compare('((((A,B)C,E)F,G)H,(I,J)K)root;', ['A', 'B', 'I'])

        #             /-A
        #          /D|
        #       /F|   \-B
        #      |  |
        #    /H|   \-E
        #   |  |                              /-A
        # -root  \-G                -root-H /F|
        #   |                                 \-B
        #   |   /-I
        #    \K|
        #       \-J
        self._compare('((((A,B)D,E)F,G)H,(I,J)K)root;', ['A', 'B', 'F', 'H'])
