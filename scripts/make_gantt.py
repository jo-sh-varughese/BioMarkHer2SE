"""Draw the Gantt chart of the remaining work into docs/gantt.png.

The task list below is the single source for the chart; docs/PROJECT_PLAN.md
repeats it as a table and as a Mermaid chart.

    python scripts/make_gantt.py
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

TODAY = date(2026, 10, 13)

# (task, start, end, owner, colour)
TASKS = [
    ("1. Pilot data request and image requirements sheet", date(2026, 10, 14), date(2026, 10, 21), "Nadeema", "#2f6f9f"),
    ("2. Security review before hospital deployment", date(2026, 10, 14), date(2026, 11, 6), "Aiswarya", "#8a5a9f"),
    ("3. Adaptation curve on the college's TIFF images", date(2026, 10, 22), date(2026, 11, 5), "Johan", "#3a8f5f"),
    ("4. Shadow-mode pilot on 5 to 10 slides", date(2026, 10, 22), date(2026, 11, 10), "Johan, Nadeema", "#3a8f5f"),
    ("5. Real pathologist reviews and agreement analysis", date(2026, 11, 6), date(2026, 11, 20), "Rishika, Aiswarya", "#c07a2a"),
    ("6. Final report update and viva preparation", date(2026, 11, 11), date(2026, 11, 28), "All", "#2f6f9f"),
    ("7. Release v1.0: tagged Docker image and handover", date(2026, 11, 21), date(2026, 11, 30), "Rishika", "#b23a3a"),
]


def main():
    fig, ax = plt.subplots(figsize=(11, 4.6))
    for i, (name, start, end, owner, colour) in enumerate(TASKS):
        y = len(TASKS) - 1 - i
        width = (end - start).days + 1
        ax.barh(y, width, left=mdates.date2num(start), height=0.55, color=colour, edgecolor="white")
        ax.text(mdates.date2num(start) + width / 2, y, owner, ha="center", va="center", color="white", fontsize=8.5, fontweight="bold")
    ax.set_yticks(range(len(TASKS)))
    ax.set_yticklabels([t[0] for t in TASKS][::-1], fontsize=9)
    ax.axvline(mdates.date2num(TODAY), color="#b23a3a", linestyle="--", linewidth=1.2)
    ax.set_ylim(-0.6, len(TASKS) - 0.1)
    ax.text(mdates.date2num(TODAY) + 0.4, len(TASKS) - 0.45, "today (13 Oct)", color="#b23a3a", fontsize=8.5, va="center")
    ax.xaxis_date()
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.MO))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
    ax.set_xlim(mdates.date2num(date(2026, 10, 12)), mdates.date2num(date(2026, 12, 2)))
    ax.grid(axis="x", alpha=0.3)
    ax.set_title("BioMarkHER2: remaining work, 14 October to 30 November 2026", fontsize=11, fontweight="bold", loc="left")
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    fig.tight_layout()
    out = Path(__file__).resolve().parents[1] / "docs" / "gantt.png"
    fig.savefig(out, dpi=160)
    print("wrote", out)


if __name__ == "__main__":
    main()
