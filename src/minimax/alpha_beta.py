"""
alpha_beta.py — Minimax + cắt tỉa Alpha-Beta.
So sánh với minimax.py về số nút đã duyệt.
"""
from src.game.board import Board


class AlphaBetaAgent:
    """
    Minimax với cắt tỉa Alpha-Beta.

    Parameters
    ----------
    max_depth : int
    eval_fn   : callable(Board, int) -> float
    """

    def __init__(self, max_depth: int = 3, eval_fn=None):
        self.max_depth = max_depth
        self.eval_fn = eval_fn
        self.nodes_visited = 0

    def get_move(self, board: Board) -> tuple[int, int]:
        self.nodes_visited = 0
        me = board.current_player
        best_score = float("-inf")
        best_move = None
        alpha = float("-inf")
        beta = float("inf")

        for move in board.get_legal_moves():
            clone = board.clone()
            clone.make_move(*move)
            score = self._alpha_beta(clone, self.max_depth - 1, alpha, beta, False, me)
            if score > best_score:
                best_score = score
                best_move = move
            alpha = max(alpha, best_score)

        return best_move

    def _alpha_beta(
        self, board: Board, depth: int, alpha: float, beta: float,
        is_maximizing: bool, me: int
    ) -> float:
        self.nodes_visited += 1

        if board.is_terminal or depth == 0:
            return self._evaluate(board, me)

        moves = board.get_legal_moves()

        if is_maximizing:
            value = float("-inf")
            for move in moves:
                clone = board.clone()
                clone.make_move(*move)
                value = max(value, self._alpha_beta(clone, depth - 1, alpha, beta, False, me))
                alpha = max(alpha, value)
                if alpha >= beta:
                    break   # cắt tỉa beta
            return value
        else:
            value = float("inf")
            for move in moves:
                clone = board.clone()
                clone.make_move(*move)
                value = min(value, self._alpha_beta(clone, depth - 1, alpha, beta, True, me))
                beta = min(beta, value)
                if alpha >= beta:
                    break   # cắt tỉa alpha
            return value

    def _evaluate(self, board: Board, me: int) -> float:
        if self.eval_fn:
            return self.eval_fn(board, me)
        if board.winner == me:
            return 1_000_000
        if board.winner == -me:
            return -1_000_000
        return 0
