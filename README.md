# Catalyst Make.com Python Client

Tools for automating Make.com workflow deployment and management for service business automations.

## Features

- **Async API Client** — Non-blocking Make.com API interactions
- **Pydantic Models** — Type-safe request/response handling
- **Unit Tests** — Comprehensive test coverage
- **GitHub Actions** — Automated CI/CD with pytest, ruff, black

## What's Included

- **src/catalyst_make_client/** — Main client library
  - `client.py` — Async Make.com API client
  - `models.py` — Pydantic models for validation
- **tests/** — Full test suite
  - `test_client.py` — API client tests
  - `test_models.py` — Model validation tests
- **pyproject.toml** — uv-compatible Python project config
- **.github/workflows/tests.yml** — CI/CD pipeline

## Quick Start

### 1. Install with uv

```bash
uv venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
uv pip install -e .
```

### 2. Set Your Make.com API Key

```bash
export MAKE_API_KEY="your_api_key_here"
```

Or save to `~/.catalyst_make_key`:
```bash
echo "your_api_key_here" > ~/.catalyst_make_key
```

### 3. Use the Client

```python
import asyncio
from catalyst_make_client import MakeClient

async def main():
    async with MakeClient() as client:
        # Test connection
        if await client.test_connection():
            print("✅ Connected to Make.com")
        
        # Get organization
        org = await client.get_organization()
        print(f"Organization: {org.name}")
        
        # List scenarios
        scenarios = await client.list_scenarios()
        for scenario in scenarios:
            print(f"  - {scenario.name} (ID: {scenario.id})")

asyncio.run(main())
```

### 4. Run Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=src

# Specific test file
pytest tests/test_client.py

# Watch mode (requires pytest-watch)
ptw
```

### 5. Code Quality

```bash
# Format code
black .

# Check formatting
black --check .

# Lint
ruff check .
ruff check --fix .
```

## Development

### Install Dev Dependencies

```bash
uv pip install -e ".[dev]"
```

### Project Structure

```
catalyst-make-client/
├── src/
│   └── catalyst_make_client/
│       ├── __init__.py
│       ├── client.py          # Async API client
│       └── models.py          # Pydantic models
├── tests/
│   ├── __init__.py
│   ├── test_client.py         # Client tests
│   └── test_models.py         # Model tests
├── pyproject.toml             # uv config
├── README.md
└── .github/
    └── workflows/
        └── tests.yml          # CI/CD pipeline
```

## API Reference

### MakeClient

```python
async with MakeClient(token="...") as client:
    # Get organization
    org = await client.get_organization()
    
    # List scenarios
    scenarios = await client.list_scenarios(limit=100)
    
    # Get specific scenario
    scenario = await client.get_scenario(scenario_id=123)
    
    # List executions for a scenario
    executions = await client.list_executions(scenario_id=123)
    
    # Test connection
    connected = await client.test_connection()
```

## Integration Points

- Jobber / Calendly / Acuity (scheduling)
- QuickBooks / Xero / Stripe (payments & invoicing)
- Twilio (SMS)
- Google Business Profile / Google Reviews (reputation)
- HubSpot / Airtable (CRM)
- Facebook Ads / Google Ads (lead capture)
- Make.com (workflow automation)

## Testing

The repo includes comprehensive unit tests that run in GitHub Actions on every push:

- Tests run on Python 3.9, 3.10, 3.11, 3.12
- Code formatting checked with black
- Linting with ruff
- Coverage reports uploaded to Codecov

## Contact

📧 catalyst.ai.services@gmail.com  
📞 (619) 800-2253  
🏢 San Diego, CA
