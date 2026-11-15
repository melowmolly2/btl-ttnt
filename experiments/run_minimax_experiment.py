"""
run_minimax_experiment.py
So sánh số nút duyệt giữa Minimax thuần và Alpha-Beta theo depth.
"""
import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.game.board import Board, X, O
from src.minimax.minimax import MinimaxAgent
from src.minimax.alpha_beta import AlphaBetaAgent
from src.utils.evaluate import evaluate
from src.utils.visualize import plot_nodes_comparison

# Trạng thái bàn cờ mẫu để test (3x3, đầu game)
def make_test_board_3x3():
    b = Board(size=3, win_len=3)
    b.make_move(1, 1)  # X giữa
    b.make_move(0, 0)  # O góc
    return b


def run_experiment(depths=(1, 2, 3, 4)):
    minimax_nodes = {}
    ab_nodes = {}

    board = make_test_board_3x3()

    for d in depths:
        mm = MinimaxAgent(max_depth=d, eval_fn=evaluate)
        ab = AlphaBetaAgent(max_depth=d, eval_fn=evaluate)

        mm.get_move(board)
        ab.get_move(board)

        minimax_nodes[d] = mm.nodes_visited
        ab_nodes[d] = ab.nodes_visited

        print(f"Depth {d}: Minimax={mm.nodes_visited} nút | Alpha-Beta={ab.nodes_visited} nút "
              f"| Giảm {(1 - ab.nodes_visited/mm.nodes_visited)*100:.1f}%")

    # Lưu kết quả
    os.makedirs(os.path.join(os.path.dirname(__file__), "results"), exist_ok=True)
    result_path = os.path.join(os.path.dirname(__file__), "results", "minimax_vs_ab.json")
    with open(result_path, "w") as f:
        json.dump({"minimax": minimax_nodes, "alpha_beta": ab_nodes}, f, indent=2)
    print(f"\nĐã lưu kết quả: {result_path}")

    # Vẽ đồ thị
    plot_nodes_comparison(minimax_nodes, ab_nodes)


if __name__ == "__main__":
    run_experiment()
