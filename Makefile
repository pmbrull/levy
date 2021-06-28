install:
	@echo "Installing requirements..."
	pip install -r requirements.txt

install_test:
	@echo "Installing test requirements..."
	pip install -r requirements-test.txt

precommit_install:
	@echo "Installing pre-commit hooks"
	@echo "Make sure to first run `make install_test`"
	pre-commit install

lint:
	pylint --rcfile=.pylintrc levy

black:
	black levy tests

black_check:
	black --check --diff levy

unit:
	pytest tests

test_all: install install_test black_check lint unit
