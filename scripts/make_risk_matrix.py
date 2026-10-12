"""Draw the risk matrix (likelihood against impact) into docs/risk_matrix.png.

The three risks and their ratings are the ones in docs/PROJECT_PLAN.md.

    python scripts/make_risk_matrix.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

LEVELS = {"Low": 1, "Medium": 2, "High": 3}
# id, short name, likelihood, impact
RISKS = [
    ("R1", "Accuracy falls at the\ncollege's scanner", "High", "High"),
    ("R2", "Slides or pathologist\ntime arrive late", "Medium", "High"),
    ("R3", "Patient data exposed\nduring the pilot", "Low", "High"),
]


def colour(score: int) -> str:
    return "#e9a39b" if score >= 6 else ("#f3d98b" if score >= 3 else "#b9dcb2")


def main():
    fig, ax = plt.subplots(figsize=(7.6, 5.0))
    for like in (1, 2, 3):
        for imp in (1, 2, 3):
            ax.add_patch(Rectangle((like - 0.5, imp - 0.5), 1, 1, facecolor=colour(like * imp), edgecolor="white", linewidth=2))
            ax.text(like + 0.42, imp - 0.42, str(like * imp), ha="right", va="bottom", fontsize=8, color="#555")
    for rid, name, like, imp in RISKS:
        x, y = LEVELS[like], LEVELS[imp]
        ax.text(x, y + 0.08, rid, ha="center", va="center", fontsize=15, fontweight="bold", color="#222")
        ax.text(x, y - 0.18, name, ha="center", va="center", fontsize=7.5, color="#222")
    ax.set_xlim(0.5, 3.5)
    ax.set_ylim(0.5, 3.5)
    ax.set_xticks([1, 2, 3])
    ax.set_xticklabels(["Low", "Medium", "High"])
    ax.set_yticks([1, 2, 3])
    ax.set_yticklabels(["Low", "Medium", "High"])
    ax.set_xlabel("Likelihood")
    ax.set_ylabel("Impact")
    ax.set_title("Risk matrix: score = likelihood x impact (1 to 9)", fontsize=11, fontweight="bold", loc="left")
    for side in ("top", "right", "left", "bottom"):
        ax.spines[side].set_visible(False)
    ax.tick_params(length=0)
    fig.tight_layout()
    out = Path(__file__).resolve().parents[1] / "docs" / "risk_matrix.png"
    fig.savefig(out, dpi=160)
    print("wrote", out)


if __name__ == "__main__":
    main()
