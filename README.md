# Deltakit SDK - Independent Test Suite

A black-box test suite for Deltakit, Riverlane open-source quantum error
correction (QEC) SDK. This repository demonstrates an independent,
consumer-side approach to verifying a QEC SDK: testing the product as
shipped, not contributing tests upstream.

## Why

Riverlane Staff Testing Engineer role is about verifying Deltaflow and
the Deltakit software stack - treating them as products with contracts,
invariants, and failure modes. This repo does exactly that, using
Deltakit as a dependency.

## What It Tests

The suite is layered:

| Layer       | What it verifies                                                  | Directory            |
|-------------|-------------------------------------------------------------------|----------------------|
| Unit        | QEC code construction - qubit counts, stabiliser structure        | tests/unit/          |
| Contract    | Public API returns the shapes and types it promises               | tests/contract/      |
| Negative    | Invalid inputs fail loudly and early                              | tests/negative/      |
| Integration | Full code to circuit to noise to simulation pipeline              | tests/integration/   |
| Cloud       | Token-gated tests for proprietary decoders                        | tests/cloud/         |

## Running Locally

    python -m venv .venv
    .venv/Scripts/activate         # Windows
    pip install -r requirements-dev.txt
    pip install deltakit
    pytest tests/ -v

Cloud tests will be skipped unless DELTAKIT_TOKEN is set.
See TESTING.md for the strategy document.

## Findings

During development, this suite has surfaced several behaviours in the
shipped SDK worth raising with the Deltakit maintainers. These are
documented in TESTING.md and where possible captured as xfail tests.

## Structure

    .
    |-- tests/
    |   |-- conftest.py
    |   |-- unit/
    |   |-- contract/
    |   |-- negative/
    |   |-- integration/
    |   `-- cloud/
    |-- investigations/       # Scripts used to discover the API surface
    |-- TESTING.md            # Test strategy and risk assessment
    `-- .github/workflows/    # CI

## License

MIT
