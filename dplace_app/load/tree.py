import re
import logging
from collections import defaultdict

from django.core.files.base import ContentFile
from nexus import NexusReader
from ete3 import Tree
from ete3.coretype.tree import TreeError
from dplace_app.models import (
    Society, LanguageTree, Language, LanguageTreeLabels, LanguageTreeLabelsSequence,
    Source,
)
from dplace_app.tree import update_newick
from clldutils.path import Path
from clldutils import dsv


def tree_names(data_dir):
    sequences = []
    phylo_dir = Path(data_dir).joinpath('phylogenies')
    if phylo_dir.joinpath('phylogenies.csv').exists():
        for phylo in dsv.reader(phylo_dir.joinpath('phylogenies.csv'), dicts=True):
            _tree_names(phylo_dir.joinpath(phylo['Directory']), sequences)
    LanguageTreeLabelsSequence.objects.bulk_create(sequences)
    return len(sequences)
            

def _tree_names(tree_dir, label_sequences):
    try:
        tree = LanguageTree.objects.get(name=tree_dir.name)
    except:
        return False

    try:
        Tree(tree.newick_string, format=1)
    except TreeError:
        return False

    for item in dsv.reader(tree_dir.joinpath('xdid_socid_links.csv'), dicts=True):
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


def load_trees(data_dir, verbose=False):
    data_dir = Path(data_dir)
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
    if data_dir.joinpath('phylogenies', 'phylogenies.csv').exists():
        for phylo in dsv.reader(
                data_dir.joinpath('phylogenies', 'phylogenies.csv'), dicts=True):
            fname = data_dir.joinpath('phylogenies', phylo['Directory'])
            assert fname.is_dir() and fname.joinpath('summary.trees').exists()
            if _load_tree(
                    fname.name,
                    fname.joinpath('summary.trees'),
                    get_language,
                    source=phylo):
                count += 1

    for fname in data_dir.joinpath('trees').iterdir():
        if fname.name.endswith('.trees'):
            if _load_tree(fname.stem, fname, get_language):
                count += 1
    return count


def _load_tree(name, fname, get_language, verbose=False, source=None):
    # now add languages to the tree
    try:
        reader = NexusReader(fname.as_posix())
    except:
        print(fname)
        raise

    # make a tree if not exists. Use the name of the tree
    tree, created = LanguageTree.objects.get_or_create(name=name)
    if not created:
        return False

    if source:
        source = Source.objects.create(
            **{k.lower(): source[k] for k in 'Year Author Name Reference'.split()})
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
    if source:
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
