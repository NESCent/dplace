
Creating a production release of dplace
=======================================


- Run flake8 to check for pep8 conformance:

```
flake8 --exclude=migrations,static --ignore=E711,E712,D100,D101,D103,D102,D301,E402,E731 --max-line-length=100 dplace_app
```

- Run the tests and make sure coverage is >90%:

```
coverage run --source='dplace_app' manage.py test
coverage report -m
```

- Destroy database, upgrade and reload data:

```
#!/bin/bash
dropdb dplace 
createdb dplace
pip install --upgrade -r requirements.txt
python manage.py migrate
./load_all_datasets.sh
```
