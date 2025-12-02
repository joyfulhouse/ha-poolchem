# Contributing to Pool Chemistry

Thank you for your interest in contributing to the Pool Chemistry integration!

## Getting Started

### Prerequisites

- Python 3.13 or newer
- [uv](https://github.com/astral-sh/uv) package manager (recommended)
- Home Assistant development environment (optional, for testing)

### Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/joyfulhouse/ha-poolchem.git
   cd ha-poolchem
   ```

2. Install dependencies:
   ```bash
   uv sync --extra dev
   ```

3. Run tests:
   ```bash
   uv run pytest
   ```

4. Run type checking:
   ```bash
   uv run mypy custom_components/poolchem
   ```

5. Run linting:
   ```bash
   uv run ruff check custom_components/poolchem
   uv run ruff format custom_components/poolchem
   ```

## Development Workflow

### Code Style

This project uses:
- **Ruff** for linting and formatting
- **MyPy** for type checking (strict mode where possible)
- **pytest** for testing

Run all checks before committing:
```bash
uv run ruff check --fix custom_components/poolchem
uv run ruff format custom_components/poolchem
uv run mypy custom_components/poolchem
uv run pytest
```

### Testing with Home Assistant

For development with a live Home Assistant instance:

1. Use the development docker-compose setup:
   ```yaml
   volumes:
     - ./custom_components/poolchem:/config/custom_components/poolchem
   ```

2. Restart Home Assistant after code changes

3. Check logs for errors:
   ```bash
   docker compose logs homeassistant | grep poolchem
   ```

### Writing Tests

Tests live in the `tests/` directory and use `pytest-homeassistant-custom-component`.

Key fixtures:
- `hass`: Home Assistant test instance
- `mock_source_entities`: Creates mock sensor entities
- `mock_config_entry_data`: Standard config entry data

Example test:
```python
async def test_my_feature(
    hass: HomeAssistant,
    mock_source_entities: None,
    mock_config_entry_data: dict[str, Any],
) -> None:
    """Test description."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data=mock_config_entry_data,
        options={},
    )
    entry.add_to_hass(hass)

    coordinator = PoolChemCoordinator(hass, entry)
    await coordinator.async_setup()

    assert coordinator.data is not None
    # ... assertions
```

## Pull Request Process

1. **Fork** the repository
2. **Create a branch** for your feature (`git checkout -b feature/my-feature`)
3. **Make changes** following code style guidelines
4. **Add tests** for new functionality
5. **Run all checks** (lint, type check, test)
6. **Commit** with a clear message
7. **Push** and create a Pull Request

### Commit Messages

Use clear, descriptive commit messages:
- `feat: Add support for mineral pools`
- `fix: Handle unavailable temperature sensor`
- `docs: Update installation instructions`
- `test: Add coordinator edge case tests`

### PR Requirements

- All tests must pass
- Type checking must pass
- Linting must pass
- New features should include tests
- Documentation updates as needed

## Reporting Issues

When reporting issues, please include:

1. **Home Assistant version**
2. **Integration version**
3. **Steps to reproduce**
4. **Expected vs actual behavior**
5. **Relevant log entries**
6. **Diagnostics** (if possible, from Settings > Devices & Services > Pool Chemistry > ... > Download diagnostics)

## Feature Requests

Feature requests are welcome! Please:

1. Check existing issues to avoid duplicates
2. Describe the use case
3. Explain the expected behavior
4. Consider implementation complexity

## Code of Conduct

- Be respectful and constructive
- Focus on the technical aspects
- Welcome newcomers
- Assume good intent

## Questions?

- Open a GitHub Discussion for general questions
- Open an Issue for bugs or feature requests
- Check existing documentation first

Thank you for contributing!
