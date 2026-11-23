"""
run_never_lose_experiment.py
Kiểm chứng: MCTS-UCT không bao giờ thua trên Tic-Tac-Toe 3x3.

Đối thủ:
  - Alpha-Beta depth 9 (đủ duyệt hết cây 3x3 -> chơi tối ưu)
  - Random agent (baseline)

Mỗi cấu hình đổi lượt đi trước từng ván; lưu đủ thắng / hòa / thua.
"""
import sys
import os
import json
import random

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.game.board import Board, X, O
from src.mcts.mcts import MCTSAgent
from src.mcts.rollout import random_rollout
from src.minimax.alpha_beta import AlphaBetaAgent
from src.utils.evaluate import evaluate

BOARD_SIZE, WIN_LEN = 3, 3


def random_move(board: Board):
    return random.choice(board.get_legal_moves())


def play_match(mcts: MCTSAgent, opponent, n_games: int) -> dict:
    """MCTS đấu opponent(board)->move; trả về dict wins/draws/losses."""
    wins = draws = losses = 0
    for i in range(n_games):
        board = Board(BOARD_SIZE, WIN_LEN)
        mcts_is_x = (i % 2 == 0)
        while not board.is_terminal:
            if (board.current_player == X) == mcts_is_x:
                move = mcts.get_move(board)
            else:
                move = opponent(board)
            board.make_move(*move)
        mcts_player = X if mcts_is_x else O
        if board.winner == mcts_player:
            wins += 1
        elif board.is_draw:
            draws += 1
        else:
            losses += 1
    return {"wins": wins, "draws": draws, "losses": losses, "games": n_games}


def run_experiment(c_values=(1.0, 1.414), iteration_list=(100, 500, 1000, 2000),
                   n_games=50):
    ab = AlphaBetaAgent(max_depth=9, eval_fn=evaluate)  # depth 9 = hết cây 3x3
    opponents = {
        "alpha_beta_perfect": lambda b: ab.get_move(b),
        "random": random_move,
    }

    results = {}
    for opp_name, opp in opponents.items():
        results[opp_name] = {}
        print(f"\n=== Đối thủ: {opp_name} ({n_games} ván/cấu hình) ===")
        for c in c_values:
            results[opp_name][str(c)] = {}
            for iters in iteration_list:
                agent = MCTSAgent(iterations=iters, c=c, rollout_fn=random_rollout)
                r = play_match(agent, opp, n_games)
                results[opp_name][str(c)][str(iters)] = r
                print(f"  c={c:<5} iters={iters:>5}: "
                      f"W={r['wins']:>3} D={r['draws']:>3} L={r['losses']:>3}")

    out_dir = os.path.join(os.path.dirname(__file__), "results")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "mcts_never_lose_3x3.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\nĐã lưu: {path}")

    total_losses_ab = sum(
        r["losses"]
        for per_c in results["alpha_beta_perfect"].values()
        for r in per_c.values()
    )
    print(f"Tổng số ván THUA trước Alpha-Beta hoàn hảo: {total_losses_ab}")


if __name__ == "__main__":
    run_experiment()
