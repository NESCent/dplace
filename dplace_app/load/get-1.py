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
IS_GLOTTOCODE = re.compile(r"""'.* <(\w{4}\d{4})>.*'$""")

def clean_tree(tree):
    """Previously, removed taxa with no ISO-639 codes.
    Now renames taxa to Glottocodes."""
    to_keep = []

    if len(tree.get_leaves()) < 3: #skip trees with less than three leaves
        print tree.get_leaves()
        return None
        
    for node in tree.traverse():
        #iso = IS_ISOCODE.findall(leaf.name)
        glotto = IS_GLOTTOCODE.findall(node.name)
        if len(glotto) == 1:
            node.name = glotto[0]  # rename to glotto code
            #print node.name
            to_keep.append(node.name)

    try:
        tree.prune(to_keep)
        return tree  
    except:
        print "Exception pruning tree, returning un-pruned tree!"
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
            tree = Tree(newick, format=3)
            tree = clean_tree(tree)
            
            if tree is not None:
                newick_string = str(tree.write(format=3))
                with codecs.open(filename, 'w', encoding="utf-8") as handle:
                    handle.write("#NEXUS\nBegin taxa;\n") #write taxa to file
                    for leaf in tree.traverse():
                        if str(leaf.name)  in newick_string:
                            handle.write(leaf.name)
                            handle.write("\n")
                    handle.write(";\nend;")
                    handle.write("\nBegin trees;\ntree UNTITLED = ") #write newick string to file
                    handle.write(newick_string)
                    handle.write("\nend;")
        else:
            print("%30s <- %s" % (family, '[ok]'))
