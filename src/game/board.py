"""
board.py — Lớp Board: trạng thái bàn cờ Tic-Tac-Toe (5 quân thẳng hàng)
"""
import numpy as np

EMPTY = 0
X = 1      # Người chơi 1
O = -1     # Người chơi 2 / AI


class Board:
    """
    Bàn cờ Tic-Tac-Toe tổng quát: kích thước n x n, thắng khi WIN_LEN quân thẳng hàng.
    Mặc định: 15x15, cần 5 quân thẳng hàng (Gomoku / Cờ caro).
    """

    def __init__(self, size: int = 15, win_len: int = 5):
        self.size = size
        self.win_len = win_len
        self.board = np.zeros((size, size), dtype=np.int8)
        self.current_player = X      # X đi trước
        self.move_history: list[tuple[int, int]] = []
        self._winner = None

    # ------------------------------------------------------------------
    # Truy cập trạng thái
    # ------------------------------------------------------------------

    def clone(self) -> "Board":
        """Trả về bản sao độc lập của bàn cờ (dùng trong tìm kiếm)."""
        b = Board(self.size, self.win_len)
        b.board = self.board.copy()
        b.current_player = self.current_player
        b.move_history = self.move_history[:]
        b._winner = self._winner
        return b

    def get_legal_moves(self) -> list[tuple[int, int]]:
        """Trả về danh sách ô trống, ưu tiên ô gần quân đã đặt (giảm không gian tìm kiếm)."""
        if self._winner is not None or len(self.move_history) == self.size * self.size:
            return []
        # Nếu bàn cờ trống, chỉ cho phép trung tâm
        if not self.move_history:
            c = self.size // 2
            return [(c, c)]
        # Lấy các ô trống trong vùng lân cận 2 ô quanh quân đã đặt
        candidates = set()
        radius = 2
        for (r, c) in self.move_history:
            for dr in range(-radius, radius + 1):
                for dc in range(-radius, radius + 1):
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < self.size and 0 <= nc < self.size:
                        if self.board[nr, nc] == EMPTY:
                            candidates.add((nr, nc))
        return list(candidates)

    def get_all_empty(self) -> list[tuple[int, int]]:
        """Mọi ô trống (không lọc vùng lân cận)."""
        return [(r, c) for r in range(self.size) for c in range(self.size)
                if self.board[r, c] == EMPTY]

    # ------------------------------------------------------------------
    # Thực hiện / huỷ nước đi
    # ------------------------------------------------------------------

    def make_move(self, row: int, col: int) -> bool:
        """Đặt quân. Trả về True nếu hợp lệ."""
        if self.board[row, col] != EMPTY or self._winner is not None:
            return False
        self.board[row, col] = self.current_player
        self.move_history.append((row, col))
        if self._check_win(row, col):
            self._winner = self.current_player
        self.current_player = -self.current_player  # đổi lượt
        return True

    def undo_move(self):
        """Huỷ nước đi cuối (dùng trong Minimax không clone)."""
        if not self.move_history:
            return
        row, col = self.move_history.pop()
        self.current_player = -self.current_player  # hoàn lại lượt
        self.board[row, col] = EMPTY
        self._winner = None  # phải kiểm tra lại nếu cần, đơn giản set None

    # ------------------------------------------------------------------
    # Kiểm tra kết thúc
    # ------------------------------------------------------------------

    def _check_win(self, row: int, col: int) -> bool:
        """Kiểm tra quân vừa đặt tại (row, col) có tạo WIN_LEN liên tiếp không."""
        player = self.board[row, col]
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for dr, dc in directions:
            count = 1
            for sign in (1, -1):
                r, c = row + sign * dr, col + sign * dc
                while 0 <= r < self.size and 0 <= c < self.size and self.board[r, c] == player:
                    count += 1
                    r += sign * dr
                    c += sign * dc
            if count >= self.win_len:
                return True
        return False

    @property
    def winner(self):
        """X, O hoặc None nếu chưa kết thúc."""
        return self._winner

    @property
    def is_draw(self) -> bool:
        return self._winner is None and len(self.move_history) == self.size * self.size

    @property
    def is_terminal(self) -> bool:
        return self._winner is not None or self.is_draw

    # ------------------------------------------------------------------
    # Hiển thị
    # ------------------------------------------------------------------

    def __str__(self) -> str:
        symbols = {EMPTY: ".", X: "X", O: "O"}
        header = "   " + " ".join(f"{c:2}" for c in range(self.size))
        rows = [header]
        for r in range(self.size):
            row_str = f"{r:2} " + " ".join(f" {symbols[self.board[r, c]]}" for c in range(self.size))
            rows.append(row_str)
        return "\n".join(rows)
