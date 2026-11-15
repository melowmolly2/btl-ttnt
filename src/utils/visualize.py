"""
visualize.py — Vẽ đồ thị kết quả thực nghiệm.
"""
import os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

FIGURES_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "figures")


def plot_winrate_vs_iterations(data: dict[float, dict[int, float]], save: bool = True):
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

    ax.set_xlabel("Số iterations", fontsize=12)
    ax.set_ylabel("Tỷ lệ thắng (%)", fontsize=12)
    ax.set_title("MCTS: Tỷ lệ thắng theo số iterations với các giá trị c khác nhau", fontsize=13)
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()

    if save:
        os.makedirs(FIGURES_DIR, exist_ok=True)
        path = os.path.join(FIGURES_DIR, "winrate_vs_iterations.png")
        fig.savefig(path, dpi=150)
        print(f"Đã lưu: {path}")
    plt.show()
    return fig


def plot_nodes_comparison(minimax_nodes: dict, ab_nodes: dict, save: bool = True):
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
    ax.bar(x - width / 2, mm, width, label="Minimax")
    ax.bar(x + width / 2, ab, width, label="Alpha-Beta")
    ax.set_xticks(x)
    ax.set_xticklabels([f"depth={d}" for d in depths])
    ax.set_ylabel("Số nút duyệt")
    ax.set_title("Minimax vs Alpha-Beta: Số nút cần duyệt")
    ax.legend()
    ax.grid(True, alpha=0.3, axis="y")
    plt.tight_layout()

    if save:
        os.makedirs(FIGURES_DIR, exist_ok=True)
        path = os.path.join(FIGURES_DIR, "nodes_minimax_vs_ab.png")
        fig.savefig(path, dpi=150)
        print(f"Đã lưu: {path}")
    plt.show()
    return fig
