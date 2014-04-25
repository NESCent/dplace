import sys
from dplace_app.models import *

MISSING_CODES = []

def run(mode=None):
    if mode == 'langs':
        clear_langs()
    elif mode == 'cultural':
        clear_cultural()
    elif mode == 'societies':
        clear_societies()
    elif mode == 'iso':
        clear_isocodes()
    elif mode == 'env':
        clear_environmentals()
    elif mode == 'all':
        clear_langs()
        clear_cultural()
        clear_environmentals()
        clear_societies()
        clear_isocodes()

def clear_langs():
    LanguageClassification.objects.all().delete()
    LanguageClass.objects.all().delete()
    Language.objects.all().delete()

def clear_cultural():
    VariableCodedValue.objects.all().delete()
    VariableCodeDescription.objects.all().delete()
    VariableDescription.objects.all().delete()
    VariableCategory.objects.all().delete()

def clear_societies():
    Society.objects.all().delete()

def clear_environmentals():
    EnvironmentalValue.objects.all().delete()
    Environmental.objects.all().delete()
    EnvironmentalVariable.objects.all().delete()

def clear_isocodes():
    ISOCode.objects.all().delete()

if __name__ == '__main__':
    run(sys.argv[1])
