test:
	python -m unittest discover -v

stress:
	python -m unittest discover -v -p 'stress_*.py'

pep8:
	pep8 --filename=*.py --exclude=.tox,build

pyflakes:
	pyflakes *.py testsuite

audit: pep8 pyflakes

clean:
	rm -vfr dist *.egg-info *.pyc __pycache__ build .coverage htmlcov \
		testsuite/*.pyc testsuite/__pycache__

coverage:
	coverage run -p -m unittest discover
	coverage run -p testsuite/force_print.py --end=''
	coverage combine
	coverage report
	coverage html

import_time:
	python -m timeit -n 1 -r 1 'import utile'
