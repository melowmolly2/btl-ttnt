"""
run_root_stats.py
Sinh bảng W, N, W/N tại nút gốc cho report (mục 5.4).

Hai tình huống:
  - 3x3: X đã đi giữa, O đi góc (cùng thế cờ dùng trong thực nghiệm minimax)
  - 15x15: vài nước đầu
"""
import sys
import os
import json
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.game.board import Board
from src.mcts.mcts import MCTSAgent
from src.mcts.rollout import random_rollout


def board_3x3():
    b = Board(3, 3)
    b.make_move(1, 1)  # X giữa
    b.make_move(0, 0)  # O góc
    return b


def board_15x15():
    b = Board(15, 5)
    for mv in [(7, 7), (7, 8), (8, 7), (6, 7)]:
        b.make_move(*mv)
    return b


def run(top_k=8, iterations=1000, c=1.0):
    scenarios = {"3x3": board_3x3(), "15x15": board_15x15()}
    results = {}
    for name, board in scenarios.items():
        agent = MCTSAgent(iterations=iterations, c=c, rollout_fn=random_rollout)
        stats = agent.get_root_stats(board)[:top_k]
        results[name] = {"iterations": iterations, "c": c, "stats": [
            {"move": list(s["move"]), "W": s["W"], "N": s["N"], "W/N": round(s["W/N"], 4)}
            for s in stats
        ]}
        print(f"\n=== {name} (iterations={iterations}, c={c}) ===")
        print(f"{'Move':<10}{'W':>9}{'N':>7}{'W/N':>8}")
        for s in stats:
            print(f"{str(s['move']):<10}{s['W']:>9.1f}{s['N']:>7}{s['W/N']:>8.3f}")

    out_dir = os.path.join(os.path.dirname(__file__), "results")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "mcts_root_stats.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\nĐã lưu: {path}")


if __name__ == "__main__":
    run()
