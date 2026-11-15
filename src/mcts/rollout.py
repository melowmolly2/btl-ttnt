"""
rollout.py — Hàm Simulation (rollout) cho MCTS.

Hai chiến lược:
1. random_rollout   — đi hoàn toàn ngẫu nhiên
2. heuristic_rollout — ưu tiên nước thắng ngay / chặn thắng đối thủ
"""
import random
from src.game.board import Board, EMPTY


def random_rollout(board: Board, player: int) -> float:
    """
    Mô phỏng ngẫu nhiên từ trạng thái board cho đến khi kết thúc.

    Parameters
    ----------
    board  : Board  — trạng thái sau Expansion (chưa là terminal)
    player : int    — người mà kết quả trả về theo góc nhìn của họ

    Returns
    -------
    1.0 nếu player thắng, 0.5 nếu hòa, 0.0 nếu thua
    """
    sim = board.clone()
    while not sim.is_terminal:
        moves = sim.get_legal_moves()
        if not moves:
            break
        move = random.choice(moves)
        sim.make_move(*move)

    return _result(sim, player)


def heuristic_rollout(board: Board, player: int) -> float:
    """
    Rollout có heuristic:
    - Nếu có nước thắng ngay → chọn nước đó.
    - Nếu đối thủ có nước thắng ngay → chặn.
    - Nếu không → ngẫu nhiên.

    Cải thiện đáng kể so với rollout thuần ngẫu nhiên, đặc biệt ở bàn lớn.
    (Tiền thân của value network trong AlphaGo/AlphaZero)
    """
    sim = board.clone()
    while not sim.is_terminal:
        move = _pick_smart_move(sim)
        sim.make_move(*move)
    return _result(sim, player)


# ------------------------------------------------------------------
# Hàm nội bộ
# ------------------------------------------------------------------

def _result(board: Board, player: int) -> float:
    if board.winner == player:
        return 1.0
    if board.is_draw:
        return 0.5
    return 0.0


def _pick_smart_move(board: Board):
    """Chọn nước thắng ngay / chặn thắng, nếu không thì random."""
    moves = board.get_legal_moves()
    me = board.current_player
    opp = -me

    # Ưu tiên 1: nước thắng ngay
    for move in moves:
        clone = board.clone()
        clone.make_move(*move)
        if clone.winner == me:
            return move

    # Ưu tiên 2: chặn đối thủ thắng ngay
    for move in moves:
        clone = board.clone()
        # Giả vờ đối thủ đánh
        clone.board[move[0], move[1]] = opp
        clone.move_history.append(move)
        if clone._check_win(move[0], move[1]):
            # nếu đối thủ sẽ thắng ở đây → chặn
            clone.board[move[0], move[1]] = EMPTY
            clone.move_history.pop()
            return move

    # Mặc định: ngẫu nhiên
    return random.choice(moves)
