"""Run the assignment test cases and write docs/TEST_CASES.md.

The "Actual output" column is what the function really returns for the input
shown; Pass/Fail compares it with the expected output. The same cases are
asserted in tests/test_assignment_a2.py, which is what CI runs.

    python scripts/make_a2_test_table.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import field_quality as fq  # noqa: E402
from app.auth import hash_password, verify_password  # noqa: E402
from app.image_io import ImageDecodeError, decode_upload  # noqa: E402
from evaluation.cap_mapping import map_to_cap_category  # noqa: E402
from evaluation.conformal import weighted_quantile  # noqa: E402
from tests.test_field_quality import _her2_like  # noqa: E402

S, M, W, N = "strong (3+)", "moderate (2+)", "weak (1+)", "negative"


def pct(strong=0.0, moderate=0.0, weak=0.0):
    return {S: strong, M: moderate, W: weak, N: 100.0 - strong - moderate - weak}


def raises(fn, exc=ValueError):
    try:
        fn()
    except exc as e:
        return f"raises {type(e).__name__}"
    return "no error"


GOOD = fq.measure_image(_her2_like(512))
SCORES = np.linspace(0.1, 1.0, 10)


def codes(v):
    return sorted(r["code"] for r in v["reasons"] if r["level"] == fq.BLOCK)


# (id, function tested, input, expected, actual, technique)
CASES = [
    ("TC01", "map_to_cap_category", "strong = 10.0 %, others 0", "2+",
     lambda: map_to_cap_category(pct(strong=10.0)).category, "BVA (on boundary)"),
    ("TC02", "map_to_cap_category", "strong = 10.01 %", "3+",
     lambda: map_to_cap_category(pct(strong=10.01)).category, "BVA (just above)"),
    ("TC03", "map_to_cap_category", "weak = 10.0 %, others 0", "0",
     lambda: map_to_cap_category(pct(weak=10.0)).category, "BVA (on boundary)"),
    ("TC04", "map_to_cap_category", "weak = 10.01 %", "1+",
     lambda: map_to_cap_category(pct(weak=10.01)).category, "BVA (just above)"),
    ("TC05", "map_to_cap_category", "all stain classes 0 %", "0",
     lambda: map_to_cap_category(pct()).category, "EP (no staining)"),
    ("TC06", "weighted_quantile", "alpha = 0.0 and alpha = 1.0", "raises ValueError (both)",
     lambda: " and ".join(raises(lambda a=a: weighted_quantile(SCORES, a)) for a in (0.0, 1.0)).replace(
         "raises ValueError and raises ValueError", "raises ValueError (both)"), "BVA (invalid boundary)"),
    ("TC07", "weighted_quantile", "scores 0.1 to 1.0 (n = 10), alpha = 0.5", "0.6",
     lambda: f"{weighted_quantile(SCORES, 0.5):.1f}", "EP (valid alpha)"),
    ("TC08", "weighted_quantile", "empty score list, alpha = 0.1", "raises ValueError",
     lambda: raises(lambda: weighted_quantile(np.array([]), 0.1)), "EP (invalid input)"),
    ("TC09", "field_quality.assess (image size)", f"width = {fq.MIN_SIDE_PX - 1} px, then {fq.MIN_SIDE_PX} px",
     "255 px blocked (too_small); 256 px accepted",
     lambda: ("255 px blocked (too_small)" if "too_small" in codes(fq.assess({**GOOD, "width": fq.MIN_SIDE_PX - 1, "height": 512}))
              else "255 px accepted") + "; " + ("256 px accepted" if "too_small" not in codes(
                  fq.assess({**GOOD, "width": fq.MIN_SIDE_PX, "height": 512})) else "256 px blocked"), "BVA"),
    ("TC10", "field_quality.assess (cell count)", f"n_cells = {fq.CELLS_BLOCK - 1}, then {fq.CELLS_BLOCK}",
     f"{fq.CELLS_BLOCK - 1} blocked (few_cells); {fq.CELLS_BLOCK} accepted",
     lambda: (f"{fq.CELLS_BLOCK - 1} blocked (few_cells)" if "few_cells" in codes(
         fq.assess(GOOD, tissue_percent=60, n_cells=fq.CELLS_BLOCK - 1)) else f"{fq.CELLS_BLOCK - 1} accepted")
     + "; " + (f"{fq.CELLS_BLOCK} accepted" if "few_cells" not in codes(
         fq.assess(GOOD, tissue_percent=60, n_cells=fq.CELLS_BLOCK)) else f"{fq.CELLS_BLOCK} blocked"), "BVA"),
    ("TC11", "field_quality.assess (specimen)", "specimen = \"gastric\"", "not assessable, reason not_breast",
     lambda: (lambda v: f"{'not assessable' if not v['assessable'] else 'assessable'}, reason {v['reasons'][0]['code']}")(
         fq.assess(GOOD, specimen="gastric")), "EP (non-breast)"),
    ("TC12", "verify_password", "right password, then same text in lower case", "True, then False",
     lambda: (lambda h: f"{verify_password('Correct-Horse-9', h)}, then {verify_password('correct-horse-9', h)}")(
         hash_password("Correct-Horse-9")), "EP (valid / invalid)"),
    ("TC13", "hash_password", "same password hashed twice", "two different hashes (salted)",
     lambda: "two different hashes (salted)" if hash_password("same-password-1") != hash_password("same-password-1")
     else "identical hashes", "EP"),
    ("TC14", "decode_upload", "bytes b\"this is not an image\"", "raises ImageDecodeError",
     lambda: raises(lambda: decode_upload(b"this is not an image"), ImageDecodeError), "EP (invalid input)"),
]


def main():
    rows, passed = [], 0
    for tc, func, inp, expected, actual_fn, tech in CASES:
        actual = actual_fn()
        ok = actual == expected
        passed += ok
        rows.append(f"| {tc} | `{func}` | {inp} | {expected} | {actual} | {'Pass' if ok else 'Fail'} | {tech} |")
    lines = [
        "# Unit test cases (Assignment 2, Q3)",
        "",
        "The cases below are asserted in [`tests/test_assignment_a2.py`](../tests/test_assignment_a2.py) and run by the CI",
        "pipeline on every push. This table is produced by `python scripts/make_a2_test_table.py`, which calls each function",
        "with the input shown and records what it returns.",
        "",
        "| TC ID | Function tested | Input | Expected output | Actual output | Pass/Fail | Technique |",
        "|---|---|---|---|---|---|---|",
        *rows,
        "",
        f"**Result: {passed} of {len(CASES)} test cases passed.**",
        "",
        "## Techniques used",
        "",
        "- **Boundary value analysis (BVA):** TC01 to TC04 test the ASCO/CAP 10 % rule exactly on the boundary and just above it. "
        "TC06 tests the two invalid ends of the open interval (0, 1) for alpha. TC09 and TC10 test the image-size and cell-count "
        "limits of the field-quality gate one below, and exactly at, the limit.",
        "- **Equivalence partitioning (EP):** TC05, TC07, TC08, TC11, TC12, TC13 and TC14 each pick one representative input "
        "from a class of inputs expected to behave alike (no staining, valid alpha, empty input, non-breast specimen, "
        "valid and invalid passwords, non-image bytes).",
        "",
    ]
    out = ROOT / "docs" / "TEST_CASES.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {out}: {passed}/{len(CASES)} passed")
    return 0 if passed == len(CASES) else 1


if __name__ == "__main__":
    raise SystemExit(main())
