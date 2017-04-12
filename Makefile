all: install

install:
	dropdb dplace
	createdb dplace
	pip install --upgrade -r requirements.txt
	python manage.py migrate
	./load_all_datasets.sh ../dplace-data
	
test:
	python manage.py test
	npm test
