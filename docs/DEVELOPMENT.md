# Development Setup

## Prerequisites
- Python 3.9 or higher
- Git

## Setup Instructions

1. Clone the repository:
```bash
git clone <repository-url>
cd RT_Academy
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
# On Windows:
.\.venv\Scripts\Activate.ps1
# On macOS/Linux:
source venv/bin/activate
```

3. Install the package in development mode:
```bash
pip install -e .[dev]
```

4. Install pre-commit hooks:
```bash
pre-commit install
```

5. Run the application:
```bash
streamlit run app.py
```

## Development Workflow

1. Before committing, run:
```bash
pre-commit run --all-files
```

2. Run type checking:
```bash
mypy src/
```

3. Run documentation checks:
```bash
pydocstyle src/
```

## Maintenance

### Update pre-commit hooks:
```bash
# Update all hooks to latest versions
pre-commit autoupdate

# Update specific repository
pre-commit autoupdate --repo https://github.com/pre-commit/pre-commit-hooks
```

### Check for outdated dependencies:
```bash
# Check what would be updated
pip list --outdated

# Update dependencies in pyproject.toml if needed
pip install -e .[dev] --upgrade
```

## Documentation Standards

Please follow the guidelines in `docs/DOCUMENTATION_STANDARDS.md` when writing code.
