"""Figure 3.3: the three verdict classes of section 3.3.6, drawn for a lay reader. A rung's paired 95%
interval on the drop in pass@1 (F16 minus rung, percentage points) is judged against the five-point margin.
The three example intervals are real cells from Table 4.1: Qwen Q8_0 (within), Qwen Q3_K_M (inconclusive),
Qwen Q2_K (collapsed)."""
import os
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
cells = [("within margin\n(Qwen Q8_0)", -0.6, -3.0, 1.2), ("inconclusive\n(Qwen Q3_K_M)", 2.4, -3.0, 7.9), ("collapsed\n(Qwen Q2_K)", 22.6, 14.6, 30.5)]
fig, ax = plt.subplots(figsize=(9, 3.3))
ax.axvspan(-6, 5, color="0.92", zorder=0); ax.axvline(5, color="black", lw=1.4)
ax.text(5.3, 2.75, "registered margin: five points below F16", fontsize=9, va="center")
ax.text(-5.7, -0.35, "within five points of F16", fontsize=9, va="center", color="0.3")
for i, (label, est, lo, hi) in enumerate(cells):
    y = 2 - i
    ax.plot([lo, hi], [y, y], color="black", lw=2.2, solid_capstyle="butt", zorder=3)
    ax.plot([lo, lo], [y - 0.12, y + 0.12], color="black", lw=1.5); ax.plot([hi, hi], [y - 0.12, y + 0.12], color="black", lw=1.5)
    ax.plot(est, y, marker="o", color="black", ms=7, zorder=4)
    ax.text(-7.0, y, label, ha="right", va="center", fontsize=9.5)
    ax.text(hi + 0.6, y, "%+.1f [%+.1f, %+.1f]" % (est, lo, hi), va="center", fontsize=8.8, family="DejaVu Sans Mono")
ax.set_xlim(-12.5, 36); ax.set_ylim(-0.6, 3.1); ax.set_yticks([])
ax.set_xlabel("drop in pass@1 relative to F16 (percentage points; paired bootstrap 95% interval, point estimate as a dot)")
for s in ("top", "right", "left"): ax.spines[s].set_visible(False)
ax.set_title("A rung is 'within margin' if its whole interval lies left of the line, 'collapsed' if wholly right of it, 'inconclusive' if it straddles it", fontsize=9.5)
plt.tight_layout()
out = os.path.join(HERE, "figures", "fig3-3_verdict.png"); fig.savefig(out, dpi=200); print("wrote", out)
