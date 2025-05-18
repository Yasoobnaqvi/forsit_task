# E-commerce Admin API Test Suite

This directory contains comprehensive tests for the E-commerce Admin API.

## Test Categories

1. **Unit/Integration Tests**: Tests for API endpoints and functionality
   - Tests for all CRUD operations on categories, products, inventory, and sales
   - Tests for analytics functionality
   - Tests for error handling and edge cases
   - Integration tests for complete workflows

2. **Data Seeding Tests**: Tests for the demo data generation script
   - Verifies that all required data is properly created
   - Checks for duplicate prevention

3. **Load Tests**: Performance testing with Locust
   - Simulates real-world user behavior
   - Tests API under various load conditions

## Running the Tests

### Unit and Integration Tests

```bash
# From the services/dashboard directory
pytest tests/test_api.py -v
```

### Data Seeding Tests

```bash
# From the services/dashboard directory
pytest tests/test_seed_data.py -v
```

### Load Tests

```bash
# From the services/dashboard directory
locust -f tests/locustfile.py
```

Then open http://localhost:8089 in your browser to control the load test.

## Test Database

The tests use SQLite in-memory databases to avoid affecting the main PostgreSQL database. This makes tests faster and isolates them from the production data.

## Adding More Tests

When adding new tests:

1. Place unit/integration tests in `test_api.py` or create a new file for specific components
2. Follow the existing test structure and naming conventions
3. Use pytest fixtures for setup and teardown
4. Make sure your tests are isolated and don't rely on external state 