"""
minimax.py — Thuật toán Minimax thuần (không cắt tỉa).
Dùng để đo số nút cần duyệt, so sánh với Alpha-Beta.
"""
from src.game.board import Board, X


class MinimaxAgent:
    """
    Minimax agent. Trả về nước đi tốt nhất và số nút đã duyệt.

    Parameters
    ----------
    max_depth : int
        Giới hạn độ sâu tìm kiếm.
    eval_fn : callable(Board, int) -> float
        Hàm lượng giá, nhận board và perspective (X hoặc O).
    """

    def __init__(self, max_depth: int = 3, eval_fn=None):
        self.max_depth = max_depth
        self.eval_fn = eval_fn
        self.nodes_visited = 0       # đếm số nút duyệt mỗi lần gọi

    def get_move(self, board: Board) -> tuple[int, int]:
        """Trả về (row, col) — nước đi tốt nhất theo Minimax."""
        self.nodes_visited = 0
        me = board.current_player
        best_score = float("-inf")
        best_move = None

        for move in board.get_legal_moves():
            clone = board.clone()
            clone.make_move(*move)
            score = self._minimax(clone, self.max_depth - 1, False, me)
            if score > best_score:
                best_score = score
                best_move = move

        return best_move

    def _minimax(self, board: Board, depth: int, is_maximizing: bool, me: int) -> float:
        self.nodes_visited += 1

        if board.is_terminal or depth == 0:
            return self._evaluate(board, me)

        moves = board.get_legal_moves()
        if is_maximizing:
            best = float("-inf")
            for move in moves:
                clone = board.clone()
                clone.make_move(*move)
                best = max(best, self._minimax(clone, depth - 1, False, me))
            return best
        else:
            best = float("inf")
            for move in moves:
                clone = board.clone()
                clone.make_move(*move)
                best = min(best, self._minimax(clone, depth - 1, True, me))
            return best

    def _evaluate(self, board: Board, me: int) -> float:
        if self.eval_fn:
            return self.eval_fn(board, me)
        # Hàm mặc định đơn giản
        if board.winner == me:
            return 1_000_000
        if board.winner == -me:
            return -1_000_000
        return 0
