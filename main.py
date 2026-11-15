"""
main.py — Entry point chính.

Chọn chế độ chơi:
  1. Human vs Minimax
  2. Human vs Alpha-Beta
  3. Human vs MCTS
  4. MCTS vs Alpha-Beta (AI tự chơi)
  5. Thoát
"""
import math
from src.game.board import Board, X, O
from src.game.game import play_game
from src.minimax.minimax import MinimaxAgent
from src.minimax.alpha_beta import AlphaBetaAgent
from src.mcts.mcts import MCTSAgent
from src.mcts.rollout import random_rollout, heuristic_rollout
from src.utils.evaluate import evaluate


def make_minimax_agent(depth=3):
    agent = MinimaxAgent(max_depth=depth, eval_fn=evaluate)
    return lambda board: agent.get_move(board)


def make_ab_agent(depth=3):
    agent = AlphaBetaAgent(max_depth=depth, eval_fn=evaluate)
    return lambda board: agent.get_move(board)


def make_mcts_agent(iterations=1000, c=math.sqrt(2), heuristic=False):
    rollout = heuristic_rollout if heuristic else random_rollout
    agent = MCTSAgent(iterations=iterations, c=c, rollout_fn=rollout)
    return lambda board: agent.get_move(board)


MENU = """
╔══════════════════════════════════════╗
║   TIC-TAC-TOE AI — Bài Tập Lớn TTNT  ║
╠══════════════════════════════════════╣
║  1. Human vs Minimax                 ║
║  2. Human vs Alpha-Beta              ║
║  3. Human vs MCTS                    ║
║  4. MCTS vs Alpha-Beta (AI tự chơi)  ║
║  5. Thoát                            ║
╚══════════════════════════════════════╝
Chọn: """


def main():
    while True:
        choice = input(MENU).strip()

        if choice == "1":
            ai = make_minimax_agent(depth=3)
            play_game(ai_x=None, ai_o=ai, board_size=15, win_len=5)

        elif choice == "2":
            ai = make_ab_agent(depth=3)
            play_game(ai_x=None, ai_o=ai, board_size=15, win_len=5)

        elif choice == "3":
            try:
                iters = int(input("  Số iterations MCTS [1000]: ").strip() or "1000")
                c_val = float(input("  Giá trị c [1.414]: ").strip() or "1.414")
                h = input("  Dùng heuristic rollout? (y/N): ").strip().lower() == "y"
            except ValueError:
                iters, c_val, h = 1000, math.sqrt(2), False
            ai = make_mcts_agent(iterations=iters, c=c_val, heuristic=h)
            play_game(ai_x=None, ai_o=ai, board_size=15, win_len=5)

        elif choice == "4":
            ai_x = make_mcts_agent(iterations=500)
            ai_o = make_ab_agent(depth=3)
            play_game(ai_x=ai_x, ai_o=ai_o, board_size=15, win_len=5, verbose=True)

        elif choice == "5":
            print("Tạm biệt!")
            break
        else:
            print("Lựa chọn không hợp lệ.")


if __name__ == "__main__":
    main()
