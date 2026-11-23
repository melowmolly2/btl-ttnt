"""
node.py — Lớp MCTSNode: một nút trong cây MCTS.
"""
import math
from src.game.board import Board
from src.utils.evaluate import evaluate

UCT_VARIANTS = ("standard", "no_sqrt", "no_ln", "linear", "progressive_bias")


class MCTSNode:
    """
    Một nút trong cây MCTS.

    Attributes
    ----------
    board       : Board  — trạng thái bàn cờ tại nút này
    parent      : MCTSNode | None
    move        : tuple(row, col) | None — nước đi dẫn đến nút này
    children    : list[MCTSNode]
    W           : float  — tổng điểm thắng (1 = thắng, 0.5 = hòa, 0 = thua)
    N           : int    — số lần nút này được thăm
    untried     : list   — các nước đi chưa mở rộng
    player      : int    — người chơi VỪA đánh nước dẫn đến nút này (để backprop)
    """

    def __init__(self, board: Board, parent=None, move=None):
        self.board = board
        self.parent = parent
        self.move = move
        self.children: list["MCTSNode"] = []
        self.W: float = 0.0
        self.N: int = 0
        # Người chơi đã đánh nước dẫn đến nút này (là người chơi trước khi board đổi lượt)
        self.player = -board.current_player
        self.untried = board.get_legal_moves()
        self._heuristic: float | None = None

    def _get_heuristic(self) -> float:
        """Điểm heuristic chuẩn hóa về [0, 1] từ góc nhìn self.player (lazy-cached)."""
        if self._heuristic is None:
            raw = evaluate(self.board, self.player)
            self._heuristic = 0.5 + 0.5 * math.tanh(raw / 5000.0)
        return self._heuristic

    # ------------------------------------------------------------------
    # UCT score
    # ------------------------------------------------------------------

    def uct_score(self, c: float = math.sqrt(2), variant: str = "standard") -> float:
        """
        Tính điểm UCT theo biến thể:
          - standard         : W/N + c * sqrt(ln(N_p) / N)
          - no_sqrt          : W/N + c * (ln(N_p) / N)
          - no_ln            : W/N + c * sqrt(N_p / N)
          - linear           : W/N + c * (N_p / N)
          - progressive_bias : W/N + c * sqrt(ln(N_p) / N) + H / (N + 1)
        Nút chưa thăm (N=0) → trả về +∞ để ưu tiên tối cao.
        """
        if self.N == 0:
            return float("inf")
        exploitation = self.W / self.N
        n_p = self.parent.N
        if variant == "standard":
            exploration = c * math.sqrt(math.log(n_p) / self.N)
            return exploitation + exploration
        if variant == "no_sqrt":
            return exploitation + c * (math.log(n_p) / self.N)
        if variant == "no_ln":
            return exploitation + c * math.sqrt(n_p / self.N)
        if variant == "linear":
            return exploitation + c * (n_p / self.N)
        if variant == "progressive_bias":
            exploration = c * math.sqrt(math.log(n_p) / self.N)
            bias = self._get_heuristic() / (self.N + 1)
            return exploitation + exploration + bias
        raise ValueError(f"Unknown UCT variant: {variant}")

    # ------------------------------------------------------------------
    # Truy vấn
    # ------------------------------------------------------------------

    @property
    def is_fully_expanded(self) -> bool:
        return len(self.untried) == 0

    @property
    def is_terminal(self) -> bool:
        return self.board.is_terminal

    def best_child(self, c: float = math.sqrt(2), variant: str = "standard") -> "MCTSNode":
        """Trả về con có UCT score cao nhất."""
        return max(self.children, key=lambda ch: ch.uct_score(c, variant))

    def most_visited_child(self) -> "MCTSNode":
        """Trả về con được thăm nhiều nhất (dùng khi chọn nước đi thực tế)."""
        return max(self.children, key=lambda ch: ch.N)

    # ------------------------------------------------------------------
    # Expand
    # ------------------------------------------------------------------

    def expand(self) -> "MCTSNode":
        """Mở rộng một nút con từ untried_moves."""
        move = self.untried.pop()          # lấy một nước chưa thử
        new_board = self.board.clone()
        new_board.make_move(*move)
        child = MCTSNode(new_board, parent=self, move=move)
        self.children.append(child)
        return child

    # ------------------------------------------------------------------
    # Backpropagation
    # ------------------------------------------------------------------

    def update(self, result: float):
        """Cập nhật W và N. result ∈ {0, 0.5, 1} từ góc nhìn của self.player."""
        self.N += 1
        self.W += result

    def __repr__(self) -> str:
        m = self.move
        return f"MCTSNode(move={m}, W={self.W:.1f}, N={self.N}, uct={self.uct_score():.3f})"
