# Contributing to Client Activity Monitor

## Development Setup

### Prerequisites

1. Python 3.10 or higher
2. Poetry for dependency management
3. Oracle Instant Client 19c+
4. Git

### Getting Started

1. Clone the repository:
   ```bash
   git clone https://github.com/yourorg/client-activity-monitor.git
   cd client-activity-monitor
   ```

2. Install development dependencies:
   ```bash
   poetry install --with dev
   ```

3. Set up pre-commit hooks (if using):
   ```bash
   pre-commit install
   ```

## Development Guidelines

### Code Style

- Follow PEP 8 Python style guide
- Use Black for code formatting
- Maximum line length: 100 characters
- Use type hints for function parameters and returns

### Testing

Run tests before submitting changes:

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=client_activity_monitor

# Run specific test file
poetry run pytest tests/unit/test_validators.py
```

### Code Quality

Check code quality:

```bash
# Format code
poetry run black src/ tests/

# Lint code
poetry run pylint src/

# Type checking
poetry run mypy src/
```

### Commit Messages

Follow conventional commits format:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes
- `refactor:` Code refactoring
- `test:` Test additions/changes
- `chore:` Build/tooling changes

Example: `feat: add CSV export functionality`

### Pull Request Process

1. Create a feature branch from `main`
2. Make your changes following guidelines
3. Add/update tests as needed
4. Update documentation if required
5. Ensure all tests pass
6. Submit PR with clear description

### Adding New Features

1. **Database Queries**: Add SQL file to `queries/` and update `databases.yaml`
2. **UI Components**: Follow existing panel patterns in `view/panels/`
3. **Services**: Add to appropriate service layer in `model/services/`
4. **Integrations**: Place in `model/integrations/`

### Architecture Principles

- Follow MVC pattern strictly
- Keep UI logic in View layer
- Business logic in Model layer
- Controller only orchestrates
- Use dependency injection
- Prefer composition over inheritance

## Project Structure

```
src/client_activity_monitor/
├── common/          # Shared utilities
├── controller/      # Application controller
├── model/           # Business logic
│   ├── integrations/   # External integrations
│   ├── repositories/   # Data access
│   └── services/       # Business services
└── view/            # UI components
    └── panels/         # UI panels
```

## Common Tasks

### Adding a New Database

1. Update `configs/databases.yaml`:
   ```yaml
   - name: new_database
     host: hostname
     port: 1521
     service_name: SERVICE
     sql_queries:
       - name: "Query Name"
         query_location: "queries/new_query.sql"
   ```

2. Add SQL file to `queries/` directory

3. Test connection and queries

### Adding a New Report Format

1. Extend `ReportGenerator` class
2. Add new method for format generation
3. Update UI to include new export option
4. Add tests for new functionality

### Debugging Tips

- Enable debug logging in `app_settings.yaml`
- Use Oracle trace for connection issues
- Check `logs/` directory for detailed logs
- Use debugger with breakpoints in threads

## Questions?

Contact the development team or open an issue on GitHub.