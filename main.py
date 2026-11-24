"""
main.py — Entry point chính.
"""
import math
from src.game.game import play_game
from src.game.board import X, O
from src.minimax.minimax import MinimaxAgent
from src.minimax.alpha_beta import AlphaBetaAgent
from src.mcts.mcts import MCTSAgent
from src.mcts.node import UCT_VARIANTS
from src.mcts.rollout import random_rollout, heuristic_rollout
from src.utils.evaluate import evaluate


# ── Tạo agent ────────────────────────────────────────────────────────────────

def make_minimax_agent():
    try:
        depth = int(input("    Depth [3]: ").strip() or "3")
    except ValueError:
        depth = 3
    agent = MinimaxAgent(max_depth=depth, eval_fn=evaluate)
    return lambda board: agent.get_move(board)


def make_ab_agent():
    try:
        depth = int(input("    Depth [3]: ").strip() or "3")
    except ValueError:
        depth = 3
    agent = AlphaBetaAgent(max_depth=depth, eval_fn=evaluate)
    return lambda board: agent.get_move(board)


def make_mcts_agent():
    try:
        iters = int(input("    Iterations [1000]: ").strip() or "1000")
        c = float(input("    C [1.414]: ").strip() or "1.414")
        h = input("    Heuristic rollout? (y/N): ").strip().lower() == "y"
        v = input(f"    UCT variant {UCT_VARIANTS} [standard]: ").strip() or "standard"
        if v not in UCT_VARIANTS:
            v = "standard"
    except ValueError:
        iters, c, h, v = 1000, math.sqrt(2), False, "standard"
    rollout = heuristic_rollout if h else random_rollout
    agent = MCTSAgent(iterations=iters, c=c, rollout_fn=rollout, uct_variant=v)
    return lambda board: agent.get_move(board)


# ── Menu chọn người chơi ─────────────────────────────────────────────────────

PLAYER_MENU = """\
  1. Human
  2. Minimax
  3. Alpha-Beta
  4. MCTS
Chọn: """

PLAYER_NAMES = {
    "1": "Human",
    "2": "Minimax",
    "3": "Alpha-Beta",
    "4": "MCTS",
}


def pick_player(label: str):
    """Hiện menu chọn loại người chơi, trả về (agent_or_None, tên)."""
    print(f"\n  [ {label} ]")
    while True:
        choice = input(PLAYER_MENU).strip()
        if choice not in PLAYER_NAMES:
            print("  Lựa chọn không hợp lệ.")
            continue
        name = PLAYER_NAMES[choice]
        if choice == "1":
            return None, name
        elif choice == "2":
            return make_minimax_agent(), name
        elif choice == "3":
            return make_ab_agent(), name
        elif choice == "4":
            return make_mcts_agent(), name


# ── Tiện ích ─────────────────────────────────────────────────────────────────

def ask_board():
    try:
        size = int(input("\n  Kích thước bàn cờ [15]: ").strip() or "15")
        win_len = int(input("  Số quân liên tiếp để thắng [5]: ").strip() or "5")
    except ValueError:
        size, win_len = 15, 5
    return size, win_len


def ask_benchmark():
    try:
        n = int(input("  Số ván [1]: ").strip() or "1")
    except ValueError:
        n = 1
    return n


def run_benchmark(ai_x, ai_o, n, board_size, win_len):
    results = {X: 0, O: 0, 0: 0}
    for i in range(1, n + 1):
        verbose = (n == 1)
        result = play_game(ai_x=ai_x, ai_o=ai_o,
                           board_size=board_size, win_len=win_len,
                           verbose=verbose)
        results[result] += 1
        if n > 1:
            label = "X thắng" if result == X else "O thắng" if result == O else "Hòa"
            print(f"  Ván {i}/{n}: {label}")
    if n > 1:
        print(f"\n  Kết quả {n} ván:")
        print(f"    X thắng : {results[X]}")
        print(f"    O thắng : {results[O]}")
        print(f"    Hòa     : {results[0]}")


# ── Main ─────────────────────────────────────────────────────────────────────

MAIN_MENU = """
╔══════════════════════════════════════╗
║  TIC-TAC-TOE AI — Bài Tập Lớn TTNT  ║
╠══════════════════════════════════════╣
║  1. Bắt đầu ván mới                  ║
║  2. Thoát                            ║
╚══════════════════════════════════════╝
Chọn: """


def main():
    while True:
        choice = input(MAIN_MENU).strip()

        if choice == "1":
            agent_x, name_x = pick_player("Người chơi X (đi trước)")
            agent_o, name_o = pick_player("Người chơi O (đi sau)")
            print(f"\n  {name_x} (X)  vs  {name_o} (O)")

            size, win_len = ask_board()

            # Chỉ hỏi số ván khi cả hai đều là AI
            if agent_x is not None and agent_o is not None:
                n = ask_benchmark()
            else:
                n = 1

            print()
            run_benchmark(agent_x, agent_o, n, size, win_len)

        elif choice == "2":
            print("Tạm biệt!")
            break

        else:
            print("  Lựa chọn không hợp lệ.")


if __name__ == "__main__":
    main()
