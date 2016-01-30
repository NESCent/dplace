import re
import logging
import os
from collections import defaultdict

from django.core.files import File
from nexus import NexusReader
from dplace_app.models import LanguageTree, Language


def load_tree(tree_dir, verbose=False):
    l_by_iso, l_by_glotto, l_by_name = \
        defaultdict(list), defaultdict(list), defaultdict(list)

    for lang in Language.objects.all().select_related('iso_code', 'glotto_code'):
        if lang.iso_code:
            l_by_iso[lang.iso_code.iso_code].append(lang)
        l_by_glotto[lang.glotto_code.glotto_code].append(lang)
        l_by_name[lang.name].append(lang)

    def get_language(taxon_name):
        if taxon_name in l_by_iso:
            return l_by_iso[taxon_name]
        if taxon_name in l_by_glotto:
            return l_by_glotto[taxon_name]
        if taxon_name in l_by_name:
            return l_by_name[taxon_name]

    for fname in os.listdir(tree_dir):
        if fname.endswith('.trees'):
            _load_tree(os.path.join(tree_dir, fname), get_language)


def _load_tree(file_name, get_language, verbose=False):
    # make a tree if not exists. Use the name of the tree
    tree_name = os.path.basename(file_name)
    with open(file_name, 'r') as f:
        tree, created = LanguageTree.objects.get_or_create(name=tree_name)
        if created:
            tree.file = File(f)
            tree.save()
    # now add languages to the tree
    reader = NexusReader(file_name)
    #Remove '[&R]' from newick string
    newick = re.sub(r'\[.*?\]', '', reader.trees.trees[0])
    try:
        newick = newick[newick.index('=')+1:]
    except ValueError:
        newick = newick
        
    if verbose:
        logging.info("Formatting newick string %s" % (newick))

    tree.newick_string = str(newick)
    for taxon_name in reader.trees.taxa:
        if taxon_name is '1':
            continue
        languages = get_language(taxon_name)
        if not languages:
            logging.warn("load_tree: Error with taxon - `%s` %s" % (taxon_name, file_name))
            continue

        for l in languages:
            tree.languages.add(l)
    tree.save()
