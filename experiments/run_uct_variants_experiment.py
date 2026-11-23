"""
run_uct_variants_experiment.py
So sánh các biến thể công thức UCT và cải tiến Progressive Bias:
  - standard         : W/N + c * sqrt(ln(N_p) / N)
  - no_sqrt          : W/N + c * (ln(N_p) / N)
  - no_ln            : W/N + c * sqrt(N_p / N)
  - linear           : W/N + c * (N_p / N)
  - progressive_bias : W/N + c * sqrt(ln(N_p) / N) + H / (N + 1)
"""
import sys
import os
import json
import time
import random
from concurrent.futures import ProcessPoolExecutor

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.game.board import Board, X, O
from src.mcts.mcts import MCTSAgent
from src.mcts.node import UCT_VARIANTS
from src.mcts.rollout import random_rollout
from src.minimax.alpha_beta import AlphaBetaAgent
from src.utils.evaluate import evaluate
from src.utils.visualize import plot_uct_variants


def _play_one_game(args) -> tuple[int, float]:
    game_idx, board_size, win_len, iters, c, variant, opp_kind, seed = args
    random.seed(seed)
    agent = MCTSAgent(
        iterations=iters,
        c=c,
        rollout_fn=random_rollout,
        uct_variant=variant,
    )
    ab = AlphaBetaAgent(max_depth=9, eval_fn=evaluate) if opp_kind == "ab" else None

    board = Board(board_size, win_len)
    mcts_is_x = (game_idx % 2 == 0)
    move_times = []

    while not board.is_terminal:
        if (board.current_player == X) == mcts_is_x:
            t0 = time.perf_counter()
            move = agent.get_move(board)
            move_times.append((time.perf_counter() - t0) * 1000.0)
        else:
            if ab is not None:
                move = ab.get_move(board)
            else:
                move = random.choice(board.get_legal_moves())
        board.make_move(*move)

    mp = X if mcts_is_x else O
    if board.winner == mp:
        outcome = 1
    elif board.is_draw:
        outcome = 0
    else:
        outcome = -1
    avg_ms = sum(move_times) / len(move_times) if move_times else 0.0
    return outcome, avg_ms


def run_suite(
    board_size: int,
    win_len: int,
    iters: int,
    c: float,
    opp_kind: str,
    n_games: int,
    executor: ProcessPoolExecutor,
    base_seed: int = 2026,
) -> dict:
    print(f"\n=== {board_size}x{board_size} vs {opp_kind} | iters={iters}, c={c}, {n_games} ván ===")
    results = {}
    for variant in UCT_VARIANTS:
        tasks = [
            (i, board_size, win_len, iters, c, variant, opp_kind, base_seed + i)
            for i in range(n_games)
        ]
        outcomes = list(executor.map(_play_one_game, tasks))
        wins = sum(1 for o, _ in outcomes if o == 1)
        draws = sum(1 for o, _ in outcomes if o == 0)
        losses = sum(1 for o, _ in outcomes if o == -1)
        avg_ms = sum(ms for _, ms in outcomes) / len(outcomes)
        winrate = wins / n_games * 100.0
        non_loss = (wins + draws) / n_games * 100.0
        results[variant] = {
            "wins": wins,
            "draws": draws,
            "losses": losses,
            "games": n_games,
            "winrate": round(winrate, 2),
            "non_loss_rate": round(non_loss, 2),
            "avg_move_ms": round(avg_ms, 2),
        }
        print(
            f"  {variant:<18}: W={wins:>3} D={draws:>3} L={losses:>3} "
            f"| Win={winrate:5.1f}% | NonLoss={non_loss:5.1f}% | {avg_ms:6.1f} ms/nước"
        )
    return results


def run_experiment():
    workers = max(1, (os.cpu_count() or 4) - 2)
    results_dir = os.path.join(os.path.dirname(__file__), "results")
    os.makedirs(results_dir, exist_ok=True)

    with ProcessPoolExecutor(max_workers=workers) as executor:
        res_3x3_ab = run_suite(3, 3, iters=300, c=1.0, opp_kind="ab", n_games=100, executor=executor)
        res_3x3_rand = run_suite(3, 3, iters=200, c=1.0, opp_kind="random", n_games=100, executor=executor)
        res_15x15_rand = run_suite(15, 5, iters=150, c=1.0, opp_kind="random", n_games=50, executor=executor)

    out = {
        "3x3_vs_ab_300": res_3x3_ab,
        "3x3_vs_random_200": res_3x3_rand,
        "15x15_vs_random_150": res_15x15_rand,
    }
    path = os.path.join(results_dir, "uct_variants.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(f"\nĐã lưu: {path}")

    plot_uct_variants(res_3x3_ab, res_15x15_rand, save=True)


if __name__ == "__main__":
    run_experiment()
