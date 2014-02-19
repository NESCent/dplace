import sys
from dplace_app.models import *

MISSING_CODES = []

def run(mode=None):
    if mode == 'langs':
        clear_langs()

def clear_langs():
    LanguageClassification.objects.all().delete()
    LanguageClass.objects.all().delete()
    LanguageFamily.objects.all().delete()
    Language.objects.all().delete()

if __name__ == '__main__':
    run(sys.argv[1])
