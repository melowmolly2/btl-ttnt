"""
run_rollout_experiment.py
So sánh rollout ngẫu nhiên vs rollout heuristic.
"""
import sys
import os
import json
import random

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.game.board import Board, X, O
from src.mcts.mcts import MCTSAgent
from src.mcts.rollout import random_rollout, heuristic_rollout


def random_agent(board: Board):
    return random.choice(board.get_legal_moves())


def run_match(agent: MCTSAgent, n_games: int = 100, board_size=3, win_len=3) -> dict:
    wins = draws = losses = 0
    for i in range(n_games):
        board = Board(board_size, win_len)
        mcts_is_x = (i % 2 == 0)
        while not board.is_terminal:
            if (board.current_player == X) == mcts_is_x:
                move = agent.get_move(board)
            else:
                move = random_agent(board)
            board.make_move(*move)
        mp = X if mcts_is_x else O
        if board.winner == mp:
            wins += 1
        elif board.is_draw:
            draws += 1
        else:
            losses += 1
    return {"wins": wins, "draws": draws, "losses": losses, "winrate": wins / n_games * 100}


def run_experiment(iterations=500, n_games=100):
    import math
    results = {}

    print("=== Random rollout ===")
    agent_rand = MCTSAgent(iterations=iterations, c=math.sqrt(2), rollout_fn=random_rollout)
    r = run_match(agent_rand, n_games)
    results["random"] = r
    print(f"  {r}")

    print("=== Heuristic rollout ===")
    agent_heur = MCTSAgent(iterations=iterations, c=math.sqrt(2), rollout_fn=heuristic_rollout)
    h = run_match(agent_heur, n_games)
    results["heuristic"] = h
    print(f"  {h}")

    improvement = h["winrate"] - r["winrate"]
    print(f"\n  Cải thiện: +{improvement:.1f}% so với rollout ngẫu nhiên")

    os.makedirs(os.path.join(os.path.dirname(__file__), "results"), exist_ok=True)
    path = os.path.join(os.path.dirname(__file__), "results", "rollout_comparison.json")
    with open(path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"  Đã lưu: {path}")


if __name__ == "__main__":
    run_experiment()
