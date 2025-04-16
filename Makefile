.PHONY: install dashboard sample clean install-uv venv sync

# Check if UV is available
HAS_UV := $(shell command -v uv 2> /dev/null)

# Create virtual environment
venv:
ifdef HAS_UV
	@echo "Creating virtual environment with UV..."
	uv venv
else
	@echo "Creating virtual environment with Python..."
	python -m venv venv
endif
	@echo "Virtual environment created. Activate with 'source venv/bin/activate'"

# Install dependencies
install:
ifdef HAS_UV
	@echo "Installing with UV package manager..."
	uv pip install --system -r requirements.txt
	uv pip install --system -e .
else
	@echo "Installing with PIP (consider installing UV for faster package management)..."
	pip install -r requirements.txt
	pip install -e .
endif

# Install UV package manager
install-uv:
	@echo "Installing UV package manager..."
	pip install uv
	@echo "UV installed successfully. Now you can use 'make venv' and 'make install'"

# Run the dashboard
dashboard:
	python -m scripts.run_dashboard

# Generate sample data
sample:
	python -m scripts.dashboard.populate_sample_data

# Clean generated files
clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name *.egg-info -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Run all steps in sequence
all: install sample dashboard 

# Run sync process (ingest and transform data)
sync:
	@echo "Running data synchronization (ingest and transform)..."
	PYTHONPATH=. python -c "from peopleanalytics.cli_unified import main; main()" sync 