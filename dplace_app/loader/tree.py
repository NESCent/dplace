import re
import logging
from collections import defaultdict

from django.core.files.base import ContentFile
from nexus import NexusReader
from ete3 import Tree
from ete3.coretype.tree import TreeError
from dplace_app.models import (
    Society, LanguageTree, Language, LanguageTreeLabels, LanguageTreeLabelsSequence,
)
from dplace_app.tree import update_newick


def tree_names(repos):
    sequences = []
    for phylo in repos.phylogenies:
        _tree_names(phylo, sequences)
    LanguageTreeLabelsSequence.objects.bulk_create(sequences)
    return len(sequences)
            

def _tree_names(phylo, label_sequences):
    try:
        tree = LanguageTree.objects.get(name=phylo.id)
    except:
        return False

    try:
        Tree(tree.newick_string, format=1)
    except TreeError:
        return False

    for item in phylo.xdid_socid_links:
        name_on_tip = item['Name_on_tree_tip']
        xd_ids = [i.strip() for i in item['xd_id'].split(',')]
        society_ids = [i.strip() for i in item['soc_id'].split(',')]

        if not xd_ids:  # pragma: no cover
            continue

        label, created = LanguageTreeLabels.objects.get_or_create(
            languageTree=tree, label=name_on_tip)
        
        tree.taxa.add(label)
        for society in Society.objects.all().filter(xd_id__in=xd_ids):
            try:
                f_order = len(society_ids) - society_ids.index(society.ext_id) - 1
            except:
                f_order = 0
            label_sequences.append(
                LanguageTreeLabelsSequence(
                    society=society, labels=label, fixed_order=f_order))
    tree.save()
    return True


def load_trees(repos, verbose=False):
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
    for phylo in repos.phylogenies:
        count += _load_tree(phylo.id, phylo.trees, get_language, phylo=phylo)

    for fname in repos.path('trees').iterdir():
        if fname.name.endswith('.trees'):
            count += _load_tree(fname.stem, fname, get_language)
    return count


def _load_tree(name, fname, get_language, verbose=False, phylo=None):
    # now add languages to the tree
    reader = NexusReader(fname.as_posix())

    # make a tree if not exists. Use the name of the tree
    tree, created = LanguageTree.objects.get_or_create(name=name)
    if not created:
        return 0

    if phylo:
        source = phylo.as_source()
        source.save()
        tree.source = source

    with open(fname.as_posix(), 'rb') as f:
        tree.file = ContentFile(f.read())
        tree.save()

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
    if phylo:
        tree.save()
        return 1

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
    return 1


def prune_trees(_):
    labels = LanguageTreeLabels.objects.all()
    count = 0
    for t in LanguageTree.objects.order_by('name').all():
        if update_newick(t, labels):
            count += 1
            t.save()
    return count
