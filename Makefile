# Set .ONESHELL to execute all lines in a recipe in a single shell
.ONESHELL:

# Set ENV_PREFIX to the path of the virtual environment's pip executable
ENV_PREFIX=$(shell python -c "if __import__('pathlib').Path('.venv/bin/pip').exists(): print('.venv/bin/')")

# Define help target to show available targets
.PHONY: help
help:             	## Show the help.
	@echo "Usage: make <target>"
	@echo ""
	@echo "Targets:"
	@fgrep "##" Makefile | fgrep -v fgrep

# Define venv target to create a virtual environment
.PHONY: venv
venv:			## Create a virtual environment
	@echo "Creating virtualenv ..."
	@rm -rf .venv
	@python3 -m venv .venv
	@./.venv/bin/pip install -U pip
	@echo
	@echo "Run 'source .venv/bin/activate' to enable the environment"

# Define install target to install dependencies
.PHONY: install
install:		## Install dependencies
	pip install -r requirements-dev.txt
	pip install -r requirements-test.txt
	pip install -r requirements.txt

# Define stress-test target to run stress tests
STRESS_URL = https://eacknmfbuoeqpzh6gsca4tyqc40spost.lambda-url.us-east-1.on.aws/ 
.PHONY: stress-test
stress-test:
	# change stress url to your deployed app 
	mkdir reports || true
	locust -f tests/stress/api_stress.py --print-stats --html reports/stress-test.html --run-time 60s --headless --users 100 --spawn-rate 1 -H $(STRESS_URL)

# Define model-test target to run model tests
.PHONY: model-test
model-test:			## Run tests and coverage
	mkdir reports || true
	pytest --cov-config=.coveragerc --cov-report term --cov-report html:reports/html --cov-report xml:reports/coverage.xml --junitxml=reports/junit.xml --cov=challenge tests/model

# Define api-test target to run API tests
.PHONY: api-test
api-test:			## Run tests and coverage
	mkdir reports || true
	pytest --cov-config=.coveragerc --cov-report term --cov-report html:reports/html --cov-report xml:reports/coverage.xml --junitxml=reports/junit.xml --cov=challenge tests/api

# Define build target to build the Python artifact
.PHONY: build
build:			## Build locally the python artifact
	python setup.py bdist_wheel