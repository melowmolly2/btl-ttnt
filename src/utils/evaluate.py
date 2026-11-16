"""
evaluate.py — Hàm lượng giá (evaluation / heuristic) cho Tic-Tac-Toe.

Dùng cho:
- Minimax: trả về điểm khi hết depth
- Rollout heuristic trong MCTS

Ý tưởng:
  Quét toàn bộ các đường (ngang, dọc, chéo chính, chéo phụ).
  Mỗi đường -> tìm chuỗi quân liên tiếp -> tra bảng điểm.
  evaluate = my_total_score - opponent_total_score
"""
import numpy as np
from src.game.board import Board, X, O, EMPTY


# Bảng điểm theo (độ_dài, số_đầu_mở)
# Chuỗi mở 2 đầu nguy hiểm hơn mở 1 đầu RẤT NHIỀU (gấp 10x, không phải 2x)
# vì đối thủ không thể chặn cả 2 đầu cùng 1 nước
_SCORE = {
    (5, 1): 100_000,  # thắng
    (5, 2): 100_000,
    (4, 2): 50_000,   # gần như thắng chắc — không thể chặn 2 đầu
    (4, 1):  5_000,   # nguy hiểm nhưng chặn được
    (3, 2):  2_000,   # rất nguy hiểm
    (3, 1):    200,
    (2, 2):    100,
    (2, 1):     10,
    (1, 2):      5,
    (1, 1):      1,
}


def _score_line(line, player: int) -> int:
    """
    Tính điểm cho player trên một đường thẳng (1D array).

    Ví dụ:
      [O, X, X, X, ., ., O] → chuỗi 3, mở 1 đầu → (3,1) = 200
      [., X, X, X, ., ., O] → chuỗi 3, mở 2 đầu → (3,2) = 2000
    """
    score = 0
    n = len(line)
    i = 0

    while i < n:
        if line[i] != player:
            i += 1
            continue

        # Kiểm tra đầu trái có mở không
        left_open = (i > 0 and line[i - 1] == EMPTY)

        # Đếm độ dài chuỗi
        j = i
        while j < n and line[j] == player:
            j += 1
        length = j - i

        # Kiểm tra đầu phải có mở không
        right_open = (j < n and line[j] == EMPTY)

        open_ends = int(left_open) + int(right_open)

        if open_ends > 0:
            key = (min(length, 5), open_ends)
            score += _SCORE.get(key, 0)

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
