"""
run_mcts_experiment.py
Khảo sát ảnh hưởng của c ∈ {0.5, 1.0, 1.4, 2.0} và iterations lên tỷ lệ thắng.
MCTS (X) đấu với Random agent (O) trên 3x3 và 15x15.
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
        # Đổi lượt đi trước theo từng ván
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


def run_experiment():
    c_values = [0.5, 1.0, 1.4, 2.0]
    iteration_list = [50, 100, 200, 500, 1000, 2000]
    n_games = 50
    board_size, win_len = 3, 3   # Thay 15, 5 để test bàn lớn

    data = {}  # {c_val: {iterations: winrate}}

    for c in c_values:
        print(f"\n=== c = {c} ===")
        data[c] = {}
        for iters in iteration_list:
            print(f"  iterations = {iters}:", end="")
            agent = MCTSAgent(iterations=iters, c=c, rollout_fn=random_rollout)
            rate = run_match(agent, n_games=n_games, board_size=board_size, win_len=win_len)
            data[c][iters] = rate

    # Lưu kết quả
    os.makedirs(os.path.join(os.path.dirname(__file__), "results"), exist_ok=True)
    result_path = os.path.join(os.path.dirname(__file__), "results", "mcts_c_experiment.json")
    # JSON keys phải là string
    save_data = {str(c): {str(k): v for k, v in imap.items()} for c, imap in data.items()}
    with open(result_path, "w") as f:
        json.dump(save_data, f, indent=2)
    print(f"\nĐã lưu: {result_path}")

    plot_winrate_vs_iterations(data)


if __name__ == "__main__":
    run_experiment()
