"""
game.py — Vòng lặp game chính: Human vs AI, AI vs AI
"""
from src.game.board import Board, X, O


def player_symbol(player: int) -> str:
    return "X" if player == X else "O"


def human_move(board: Board) -> tuple[int, int]:
    """Nhập nước đi từ bàn phím."""
    while True:
        try:
            inp = input(f"  [{player_symbol(board.current_player)}] Nhập hàng cột (vd: 7 7): ").strip()
            r, c = map(int, inp.split())
            if board.make_move(r, c):
                return r, c
            print("  Ô đã có quân hoặc không hợp lệ, thử lại.")
        except (ValueError, IndexError):
            print("  Định dạng sai. Nhập hai số nguyên cách nhau dấu cách.")


def play_game(
    ai_x=None,   # callable(board) -> (row, col) hoặc None (human)
    ai_o=None,   # callable(board) -> (row, col) hoặc None (human)
    board_size: int = 15,
    win_len: int = 5,
    verbose: bool = True,
) -> int:
    """
    Chạy một ván. Trả về X (1), O (-1), hoặc 0 (hòa).
    ai_x / ai_o: None = người, callable = AI.
    """
    board = Board(board_size, win_len)
    agents = {X: ai_x, O: ai_o}

    while not board.is_terminal:
        if verbose:
            print(board)
            print()

        agent = agents[board.current_player]
        if agent is None:
            human_move(board)
        else:
            move = agent(board)
            board.make_move(*move)
            if verbose:
                p = player_symbol(-board.current_player)  # đã đổi rồi
                print(f"  [{p}] đánh vào: {move}")

    if verbose:
        print(board)
        if board.winner:
            print(f"\n=== {player_symbol(board.winner)} THẮNG! ===")
        else:
            print("\n=== HÒA! ===")

    return board.winner if board.winner else 0
