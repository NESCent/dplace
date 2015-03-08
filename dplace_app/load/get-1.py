#!/usr/bin/env python
#coding=utf-8
"""Download all Glottolog Newick Files"""

import os
import re
import codecs

try:
    import requests
except ImportError:
    raise ImportError("please install the requests library")

try:
    from bs4 import BeautifulSoup as bs
except ImportError:
    raise ImportError("please install the beautifulsoup4 library")

try:
    from ete2 import Tree
except ImportError:
    raise ImportError("please install the ete2 library")

IS_ISOCODE = re.compile(r"""'.* <\w{4}\d{4}><(\w{3})>'$""")


def clean_tree(tree):
    """Removes taxa with no ISO-639 codes"""
    to_keep = []
    for leaf in tree.iter_leaves():
        iso = IS_ISOCODE.findall(leaf.name)
        if len(iso) == 1:
            leaf.name = iso[0]  # rename to ISO code
            to_keep.append(leaf.name)
    
    if len(to_keep) <= 3:  # not worth keeping.
        return None
    tree.prune(to_keep)
    return tree

GLOTTOLOG_FAMILIES = "http://glottolog.org/glottolog/language.atom?type=families&sSearch_1=Top-level+unit"

if __name__ == '__main__':
    urls = {}
    
    for entry in bs(requests.get(GLOTTOLOG_FAMILIES).text).find_all('entry'):
        urls[entry.find('title').text] = entry.find('id').text
    
    for family in sorted(urls):
        url = urls[family]
        filename = "%s.glotto.trees" % family
        if not os.path.isfile(filename):
            print("%30s <- %s" % (family, url))
            newick = requests.get(url + '.newick.txt').text.encode('utf-8')
            newick = newick.replace("[", "<").replace("]", ">")  # hack to keep ISO code in leaf name
            tree = Tree(newick)
            tree = clean_tree(tree)
            if tree is not None:
                with codecs.open(filename, 'w', encoding="utf-8") as handle:
                    handle.write("#NEXUS\nBegin taxa;\n") #write taxa to file
                    for leaf in tree.iter_leaves():
                        handle.write(leaf.name)
                        handle.write("\n")
                    handle.write(";\nend;")
                    handle.write("\nBegin trees;\ntree UNTITLED = ") #write newick string to file
                    handle.write(tree.write())
                    handle.write("\nend;")
        else:
            print("%30s <- %s" % (family, '[ok]'))
