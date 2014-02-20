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

def clear_langs():
    LanguageClassification.objects.all().delete()
    LanguageClass.objects.all().delete()
    LanguageFamily.objects.all().delete()
    Language.objects.all().delete()

def clear_ea():
    EAVariableCodedValue.objects.all().delete()
    EAVariableCodeDescription.objects.all().delete()
    EAVariableDescription.objects.all().delete()

def clear_societies():
    Society.objects.all().delete()

if __name__ == '__main__':
    run(sys.argv[1])
