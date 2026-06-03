# Development

How to set up a development environment for Pool Chem.

## Prerequisites

- Python 3.13+ and [`uv`](https://docs.astral.sh/uv/).

## Setup

```bash
git clone https://github.com/joyfulhouse/ha-poolchem.git
cd ha-poolchem
uv sync --extra dev
```

## Quality Checks

```bash
uv run pytest                                   # tests
uv run pytest --cov=custom_components/poolchem  # tests with coverage
uv run ruff check --fix custom_components/poolchem  # lint
uv run ruff format custom_components/poolchem       # format
uv run mypy custom_components/poolchem              # type check
```

Run all of these before opening a pull request. See
[CONTRIBUTING](https://github.com/joyfulhouse/.github/blob/main/CONTRIBUTING.md)
for the contribution workflow.

## Testing with a Live Home Assistant Instance

Map the integration into a Home Assistant dev container:

```yaml
# docker-compose.yaml
services:
  homeassistant:
    image: homeassistant/home-assistant:latest
    volumes:
      - ./config:/config
      - ./custom_components/poolchem:/config/custom_components/poolchem
```

Restart the container to load changes: `docker compose up -d`

Check logs: `docker compose logs homeassistant | grep poolchem`

## Writing Tests

Tests live in `tests/` and use `pytest-homeassistant-custom-component`.

Key fixtures (defined in `tests/conftest.py`):
- `hass` — Home Assistant test instance
- `mock_source_entities` — creates mock sensor entities
- `mock_config_entry_data` — standard config entry data

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for a description of the integration's structure and design
decisions. All chemistry calculations live in
[pypoolchem](https://github.com/joyfulhouse/pypoolchem); this integration is a thin HA wrapper.

## Releasing

1. Update `version` in `custom_components/poolchem/manifest.json` and `pyproject.toml`.
2. Add a new entry to `CHANGELOG.md`.
3. Create and push a tag: `git tag vX.Y.Z && git push origin vX.Y.Z`.
4. GitHub Actions publishes the release.
