import re
from collections import defaultdict

from clldutils.misc import nfilter
from nexus import NexusReader
from ete3 import Tree
from dplace_app.models import (
    Society, LanguageTree, Language, LanguageTreeLabels, LanguageTreeLabelsSequence,
)
from dplace_app.tree import update_newick


def load_trees(repos):
    l_by_iso, l_by_glotto, l_by_name = \
        defaultdict(list), defaultdict(list), defaultdict(list)

    for lang in Language.objects.all():
        if lang.iso_code:
            l_by_iso[lang.iso_code].append(lang)
        l_by_glotto[lang.glotto_code].append(lang)
        l_by_name[lang.name].append(lang)

    def get_language(taxon_name):
        if taxon_name in l_by_iso:
            return l_by_iso[taxon_name]
        if taxon_name in l_by_glotto:
            return l_by_glotto[taxon_name]
        if taxon_name in l_by_name:
            return l_by_name[taxon_name]

    sources, sequences, labels = {}, [], []
    trees = [
        _load_tree(obj, get_language, sources, sequences, labels)
        for obj in repos.phylogenies + repos.trees]
    LanguageTreeLabelsSequence.objects.bulk_create(sequences)

    for t in trees:
        update_newick(t, labels)
    return len(trees)


def _load_tree(obj, get_language, sources, sequences, labels):
    # now add languages to the tree
    reader = NexusReader(obj.trees.as_posix())

    tree = LanguageTree.objects.create(name=obj.id)
    source = sources.get((obj.author, obj.year))
    if not source:
        sources[(obj.author, obj.year)] = source = obj.as_source()
        source.save()
    tree.source = source

    # Remove '[&R]' from newick string
    reader.trees.detranslate()
    newick = re.sub(r'\[.*?\]', '', reader.trees.trees[0])
    try:
        newick = newick[newick.index('=') + 1:]
    except ValueError:  # pragma: no cover
        newick = newick

    tree.newick_string = str(newick)
    Tree(tree.newick_string, format=1)

    def labels_for_language(taxon, language_id=None):
        language_id = language_id or taxon
        languages = get_language(language_id)
        if languages:
            for l in languages:
                label = LanguageTreeLabels.objects.create(
                    languageTree=tree, label=taxon, language=l)
                labels.append(label)
                tree.taxa.add(label)
                for s in Society.objects.filter(language=l):
                    sequences.append(LanguageTreeLabelsSequence(
                        society=s, labels=label, fixed_order=0))

    if obj.__class__.__name__ == 'Tree':
        for taxon_name in reader.trees.taxa:
            labels_for_language(taxon_name)
    else:
        for item in obj.taxa:
            name_on_tip = item['taxon']
            xd_ids = nfilter(i.strip() for i in item['xd_ids'].split(','))
            society_ids = nfilter(i.strip() for i in item['soc_ids'].split(','))
            if not xd_ids:
                if item['glottocode']:
                    labels_for_language(name_on_tip, item['glottocode'])
                continue

            label = LanguageTreeLabels.objects.create(
                languageTree=tree, label=name_on_tip)
            labels.append(label)
            tree.taxa.add(label)
            for society in Society.objects.all().filter(xd_id__in=xd_ids):
                try:
                    f_order = len(society_ids) - society_ids.index(society.ext_id) - 1
                except:
                    f_order = 0
                sequences.append(LanguageTreeLabelsSequence(
                    society=society, labels=label, fixed_order=f_order))
    tree.save()
    return tree
