"""
run_mcts_experiment.py
Khảo sát ảnh hưởng của c ∈ {0.5, 1.0, 1.4, 2.0} và iterations lên tỷ lệ thắng.
MCTS đấu với Random agent trên 2 bàn: 3×3 (win=3) và 15×15 (win=5).
Chạy song song các ván bằng ProcessPoolExecutor để đạt >= 50 ván/cấu hình.
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
from src.mcts.rollout import random_rollout
from src.utils.visualize import plot_winrate_vs_iterations


def _play_one_game(args) -> tuple[int, float]:
    """Chạy 1 ván độc lập trong worker process. Trả về (outcome, avg_move_ms)."""
    game_idx, board_size, win_len, iters, c, seed = args
    random.seed(seed)
    agent = MCTSAgent(iterations=iters, c=c, rollout_fn=random_rollout)
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

    mcts_player = X if mcts_is_x else O
    if board.winner == mcts_player:
        outcome = 1
    elif board.is_draw:
        outcome = 0
    else:
        outcome = -1
    avg_ms = sum(move_times) / len(move_times) if move_times else 0.0
    return outcome, avg_ms


def run_match(
    iters: int,
    c: float,
    n_games: int,
    board_size: int,
    win_len: int,
    executor: ProcessPoolExecutor,
    base_seed: int = 42,
) -> dict:
    """Chạy n_games ván song song, trả về dict wins/draws/losses/winrate/avg_move_ms."""
    tasks = [
        (i, board_size, win_len, iters, c, base_seed + i)
        for i in range(n_games)
    ]
    outcomes = list(executor.map(_play_one_game, tasks))

    wins = sum(1 for o, _ in outcomes if o == 1)
    draws = sum(1 for o, _ in outcomes if o == 0)
    losses = sum(1 for o, _ in outcomes if o == -1)
    avg_ms = sum(ms for _, ms in outcomes) / len(outcomes)
    winrate = wins / n_games * 100.0

    print(
        f"Thắng: {wins:>3} | Hòa: {draws:>3} | Thua: {losses:>3} "
        f"| Winrate: {winrate:5.1f}% | {avg_ms:6.1f} ms/nước"
    )
    return {
        "wins": wins,
        "draws": draws,
        "losses": losses,
        "games": n_games,
        "winrate": round(winrate, 2),
        "avg_move_ms": round(avg_ms, 2),
    }


def run_experiment_for_board(
    board_size: int,
    win_len: int,
    n_games: int,
    c_values: list,
    iteration_list: list,
    executor: ProcessPoolExecutor,
) -> tuple[dict, dict]:
    """Trả về (winrate_map {c: {iters: winrate}}, detail_map {c: {iters: dict}})."""
    print(f"\n{'='*65}")
    print(f"  BÀN {board_size}×{board_size} — cần {win_len} quân thẳng hàng | {n_games} ván/cấu hình")
    print(f"{'='*65}")

    winrate_data = {}
    detail_data = {}
    for c in c_values:
        print(f"\n  c = {c}")
        winrate_data[c] = {}
        detail_data[c] = {}
        for iters in iteration_list:
            print(f"    iterations = {iters:>5}: ", end="", flush=True)
            res = run_match(
                iters=iters,
                c=c,
                n_games=n_games,
                board_size=board_size,
                win_len=win_len,
                executor=executor,
            )
            winrate_data[c][iters] = res["winrate"]
            detail_data[c][iters] = res

    return winrate_data, detail_data


def run_experiment():
    c_values = [0.5, 1.0, 1.4, 2.0]
    workers = max(1, (os.cpu_count() or 4) - 2)

    configs = [
        {
            "board_size": 3,
            "win_len": 3,
            "n_games": 100,
            "iteration_list": [50, 100, 200, 500, 1000, 2000],
            "label": "3x3",
        },
        {
            "board_size": 15,
            "win_len": 5,
            "n_games": 50,
            "iteration_list": [100, 200, 500],
            "label": "15x15",
        },
    ]

    results_dir = os.path.join(os.path.dirname(__file__), "results")
    os.makedirs(results_dir, exist_ok=True)

    with ProcessPoolExecutor(max_workers=workers) as executor:
        for cfg in configs:
            lbl = cfg["label"]
            winrate_data, detail_data = run_experiment_for_board(
                board_size=cfg["board_size"],
                win_len=cfg["win_len"],
                n_games=cfg["n_games"],
                c_values=c_values,
                iteration_list=cfg["iteration_list"],
                executor=executor,
            )

            # Lưu winrate (tương thích format cũ) + file chi tiết W/D/L
            save_rates = {
                str(c): {str(k): v for k, v in imap.items()}
                for c, imap in winrate_data.items()
            }
            rate_path = os.path.join(results_dir, f"mcts_c_experiment_{lbl}.json")
            with open(rate_path, "w", encoding="utf-8") as f:
                json.dump(save_rates, f, indent=2)
            print(f"\n  Đã lưu: {rate_path}")

            save_detail = {
                str(c): {str(k): v for k, v in imap.items()}
                for c, imap in detail_data.items()
            }
            detail_path = os.path.join(results_dir, f"mcts_c_detail_{lbl}.json")
            with open(detail_path, "w", encoding="utf-8") as f:
                json.dump(save_detail, f, indent=2)
            print(f"  Đã lưu: {detail_path}")

            plot_winrate_vs_iterations(
                winrate_data,
                save=True,
                filename=f"winrate_vs_iterations_{lbl}.png",
                title_suffix=lbl,
            )


if __name__ == "__main__":
    run_experiment()
