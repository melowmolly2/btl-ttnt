"""
run_mcts_experiment.py
Khảo sát ảnh hưởng của c ∈ {0.5, 1.0, 1.4, 2.0} và iterations lên tỷ lệ thắng.
MCTS đấu với Random agent trên 2 bàn: 3×3 (win=3) và 15×15 (win=5).
"""
import sys
import os
import json
import random
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.game.board import Board, X, O
from src.mcts.mcts import MCTSAgent
from src.mcts.rollout import random_rollout
from src.utils.visualize import plot_winrate_vs_iterations


def random_agent(board: Board):
    moves = board.get_legal_moves()
    return random.choice(moves)


def run_match(mcts: MCTSAgent, n_games: int = 50, board_size: int = 3, win_len: int = 3) -> float:
    """Chạy n_games ván, trả về tỷ lệ thắng của MCTS (%)."""
    wins = draws = losses = 0
    for i in range(n_games):
        board = Board(board_size, win_len)
        # Đổi lượt đi trước theo từng ván để công bằng
        mcts_is_x = (i % 2 == 0)
        while not board.is_terminal:
            if (board.current_player == X) == mcts_is_x:
                move = mcts.get_move(board)
            else:
                move = random_agent(board)
            board.make_move(*move)
        mcts_player = X if mcts_is_x else O
        if board.winner == mcts_player:
            wins += 1
        elif board.is_draw:
            draws += 1
        else:
            losses += 1

    winrate = wins / n_games * 100
    print(f"    Thắng: {wins} | Hòa: {draws} | Thua: {losses} | Winrate: {winrate:.1f}%")
    return winrate


def run_experiment_for_board(board_size: int, win_len: int, n_games: int,
                              c_values: list, iteration_list: list) -> dict:
    """Chạy thực nghiệm cho một cấu hình bàn cờ, trả về data {c: {iters: winrate}}."""
    print(f"\n{'='*60}")
    print(f"  BÀN {board_size}×{board_size} — cần {win_len} quân thẳng hàng")
    print(f"  Số ván mỗi cấu hình: {n_games}")
    print(f"{'='*60}")

    data = {}
    for c in c_values:
        print(f"\n  c = {c}")
        data[c] = {}
        for iters in iteration_list:
            print(f"    iterations = {iters:>5}:", end="  ")
            agent = MCTSAgent(iterations=iters, c=c, rollout_fn=random_rollout)
            rate = run_match(agent, n_games=n_games, board_size=board_size, win_len=win_len)
            data[c][iters] = rate

    return data


def run_experiment():
    c_values      = [0.5, 1.0, 1.4, 2.0]

    # Bàn 3×3: nhiều ván hơn vì mỗi ván nhanh
    # Bàn 15×15: ít ván hơn vì mỗi ván chậm hơn nhiều
    configs = [
        # {"board_size": 3,  "win_len": 3, "n_games": 200,
        #  "iteration_list": [50, 100, 200, 500, 1000, 2000],
        #  "label": "3x3"},   # đã có kết quả, bỏ comment nếu muốn chạy lại
        {"board_size": 15, "win_len": 5, "n_games": 20,
         "iteration_list": [100, 200, 500],
         "label": "15x15"},
    ]

    results_dir = os.path.join(os.path.dirname(__file__), "results")
    os.makedirs(results_dir, exist_ok=True)

    for cfg in configs:
        data = run_experiment_for_board(
            board_size=cfg["board_size"],
            win_len=cfg["win_len"],
            n_games=cfg["n_games"],
            c_values=c_values,
            iteration_list=cfg["iteration_list"],
        )

        # Lưu JSON (key phải là string)
        save_data = {str(c): {str(k): v for k, v in imap.items()} for c, imap in data.items()}
        fname = f"mcts_c_experiment_{cfg['label']}.json"
        result_path = os.path.join(results_dir, fname)
        with open(result_path, "w", encoding="utf-8") as f:
            json.dump(save_data, f, indent=2)
        print(f"\n  Đã lưu: {result_path}")

        # Vẽ đồ thị cho bàn này
        print(f"  Vẽ đồ thị bàn {cfg['label']}...")
        plot_winrate_vs_iterations(data, save=True)


if __name__ == "__main__":
    run_experiment()
