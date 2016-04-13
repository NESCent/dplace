import re
import logging
import os
from collections import defaultdict

from django.core.files import File
from nexus import NexusReader
from ete2 import Tree
from ete2.coretype.tree import TreeError
from dplace_app.models import Society, LanguageTree, Language, LanguageTreeLabels, LanguageTreeLabelsSequence
from dplace_app.tree import update_newick
from util import csv_dict_reader


def tree_names(name_dir):
    sequences = []
    for fname in os.listdir(name_dir):
        if fname.startswith('phylogeny'): #save all csv files as phylogeny_name_etc.csv 
            res = _tree_names(fname.split('_')[1], csv_dict_reader(os.path.join(name_dir,fname)), sequences)
    LanguageTreeLabelsSequence.objects.bulk_create(sequences)
    return len(sequences)
            

def _tree_names(tree_name, items, label_sequences):
    try:
        tree = LanguageTree.objects.get(name=tree_name+'.trees')
    except:
        return False
        
    try:
        newick = Tree(tree.newick_string, format=1)
    except TreeError:
        return False
        
    for item in items:
        name_on_tip = item['Name_on_tree_tip']
        xd_ids = [i.strip() for i in item['xd_id'].split(',')]
        society_ids = [i.strip() for i in item['soc_id'].split(',')]
        order = item['fixed_order']
        
        if not xd_ids: # pragma: no cover
            continue
        
        label, created = LanguageTreeLabels.objects.get_or_create(
            languageTree=tree,
            label=name_on_tip
        )
        
        tree.taxa.add(label)
        for society in Society.objects.all().filter(xd_id__in=xd_ids):
            try:
                f_order = len(society_ids) - society_ids.index(society.ext_id) - 1
            except:
                f_order = 0
            label_sequences.append(
                LanguageTreeLabelsSequence(
                    society=society,
                    labels=label,
                    fixed_order=f_order
                )
            )
    tree.save()
    return True
    

def load_trees(tree_dir, verbose=False):
    l_by_iso, l_by_glotto, l_by_name = \
        defaultdict(list), defaultdict(list), defaultdict(list)

    for lang in Language.objects.all().select_related('iso_code'):
        if lang.iso_code:
            l_by_iso[lang.iso_code.iso_code].append(lang)
        l_by_glotto[lang.glotto_code].append(lang)
        l_by_name[lang.name].append(lang)

    def get_language(taxon_name):
        if taxon_name in l_by_iso:
            return l_by_iso[taxon_name]
        if taxon_name in l_by_glotto:
            return l_by_glotto[taxon_name]
        if taxon_name in l_by_name:
            return l_by_name[taxon_name]

    count = 0
    for fname in os.listdir(tree_dir):
        if fname.endswith('.trees'):
            if _load_tree(os.path.join(tree_dir, fname), get_language):
                count += 1
    return count


def _load_tree(file_name, get_language, verbose=False):
    # make a tree if not exists. Use the name of the tree
    tree, created = LanguageTree.objects.get_or_create(
        name=os.path.basename(file_name)
    )
    if not created:
        return False

    with open(file_name, 'r') as f:
        tree.file = File(f)
        tree.save()

    # now add languages to the tree
    reader = NexusReader(file_name)
    # Remove '[&R]' from newick string
    reader.trees.detranslate()
    newick = re.sub(r'\[.*?\]', '', reader.trees.trees[0])
    try:
        newick = newick[newick.index('=') + 1:]
    except ValueError:  # pragma: no cover
        newick = newick
        
    if verbose:  # pragma: no cover
        logging.info("Formatting newick string %s" % (newick))
        
    tree.newick_string = str(newick)
    if 'global' not in file_name and'glotto' not in file_name:
        tree.save()
        return True
       
    # phylogeny taxa require reading of CSV mapping files, glottolog trees do not
    for taxon_name in reader.trees.taxa:
        if taxon_name is '1':
            continue  # pragma: no cover
        languages = get_language(taxon_name)
        if not languages:
            continue

        for l in languages:
            society = Society.objects.filter(language=l)
            label, created = LanguageTreeLabels.objects.get_or_create(
                languageTree=tree,
                label=taxon_name,
                language=l
            )
            for s in society:
                LanguageTreeLabelsSequence.objects.get_or_create(
                    society=s,
                    labels=label,
                    fixed_order=0
                )
            tree.taxa.add(label)
    tree.save()
    return True


def prune_trees():
    labels = LanguageTreeLabels.objects.all()
    count = 0
    for t in LanguageTree.objects.order_by('name').all():
        if update_newick(t, labels):
            count += 1
            t.save()
    return count
