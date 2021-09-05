TEST_DIR ?= tests
PROJECT_DIR ?= levy

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

isort:
	isort $(PROJECT_DIR)

lint:
	pylint --rcfile=.pylintrc $(PROJECT_DIR)

black:
	black $(PROJECT_DIR) $(TEST_DIR)

black_check:
	black --check --diff $(PROJECT_DIR)

unit:
	pytest $(TEST_DIR)

test_all: install install_test black_check lint unit
