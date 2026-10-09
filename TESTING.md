# Test Strategy - Deltakit SDK

## 1. Purpose

This document describes the test strategy for independently verifying
the Deltakit SDK as a consumed product. It is written from the
perspective of a Staff Test Engineer joining a QEC organisation,
treating Deltakit and Deltaflow as systems whose quality must be
asserted externally.

## 2. Scope

In scope:
- Public API of deltakit-explorer, deltakit-circuit, deltakit-decode
- QEC code construction correctness
- Full code to circuit to noise to simulation pipeline
- API contract stability
- Negative input handling
- Cloud-token gated features (when credentials present)

Out of scope:
- Internal implementation of proprietary decoders (black-box only)
- Performance benchmarking at production scale
- Hardware-level testing of Deltaflow (no hardware access)

## 3. Risk Assessment

| ID  | Risk                                                           | Impact   | Likelihood | Coverage             |
|-----|----------------------------------------------------------------|----------|------------|----------------------|
| R1  | Silent wrong result from decoder (logical error rate wrong)    | Critical | Medium     | Integration (partial)|
| R2  | Noise model accepts out-of-range parameters silently           | High     | Confirmed  | Negative (xfail)     |
| R3  | Circuit to Stim conversion silently corrupts gates             | High     | Low        | Contract             |
| R4  | Stabiliser/parity-matrix inconsistency between representations | High     | Low        | Unit (cross-check)   |
| R5  | API drift - return types change without notice                 | Medium   | Medium     | Contract             |
| R6  | Code construction accepts invalid parameters                   | Low      | Very low   | Negative (strong)    |
| R7  | Reproducibility - same seed produces different results         | Medium   | Unknown    | Not yet covered      |

Note on R6: The SDK demonstrates strong input validation across all
tested constructors. Every invalid input tested raised a `ValueError`
with a clear message. This risk is assessed as very low.

## 4. Test Levels

| Level       | Purpose                                  | Directory            |
|-------------|------------------------------------------|----------------------|
| Unit        | Structural invariants of code objects    | tests/unit/          |
| Contract    | Public API returns declared shapes/types | tests/contract/      |
| Negative    | Invalid inputs rejected at boundary      | tests/negative/      |
| Integration | Physical correctness of full pipeline    | tests/integration/   |
| Cloud       | Token-gated proprietary features         | tests/cloud/         |

## 5. Environment Strategy

- Local (default): cloud tests skip automatically. All other tests run.
- CI: DELTAKIT_TOKEN supplied via GitHub secret. Cloud tests run.
- Fork PRs: secrets are not passed by GitHub. Cloud tests skip.
- Noise model: all tests use SI1000Noise at p=0.01 unless noted.

## 6. Exit Criteria

A release is considered verified when:
- All unit, contract, and negative tests pass
- All integration tests pass with no xfail transitions
- Detector rate monotonicity holds
- Zero-noise invariant holds
- No new defects added to the findings log below

## 7. Findings Log

### DEFECT-001 - RepetitionCode does not expose its stabiliser basis

Severity: Low (API ergonomics)
Discovered: Unit test `test_z_stabiliser_type_stored` (removed)

The `stabiliser_type` parameter is used at construction time but not
stored on the instance. Consumers who receive a `RepetitionCode` object
cannot determine its basis from the object alone without inspecting
`.stabilisers` or `.parity_check_matrices`.

Recommendation: Store `stabiliser_type` as a public read-only attribute,
or document clearly that it is not queryable post-construction.

### DEFECT-002 - SI1000Noise accepts out-of-range probabilities

Severity: High (silent invalid state)
Discovered: `investigations/inspect_remaining_api.py`, section 4

`SI1000Noise(p=-0.1)` and `SI1000Noise(p=1.5)` both construct
successfully. A probability outside [0, 1] is physically meaningless.
Downstream simulation may produce undefined or misleading results.

Recommendation: Validate `p` in [0, 1] at construction and raise
`ValueError`.

Tests: `tests/negative/test_circuit_negative.py::TestNoiseParameterValidation`

### Observation - Input validation is otherwise strong

During negative testing, the following SDK behaviours were confirmed
as correct and are now locked in by tests:
- `RepetitionCode(distance=0)` -> `ValueError("Code distance must be at least 2.")`
- `RepetitionCode(stabiliser_type="Z")` -> `ValueError` about PauliBasis
- `RotatedPlanarCode(width=1)` -> `ValueError("Width and height need to be ...")`
- `css_code_memory_circuit(num_rounds=0)` -> raises

These are recorded as positive findings: the SDK validates inputs at
its boundaries and produces clear error messages. This is the pattern
SI1000Noise should follow (see DEFECT-002).

## 8. Known Limitations

- Cloud decoder API not yet fully mapped.
- No reproducibility test: `simulate_with_stim` does not accept a seed
  parameter, and Stim default seeding may not be deterministic across
  versions.
- Coverage measured against test code itself, not against the SDK.