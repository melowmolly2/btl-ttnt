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


def _count_space(line, pos: int, direction: int) -> int:
    """Đếm số ô EMPTY liên tiếp từ pos theo direction (+1 hoặc -1)."""
    n = len(line)
    space = 0
    p = pos
    while 0 <= p < n and line[p] == EMPTY:
        space += 1
        p += direction
    return space


def _score_line(line, player: int, win_len: int = 5) -> int:
    """
    Tính điểm cho player trên một đường thẳng (1D array).

    Một đầu được coi là "mở" khi ô kề là EMPTY.
    Nhưng nếu space_left + length + space_right < win_len thì chuỗi
    không thể thắng theo hướng này → 0 điểm (bị chặn hoàn toàn).
    Nếu đủ chỗ nhưng chỉ 1 phía có space → tính 1 đầu mở.

    Ví dụ (win_len=5):
      O . X X X . O  → total_space=1+1=2, length=3 → 2+3=5 >= 5 → có thể thắng
                       nhưng space_left=space_right=1, không đầu nào "rộng hơn"
                       → cả 2 đầu đều bị hạn chế → tính (3,1) = 200
      . . X X X . O  → space_left=2, space_right=1, total=6 >= 5
                       trái rộng hơn (2 chỗ), phải hẹp (1 chỗ)
                       → 2 đầu kề EMPTY → (3,2) = 2000  (vẫn double threat)
      O . X X X . .  → đối xứng với trên → (3,2) = 2000
      O X X X O      → total=0 < 5 → 0 điểm
    """
    score = 0
    n = len(line)
    i = 0

    while i < n:
        if line[i] != player:
            i += 1
            continue

        # Đếm độ dài chuỗi
        j = i
        while j < n and line[j] == player:
            j += 1
        length = j - i

        # Đếm chỗ trống 2 phía
        space_left  = _count_space(line, i - 1, direction=-1)
        space_right = _count_space(line, j,     direction=+1)

        total_space = space_left + space_right

        # Không đủ chỗ để thắng → bỏ qua
        if length + total_space < win_len:
            i = j
            continue

        # Đầu nào kề EMPTY thì coi là mở
        left_open  = (i > 0   and line[i - 1] == EMPTY)
        right_open = (j < n   and line[j]     == EMPTY)
        open_ends  = int(left_open) + int(right_open)

        # Nếu cả 2 đầu kề EMPTY nhưng mỗi bên chỉ có đúng 1 chỗ trống
        # và tổng vừa đủ win_len → thực ra chỉ có thể đi 1 hướng → 1 đầu mở
        if open_ends == 2 and space_left == 1 and space_right == 1 and length + 2 == win_len:
            open_ends = 1

        if open_ends > 0:
            key = (min(length, 5), open_ends)
            score += _SCORE.get(key, 0)

        i = j

    return score


def _total_score(board: Board, player: int) -> int:
    """Tổng điểm của player trên toàn bộ bàn cờ (4 hướng)."""
    b = board.board
    n = board.size
    win = board.win_len
    total = 0

    # Hàng ngang
    for r in range(n):
        total += _score_line(b[r, :], player, win)

    # Hàng dọc
    for c in range(n):
        total += _score_line(b[:, c], player, win)

    # Đường chéo chính (↘): chỉ lấy đường đủ dài (>= win_len)
    for k in range(-(n - win), n - win + 1):
        total += _score_line(b.diagonal(k), player, win)

    # Đường chéo phụ (↙): lật bảng rồi lấy chéo chính
    b_flip = np.fliplr(b)
    for k in range(-(n - win), n - win + 1):
        total += _score_line(b_flip.diagonal(k), player, win)

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
