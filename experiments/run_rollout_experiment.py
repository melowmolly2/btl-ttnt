"""
run_rollout_experiment.py
So sánh rollout ngẫu nhiên vs rollout heuristic trên 3×3 và 15×15.
Chạy song song các ván bằng ProcessPoolExecutor để đạt >= 50 ván/cấu hình.
"""
import sys
import os
import json
import math
import time
import random
from concurrent.futures import ProcessPoolExecutor

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.game.board import Board, X, O
from src.mcts.mcts import MCTSAgent
from src.mcts.rollout import random_rollout, heuristic_rollout


def _play_one_game(args) -> tuple[int, float]:
    game_idx, board_size, win_len, iters, use_heuristic, seed = args
    random.seed(seed)
    rollout_fn = heuristic_rollout if use_heuristic else random_rollout
    agent = MCTSAgent(iterations=iters, c=math.sqrt(2), rollout_fn=rollout_fn)
    board = Board(board_size, win_len)
    mcts_is_x = (game_idx % 2 == 0)

    move_times = []
    while not board.is_terminal:
        if (board.current_player == X) == mcts_is_x:
            t0 = time.perf_counter()
            move = agent.get_move(board)
            move_times.append((time.perf_counter() - t0) * 1000.0)
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


def run_match(
    use_heuristic: bool,
    iterations: int,
    n_games: int,
    board_size: int,
    win_len: int,
    executor: ProcessPoolExecutor,
    base_seed: int = 1000,
) -> dict:
    tasks = [
        (i, board_size, win_len, iterations, use_heuristic, base_seed + i)
        for i in range(n_games)
    ]
    outcomes = list(executor.map(_play_one_game, tasks))
    wins = sum(1 for o, _ in outcomes if o == 1)
    draws = sum(1 for o, _ in outcomes if o == 0)
    losses = sum(1 for o, _ in outcomes if o == -1)
    avg_ms = sum(ms for _, ms in outcomes) / len(outcomes)
    return {
        "wins": wins,
        "draws": draws,
        "losses": losses,
        "games": n_games,
        "winrate": round(wins / n_games * 100.0, 2),
        "avg_move_ms": round(avg_ms, 2),
    }


def run_experiment_for_board(
    board_size: int,
    win_len: int,
    iterations: int,
    n_games: int,
    executor: ProcessPoolExecutor,
) -> dict:
    print(f"\n{'='*65}")
    print(f"  BÀN {board_size}×{board_size} — cần {win_len} quân | iterations={iterations} | {n_games} ván")
    print(f"{'='*65}")

    results = {}

    print("  Random rollout:")
    r = run_match(False, iterations, n_games, board_size, win_len, executor)
    results["random"] = r
    print(f"    {r}")

    print("  Heuristic rollout:")
    h = run_match(True, iterations, n_games, board_size, win_len, executor)
    results["heuristic"] = h
    print(f"    {h}")

    improvement = h["winrate"] - r["winrate"]
    print(f"\n  Cải thiện: {improvement:+.1f}% so với rollout ngẫu nhiên")
    return results


def run_experiment():
    results_dir = os.path.join(os.path.dirname(__file__), "results")
    os.makedirs(results_dir, exist_ok=True)
    workers = max(1, (os.cpu_count() or 4) - 2)

    configs = [
        {"board_size": 3,  "win_len": 3, "iterations": 500, "n_games": 100},
        {"board_size": 15, "win_len": 5, "iterations": 200, "n_games": 50},
    ]

    with ProcessPoolExecutor(max_workers=workers) as executor:
        for cfg in configs:
            label = f"{cfg['board_size']}x{cfg['board_size']}"
            data = run_experiment_for_board(executor=executor, **cfg)
            path = os.path.join(results_dir, f"rollout_comparison_{label}.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            print(f"  Đã lưu: {path}")


if __name__ == "__main__":
    run_experiment()
