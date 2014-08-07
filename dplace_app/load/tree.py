from os.path import basename
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from nexus import NexusReader
from dplace_app.models import LanguageTree, Language
__author__ = 'dan'

def load_tree(file_name):
    # make a tree if not exists. Use the name of the tree
    tree_name = basename(file_name)
    tree, created = LanguageTree.objects.get_or_create(name=tree_name)
    # now add languages to the tree
    reader = NexusReader(file_name)
    for language_name in reader.trees.taxa:
        try:
            language = Language.objects.get(name=language_name)
            tree.languages.add(language)
        except ObjectDoesNotExist:
            print "Warning: Language %s in tree %s not found" % (language_name, tree_name)
        except MultipleObjectsReturned:
            print "Error: multiple languages returned for %s" % (language_name)
    tree.save()

