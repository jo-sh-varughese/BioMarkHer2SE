# Unit test cases (Assignment 2, Q3)

The cases below are asserted in [`tests/test_assignment_a2.py`](../tests/test_assignment_a2.py) and run by the CI
pipeline on every push. This table is produced by `python scripts/make_a2_test_table.py`, which calls each function
with the input shown and records what it returns.

| TC ID | Function tested | Input | Expected output | Actual output | Pass/Fail | Technique |
|---|---|---|---|---|---|---|
| TC01 | `map_to_cap_category` | strong = 10.0 %, others 0 | 2+ | 2+ | Pass | BVA (on boundary) |
| TC02 | `map_to_cap_category` | strong = 10.01 % | 3+ | 3+ | Pass | BVA (just above) |
| TC03 | `map_to_cap_category` | weak = 10.0 %, others 0 | 0 | 0 | Pass | BVA (on boundary) |
| TC04 | `map_to_cap_category` | weak = 10.01 % | 1+ | 1+ | Pass | BVA (just above) |
| TC05 | `map_to_cap_category` | all stain classes 0 % | 0 | 0 | Pass | EP (no staining) |
| TC06 | `weighted_quantile` | alpha = 0.0 and alpha = 1.0 | raises ValueError (both) | raises ValueError (both) | Pass | BVA (invalid boundary) |
| TC07 | `weighted_quantile` | scores 0.1 to 1.0 (n = 10), alpha = 0.5 | 0.6 | 0.6 | Pass | EP (valid alpha) |
| TC08 | `weighted_quantile` | empty score list, alpha = 0.1 | raises ValueError | raises ValueError | Pass | EP (invalid input) |
| TC09 | `field_quality.assess (image size)` | width = 255 px, then 256 px | 255 px blocked (too_small); 256 px accepted | 255 px blocked (too_small); 256 px accepted | Pass | BVA |
| TC10 | `field_quality.assess (cell count)` | n_cells = 29, then 30 | 29 blocked (few_cells); 30 accepted | 29 blocked (few_cells); 30 accepted | Pass | BVA |
| TC11 | `field_quality.assess (specimen)` | specimen = "gastric" | not assessable, reason not_breast | not assessable, reason not_breast | Pass | EP (non-breast) |
| TC12 | `verify_password` | right password, then same text in lower case | True, then False | True, then False | Pass | EP (valid / invalid) |
| TC13 | `hash_password` | same password hashed twice | two different hashes (salted) | two different hashes (salted) | Pass | EP |
| TC14 | `decode_upload` | bytes b"this is not an image" | raises ImageDecodeError | raises ImageDecodeError | Pass | EP (invalid input) |

**Result: 14 of 14 test cases passed.**

## Techniques used

- **Boundary value analysis (BVA):** TC01 to TC04 test the ASCO/CAP 10 % rule exactly on the boundary and just above it. TC06 tests the two invalid ends of the open interval (0, 1) for alpha. TC09 and TC10 test the image-size and cell-count limits of the field-quality gate one below, and exactly at, the limit.
- **Equivalence partitioning (EP):** TC05, TC07, TC08, TC11, TC12, TC13 and TC14 each pick one representative input from a class of inputs expected to behave alike (no staining, valid alpha, empty input, non-breast specimen, valid and invalid passwords, non-image bytes).
