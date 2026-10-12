# Test strategy

## What is tested, and how

The project has two layers of tests.

| Layer | Where | Size | Purpose |
|---|---|---|---|
| The project suite | `tests/` (about 40 files) | 547 tests | The project's specification: models, evaluation, the web server, the review record, the safety rules |
| The assignment cases | [`tests/test_assignment_a2.py`](../tests/test_assignment_a2.py) | 14 cases (15 test items) | A small, fast set designed with named techniques, tabulated in [`TEST_CASES.md`](TEST_CASES.md) |

CI runs both on every push ([`CI_CD.md`](CI_CD.md)). The assignment cases also run on Python 3.11 and 3.12.

## How the cases were designed

Each function under test has a rule that can be stated in one line, and the cases are placed where that rule can fail.

| Function | Rule | Technique | Cases |
|---|---|---|---|
| `map_to_cap_category` | 3+ needs more than 10 % strong staining; 1+ needs more than 10 % weak-or-above | Boundary value analysis: on the boundary and just above it | TC01 to TC04 |
| `map_to_cap_category` | No staining gives 0 | Equivalence partitioning | TC05 |
| `weighted_quantile` | alpha must lie strictly inside (0, 1) | Boundary value analysis: both invalid ends | TC06 |
| `weighted_quantile` | The result follows the conformal formula; empty input is refused | Equivalence partitioning | TC07, TC08 |
| `field_quality.assess` | A field needs at least `MIN_SIDE_PX` pixels and `CELLS_BLOCK` cells | Boundary value analysis: one below and exactly at the limit | TC09, TC10 |
| `field_quality.assess` | A non-breast specimen is refused | Equivalence partitioning | TC11 |
| `hash_password`, `verify_password` | Only the original password verifies; hashes are salted | Equivalence partitioning | TC12, TC13 |
| `decode_upload` | Bytes that are not an image are refused | Equivalence partitioning | TC14 |

The functions were chosen because a wrong answer here is a patient-safety problem, not a cosmetic one: a threshold off by one
changes a HER2 category, and a wrong quality verdict lets an unusable image receive a grade.

## What the assignment cases cover

Measured with `coverage run` on `tests/test_assignment_a2.py` alone, for the five modules the cases target:

| Module | Statements | Covered |
|---|---|---|
| `app/field_quality.py` | 151 | 79 % |
| `evaluation/cap_mapping.py` | 83 | 53 % |
| `evaluation/conformal.py` | 190 | 35 % |
| `app/image_io.py` | 45 | 29 % |
| `app/auth.py` | 638 | 19 % |
| **All five** | **1,107** | **33 %** |

These 14 cases are a focused sample, not the whole safety net: they target the rules above and leave the rest of each module to the
project suite. The coverage of the whole suite is measured on every CI run and shown on the run's summary page.

## Adding a test

1. Name the rule in one line and pick the technique (boundary value analysis for a limit, equivalence partitioning for a class of inputs).
2. Add the case to `tests/test_assignment_a2.py`, naming the technique in its docstring.
3. Add the same case to `scripts/make_a2_test_table.py` and run it to regenerate `docs/TEST_CASES.md`.
4. Open a pull request; CI must be green and another member must approve it.
