"""Figure 3.2: the reproducibility artefacts, as text panels: an excerpt of the MacBook per-device
configuration file (left) and the provenance manifest the harness writes for a run (right).
Both are read from the real files so the figure cannot drift from the artefact directory."""
import os, io, json
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
cfg = io.open(os.path.join(ROOT, "proposal-dev", "pilot", "configs", "mac.yaml"), encoding="utf-8").read().split("\n")
keep = ["device:", "llama_cpp_tag:", "server_bin:", "n_ctx:", "seed:", "temperature:", "max_tokens:", "dataset:", "  - name:", "    ngl:"]
left = [ln.split("#")[0].rstrip() for ln in cfg if any(ln.startswith(k) for k in keep)]
left = left[:10]
man = json.load(io.open(os.path.join(ROOT, "proposal-dev", "pilot", "results", "mac", "manifest.json"), encoding="utf-8"))
order = ["device", "timestamp", "os", "processor", "cpu_count", "ram_gb", "python", "llama_cpp_tag", "config_file", "condition", "openbook_artefact_sha256"]
right = ['"%s": %s' % (k, json.dumps(man[k])) for k in order if k in man]

fig, axes = plt.subplots(1, 2, figsize=(10.5, 3.6))
for ax, title, lines in ((axes[0], "configs/mac.yaml (excerpt)", left), (axes[1], "results/mac/manifest.json", right)):
    ax.set_axis_off()
    ax.text(0.02, 0.97, title, transform=ax.transAxes, fontsize=10.5, fontweight="bold", va="top", family="DejaVu Sans")
    ax.text(0.02, 0.86, "\n".join(lines), transform=ax.transAxes, fontsize=8.6, va="top", family="DejaVu Sans Mono", linespacing=1.35)
    ax.add_patch(plt.Rectangle((0.0, 0.0), 1.0, 1.0, transform=ax.transAxes, fill=False, lw=0.8, color="0.4"))
fig.text(0.5, 0.015, "Same script on every tier; only the configuration file differs. Every run writes the manifest beside its results.",
         ha="center", fontsize=9, style="italic")
plt.tight_layout(rect=(0, 0.05, 1, 1))
out = os.path.join(HERE, "figures", "fig3-2_config.png"); fig.savefig(out, dpi=200); print("wrote", out)
