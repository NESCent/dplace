all: install

install:
	dropdb dplace
	createdb dplace
	pip install --upgrade -r requirements.txt
	python manage.py migrate
	./load_all_datasets.sh
	
test:
	python manage.py test
	npm test
