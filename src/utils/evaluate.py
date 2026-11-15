"""
evaluate.py — Hàm lượng giá (evaluation / heuristic) cho Tic-Tac-Toe.

Dùng cho:
- Minimax: trả về điểm khi hết depth
- Rollout heuristic trong MCTS

Ý tưởng:
  Quét toàn bộ các đường (ngang, dọc, chéo chính, chéo phụ).
  Mỗi đường → tìm chuỗi quân liên tiếp → tra bảng điểm.
  evaluate = my_total_score - opponent_total_score
"""
import numpy as np
from src.game.board import Board, X, O, EMPTY


# Bảng điểm cho chuỗi N quân liên tiếp
# Chuỗi mở 2 đầu nguy hiểm hơn mở 1 đầu → nhân hệ số
_SCORE = {
    5: 100_000,   # thắng chắc chắn
    4: 10_000,
    3: 1_000,
    2: 100,
    1: 10,
}


def _score_line(line, player: int) -> int:
    """
    Tính điểm cho player trên một đường thẳng (1D array).

    Ví dụ line = [O, X, X, X, ., ., O]
    Với player = X:
      - Chuỗi X X X, mở 1 đầu phải (ô trống), bị chặn trái bởi O
      → điểm = 1_000 * 1
    """
    score = 0
    n = len(line)
    i = 0

    while i < n:
        if line[i] != player:
            i += 1
            continue

        # Tìm đầu chuỗi quân player
        # Kiểm tra đầu trái có mở không
        left_open = (i > 0 and line[i - 1] == EMPTY)

        # Đếm độ dài chuỗi
        j = i
        while j < n and line[j] == player:
            j += 1
        length = j - i  # số quân liên tiếp

        # Kiểm tra đầu phải có mở không
        right_open = (j < n and line[j] == EMPTY)

        open_ends = int(left_open) + int(right_open)

        if open_ends > 0:
            score += _SCORE.get(min(length, 5), 0) * open_ends

        i = j  # nhảy qua chuỗi vừa xét

    return score


def _total_score(board: Board, player: int) -> int:
    """Tổng điểm của player trên toàn bộ bàn cờ (4 hướng)."""
    b = board.board
    n = board.size
    win = board.win_len
    total = 0

    # Hàng ngang
    for r in range(n):
        total += _score_line(b[r, :], player)

    # Hàng dọc
    for c in range(n):
        total += _score_line(b[:, c], player)

    # Đường chéo chính (↘): chỉ lấy đường đủ dài (>= win_len)
    for k in range(-(n - win), n - win + 1):
        total += _score_line(b.diagonal(k), player)

    # Đường chéo phụ (↙): lật bảng rồi lấy chéo chính
    b_flip = np.fliplr(b)
    for k in range(-(n - win), n - win + 1):
        total += _score_line(b_flip.diagonal(k), player)

    return total


def evaluate(board: Board, perspective: int = X) -> float:
    """
    Hàm lượng giá trạng thái bàn cờ từ góc nhìn perspective (X hoặc O).

    Trả về:
      +1_000_000  nếu perspective thắng
      -1_000_000  nếu perspective thua
       0          nếu hòa
      my_score - opp_score  nếu chưa kết thúc
    """
    if board.winner == perspective:
        return 1_000_000.0
    if board.winner == -perspective:
        return -1_000_000.0
    if board.is_draw:
        return 0.0

    my_score  = _total_score(board, perspective)
    opp_score = _total_score(board, -perspective)
    return float(my_score - opp_score)
