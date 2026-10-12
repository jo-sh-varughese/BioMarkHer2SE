"""Unit tests for the Software Engineering assignment (A2, Q3).

Each test targets one important function of BioMarkHER2. The technique used for
each case is named in its docstring: equivalence partitioning (EP) or boundary
value analysis (BVA). The same cases are tabulated in docs/TEST_CASES.md.

Run:  pytest tests/test_assignment_a2.py -v
"""

from __future__ import annotations

import numpy as np
import pytest

from app import field_quality as fq
from app.auth import hash_password, verify_password
from app.image_io import ImageDecodeError, decode_upload
from evaluation.cap_mapping import map_to_cap_category
from evaluation.conformal import weighted_quantile
from tests.test_field_quality import _her2_like

STRONG, MODERATE, WEAK, NEG = "strong (3+)", "moderate (2+)", "weak (1+)", "negative"


def _pct(strong=0.0, moderate=0.0, weak=0.0):
    return {STRONG: strong, MODERATE: moderate, WEAK: weak, NEG: 100.0 - strong - moderate - weak}


# --------------------------------------------------------------------------- map_to_cap_category
# ASCO/CAP: 3+ needs MORE than 10% strong staining; 1+ needs MORE than 10% weak-or-above.


def test_tc01_cap_strong_exactly_at_threshold_is_not_3plus():
    """TC01 (BVA, on the boundary): strong = 10.0% is not > 10%, so it falls to 2+."""
    assert map_to_cap_category(_pct(strong=10.0)).category == "2+"


def test_tc02_cap_strong_just_above_threshold_is_3plus():
    """TC02 (BVA, just above the boundary): strong = 10.01% is > 10%, so 3+."""
    assert map_to_cap_category(_pct(strong=10.01)).category == "3+"


def test_tc03_cap_weak_exactly_at_threshold_is_negative():
    """TC03 (BVA, on the boundary): weak = 10.0% is not > 10%, so score 0."""
    assert map_to_cap_category(_pct(weak=10.0)).category == "0"


def test_tc04_cap_weak_just_above_threshold_is_1plus():
    """TC04 (BVA, just above the boundary): weak = 10.01% is > 10%, so 1+."""
    assert map_to_cap_category(_pct(weak=10.01)).category == "1+"


def test_tc05_cap_no_staining_is_zero():
    """TC05 (EP, class 'no staining'): all stain classes at 0% gives score 0."""
    assert map_to_cap_category(_pct()).category == "0"


# --------------------------------------------------------------------------- weighted_quantile (conformal)


@pytest.mark.parametrize("alpha", [0.0, 1.0])
def test_tc06_quantile_rejects_alpha_on_the_open_interval_boundary(alpha):
    """TC06 (BVA, invalid boundary): alpha must lie strictly inside (0, 1)."""
    with pytest.raises(ValueError):
        weighted_quantile(np.linspace(0.1, 1.0, 10), alpha)


def test_tc07_quantile_of_ten_scores_matches_the_conformal_formula():
    """TC07 (EP, valid alpha): n=10 scores 0.1..1.0, alpha=0.5 gives the ceil((n+1)(1-alpha))/n = 6th score, 0.6."""
    assert weighted_quantile(np.linspace(0.1, 1.0, 10), 0.5) == pytest.approx(0.6)


def test_tc08_quantile_with_no_calibration_scores_is_refused():
    """TC08 (EP, invalid partition): an empty calibration set cannot give a quantile."""
    with pytest.raises(ValueError):
        weighted_quantile(np.array([]), 0.1)


# --------------------------------------------------------------------------- field quality gate


@pytest.fixture(scope="module")
def good_field_metrics():
    return fq.measure_image(_her2_like(512))


def test_tc09_quality_gate_minimum_side_boundary(good_field_metrics):
    """TC09 (BVA): a side of MIN_SIDE_PX - 1 is blocked as too small; MIN_SIDE_PX is accepted."""
    small = fq.assess({**good_field_metrics, "width": fq.MIN_SIDE_PX - 1, "height": 512})
    exact = fq.assess({**good_field_metrics, "width": fq.MIN_SIDE_PX, "height": 512})
    assert not small["assessable"] and "too_small" in {r["code"] for r in small["reasons"]}
    assert "too_small" not in {r["code"] for r in exact["reasons"]}


def test_tc10_quality_gate_cell_count_boundary(good_field_metrics):
    """TC10 (BVA): fewer than CELLS_BLOCK measured cells is blocked; exactly CELLS_BLOCK is not."""
    few = fq.assess(good_field_metrics, tissue_percent=60, n_cells=fq.CELLS_BLOCK - 1)
    enough = fq.assess(good_field_metrics, tissue_percent=60, n_cells=fq.CELLS_BLOCK)
    assert "few_cells" in {r["code"] for r in few["reasons"] if r["level"] == fq.BLOCK}
    assert "few_cells" not in {r["code"] for r in enough["reasons"] if r["level"] == fq.BLOCK}


def test_tc11_quality_gate_refuses_non_breast_specimen(good_field_metrics):
    """TC11 (EP, class 'non-breast specimen'): breast ASCO/CAP rules do not apply to gastric tissue."""
    verdict = fq.assess(good_field_metrics, specimen="gastric")
    assert not verdict["assessable"] and verdict["reasons"][0]["code"] == "not_breast"


# --------------------------------------------------------------------------- authentication / input decoding


def test_tc12_password_hash_accepts_right_and_rejects_wrong_password():
    """TC12 (EP, valid and invalid password classes): only the original password verifies."""
    stored = hash_password("Correct-Horse-9")
    assert verify_password("Correct-Horse-9", stored)
    assert not verify_password("correct-horse-9", stored)


def test_tc13_password_hash_is_salted():
    """TC13 (EP): hashing the same password twice gives different stored values."""
    assert hash_password("same-password-1") != hash_password("same-password-1")


def test_tc14_decode_upload_rejects_bytes_that_are_not_an_image():
    """TC14 (EP, invalid input class): arbitrary bytes raise ImageDecodeError, never a crash or a fake image."""
    with pytest.raises(ImageDecodeError):
        decode_upload(b"this is not an image")
