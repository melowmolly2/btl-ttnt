"""
rollout.py — Hàm Simulation (rollout) cho MCTS.

Hai chiến lược:
1. random_rollout   — đi hoàn toàn ngẫu nhiên
2. heuristic_rollout — ưu tiên nước thắng ngay / chặn thắng đối thủ
"""
import random
from src.game.board import Board, EMPTY

# Giới hạn số bước trong random rollout để tránh simulation quá dài trên bàn lớn.
# Nếu chưa kết thúc sau MAX_ROLLOUT_STEPS nước → coi như hòa (0.5).
MAX_ROLLOUT_STEPS = 30


def random_rollout(board: Board, player: int) -> float:
    """
    Mô phỏng ngẫu nhiên từ trạng thái board, tối đa MAX_ROLLOUT_STEPS nước.

    Giới hạn bước cần thiết trên bàn 15×15: không giới hạn thì simulation
    có thể chạy 100–200 nước mà không ra kết quả vì hai bên đi bừa hiếm
    khi tạo được 5 quân thẳng hàng.

    Parameters
    ----------
    board  : Board  — trạng thái sau Expansion (chưa là terminal)
    player : int    — người mà kết quả trả về theo góc nhìn của họ

    Returns
    -------
    1.0 nếu player thắng, 0.5 nếu hòa hoặc hết bước, 0.0 nếu thua
    """
    sim = board.clone()
    steps = 0
    while not sim.is_terminal and steps < MAX_ROLLOUT_STEPS:
        moves = sim.get_legal_moves()
        if not moves:
            break
        sim.make_move(*random.choice(moves))
        steps += 1

    return _result(sim, player)


def heuristic_rollout(board: Board, player: int) -> float:
    """
    Rollout có heuristic, tối đa MAX_ROLLOUT_STEPS nước:
    - Nếu có nước thắng ngay → chọn nước đó.
    - Nếu đối thủ có nước thắng ngay → chặn.
    - Nếu không → ngẫu nhiên.

    Cải thiện đáng kể so với rollout thuần ngẫu nhiên, đặc biệt ở bàn lớn.
    (Tiền thân của value network trong AlphaGo/AlphaZero)
    """
    sim = board.clone()
    steps = 0
    while not sim.is_terminal and steps < MAX_ROLLOUT_STEPS:
        move = _pick_smart_move(sim)
        sim.make_move(*move)
        steps += 1
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
    """Chọn nước thắng ngay / chặn thắng, nếu không thì random.
    Ghi tay + hoàn tác thủ công để tránh clone và undo_move overhead.
    """
    moves = board.get_legal_moves()
    me = board.current_player
    opp = -me

    # Ưu tiên 1: nước thắng ngay
    for move in moves:
        board.board[move[0], move[1]] = me
        board.move_history.append(move)
        wins = board._check_win(move[0], move[1])
        board.board[move[0], move[1]] = EMPTY
        board.move_history.pop()
        if wins:
            return move

    # Ưu tiên 2: chặn đối thủ thắng ngay
    for move in moves:
        board.board[move[0], move[1]] = opp
        board.move_history.append(move)
        blocks = board._check_win(move[0], move[1])
        board.board[move[0], move[1]] = EMPTY
        board.move_history.pop()
        if blocks:
            return move

    return random.choice(moves)
