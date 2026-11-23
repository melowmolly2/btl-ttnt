"""
run_minimax_experiment.py
So sánh số nút duyệt giữa Minimax thuần và Alpha-Beta theo depth.
Chạy trên 2 bàn: 3×3 (đủ depth) và 15×15 (depth nhỏ do branching factor lớn).
"""
import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.game.board import Board
from src.minimax.minimax import MinimaxAgent
from src.minimax.alpha_beta import AlphaBetaAgent
from src.utils.evaluate import evaluate
from src.utils.visualize import plot_nodes_comparison


def make_test_board_3x3():
    """Bàn 3×3 đã đi 2 nước — đủ phức tạp để test."""
    b = Board(size=3, win_len=3)
    b.make_move(1, 1)  # X giữa
    b.make_move(0, 0)  # O góc
    return b


def make_test_board_15x15():
    """Bàn 15×15 đã đi vài nước — trạng thái đầu game thực tế."""
    b = Board(size=15, win_len=5)
    b.make_move(7, 7)   # X trung tâm
    b.make_move(7, 8)   # O cạnh
    b.make_move(8, 7)   # X
    b.make_move(6, 7)   # O
    return b


def run_experiment_for_board(board, depths, label):
    minimax_nodes = {}
    ab_nodes = {}

    print(f"\n{'='*60}")
    print(f"  BÀN {label}")
    print(f"{'='*60}")

    for d in depths:
        mm = MinimaxAgent(max_depth=d, eval_fn=evaluate)
        ab = AlphaBetaAgent(max_depth=d, eval_fn=evaluate)

        mm.get_move(board)
        ab.get_move(board)

        minimax_nodes[d] = mm.nodes_visited
        ab_nodes[d] = ab.nodes_visited

        reduction = (1 - ab.nodes_visited / mm.nodes_visited) * 100
        print(f"  Depth {d}: Minimax={mm.nodes_visited:>8} nút | "
              f"Alpha-Beta={ab.nodes_visited:>8} nút | Giảm {reduction:.1f}%")

    return minimax_nodes, ab_nodes


def run_experiment():
    results_dir = os.path.join(os.path.dirname(__file__), "results")
    os.makedirs(results_dir, exist_ok=True)

    configs = [
        {
            "board":  make_test_board_3x3(),
            "depths": (1, 2, 3, 4),
            "label":  "3x3",
        },
        {
            "board":  make_test_board_15x15(),
            "depths": (1, 2, 3),   # depth cao hơn quá chậm trên bàn 15×15
            "label":  "15x15",
        },
    ]

    all_minimax = {}
    all_ab = {}

    for cfg in configs:
        mm_nodes, ab_nodes = run_experiment_for_board(
            board=cfg["board"],
            depths=cfg["depths"],
            label=cfg["label"],
        )

        # Lưu từng bàn riêng
        path = os.path.join(results_dir, f"minimax_vs_ab_{cfg['label']}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"minimax": mm_nodes, "alpha_beta": ab_nodes}, f, indent=2)
        print(f"  Đã lưu: {path}")

        all_minimax[cfg["label"]] = mm_nodes
        all_ab[cfg["label"]] = ab_nodes

    # Vẽ đồ thị cho từng bàn (lưu file riêng, không ghi đè)
    for cfg in configs:
        lbl = cfg["label"]
        print(f"\n  Vẽ đồ thị bàn {lbl}...")
        plot_nodes_comparison(
            all_minimax[lbl],
            all_ab[lbl],
            filename=f"nodes_minimax_vs_ab_{lbl}.png",
            title_suffix=lbl,
        )


if __name__ == "__main__":
    run_experiment()
