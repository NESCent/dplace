import sys
from dplace_app.models import *

MISSING_CODES = []

def run(mode=None):
    if mode == 'langs':
        clear_langs()
    elif mode == 'ea':
        clear_ea()
    elif mode == 'societies':
        clear_societies()
    elif mode == 'iso':
        clear_isocodes()
    elif mode == 'env':
        clear_environmentals()
    elif mode == 'all':
        clear_langs()
        clear_ea()
        clear_environmentals()
        clear_societies()
        clear_isocodes()

def clear_langs():
    LanguageClassification.objects.all().delete()
    LanguageClass.objects.all().delete()
    Language.objects.all().delete()

def clear_ea():
    EAVariableCodedValue.objects.all().delete()
    VariableCodeDescription.objects.all().delete()
    VariableDescription.objects.all().delete()

def clear_societies():
    Society.objects.all().delete()

def clear_environmentals():
    Environmental.objects.all().delete()

def clear_isocodes():
    ISOCode.objects.all().delete()

if __name__ == '__main__':
    run(sys.argv[1])
