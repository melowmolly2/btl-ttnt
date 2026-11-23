"""
visualize.py — Vẽ đồ thị kết quả thực nghiệm.
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

FIGURES_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "figures")


def plot_winrate_vs_iterations(
    data: dict[float, dict[int, float]],
    save: bool = True,
    filename: str = "winrate_vs_iterations.png",
    title_suffix: str = "",
    show: bool = False,
):
    """
    Vẽ đồ thị tỷ lệ thắng theo số iterations với nhiều giá trị c.

    Parameters
    ----------
    data : {c_value: {iterations: winrate}}
    """
    fig, ax = plt.subplots(figsize=(9, 5))
    for c_val, iter_map in sorted(data.items()):
        iters = sorted(iter_map.keys())
        rates = [iter_map[i] for i in iters]
        ax.plot(iters, rates, marker="o", label=f"c = {c_val}")

    ax.set_xlabel("Iterations", fontsize=12)
    ax.set_ylabel("Win Rate (%)", fontsize=12)
    title = "MCTS-UCT: Win Rate vs Iterations across Exploration Constants c"
    if title_suffix:
        title += f" ({title_suffix})"
    ax.set_title(title, fontsize=12)
    ax.set_ylim(0, 105)
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()

    if save:
        os.makedirs(FIGURES_DIR, exist_ok=True)
        path = os.path.join(FIGURES_DIR, filename)
        fig.savefig(path, dpi=150)
        print(f"Đã lưu: {path}")
    if show:
        plt.show()
    else:
        plt.close(fig)
    return fig


def plot_nodes_comparison(
    minimax_nodes: dict,
    ab_nodes: dict,
    save: bool = True,
    filename: str = "nodes_minimax_vs_ab.png",
    title_suffix: str = "",
    show: bool = False,
):
    """
    So sánh số nút duyệt: Minimax vs Alpha-Beta theo depth.

    Parameters
    ----------
    minimax_nodes : {depth: nodes}
    ab_nodes      : {depth: nodes}
    """
    depths = sorted(set(minimax_nodes) | set(ab_nodes))
    mm = [minimax_nodes.get(d, 0) for d in depths]
    ab = [ab_nodes.get(d, 0) for d in depths]

    x = np.arange(len(depths))
    width = 0.35
    fig, ax = plt.subplots(figsize=(8, 5))
    b1 = ax.bar(x - width / 2, mm, width, label="Minimax")
    b2 = ax.bar(x + width / 2, ab, width, label="Alpha-Beta")
    ax.bar_label(b1, fmt="%d", padding=2, fontsize=8)
    ax.bar_label(b2, fmt="%d", padding=2, fontsize=8)
    ax.set_xticks(x)
    ax.set_xticklabels([f"depth={d}" for d in depths])
    ax.set_ylabel("Nodes Visited")
    title = "Minimax vs Alpha-Beta: Nodes Visited"
    if title_suffix:
        title += f" ({title_suffix})"
    ax.set_title(title)
    ax.legend()
    ax.grid(True, alpha=0.3, axis="y")
    plt.tight_layout()

    if save:
        os.makedirs(FIGURES_DIR, exist_ok=True)
        path = os.path.join(FIGURES_DIR, filename)
        fig.savefig(path, dpi=150)
        print(f"Đã lưu: {path}")
    if show:
        plt.show()
    else:
        plt.close(fig)
    return fig


def plot_uct_variants(
    results_3x3_ab: dict,
    results_15x15_rand: dict,
    save: bool = True,
    filename: str = "uct_variants_comparison.png",
    show: bool = False,
):
    """
    Vẽ biểu đồ so sánh các biến thể UCT:
      - Trái: Tỷ lệ không thua (Win+Draw %) trước Alpha-Beta tối ưu trên 3x3
      - Phải: Tỷ lệ thắng (%) trước Random trên 15x15
    """
    variants = list(results_3x3_ab.keys())
    labels = {
        "standard": "Standard\nUCT",
        "no_sqrt": "No sqrt\n(ln Np / N)",
        "no_ln": "No ln\n(sqrt(Np/N))",
        "linear": "Linear\n(Np / N)",
        "progressive_bias": "Progressive\nBias (Ours)",
    }
    x_labels = [labels.get(v, v) for v in variants]
    non_loss_3x3 = [
        (results_3x3_ab[v]["wins"] + results_3x3_ab[v]["draws"])
        / results_3x3_ab[v]["games"] * 100.0
        for v in variants
    ]
    win_15x15 = [results_15x15_rand[v]["winrate"] for v in variants]

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    colors = ["#4c72b0", "#dd8452", "#c44e52", "#8172b3", "#55a868"]

    b0 = axes[0].bar(x_labels, non_loss_3x3, color=colors)
    axes[0].bar_label(b0, fmt="%.1f%%", padding=2, fontsize=8)
    axes[0].set_ylim(0, 112)
    axes[0].set_ylabel("Non-Loss Rate (%)")
    axes[0].set_title("3x3 vs Optimal Alpha-Beta (300 iters)")
    axes[0].grid(True, alpha=0.3, axis="y")

    b1 = axes[1].bar(x_labels, win_15x15, color=colors)
    axes[1].bar_label(b1, fmt="%.1f%%", padding=2, fontsize=8)
    axes[1].set_ylim(0, 112)
    axes[1].set_ylabel("Win Rate (%)")
    axes[1].set_title("15x15 vs Random (150 iters)")
    axes[1].grid(True, alpha=0.3, axis="y")

    plt.tight_layout()
    if save:
        os.makedirs(FIGURES_DIR, exist_ok=True)
        path = os.path.join(FIGURES_DIR, filename)
        fig.savefig(path, dpi=150)
        print(f"Đã lưu: {path}")
    if show:
        plt.show()
    else:
        plt.close(fig)
    return fig
