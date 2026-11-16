"""
mcts.py — MCTS agent với UCT.

Bốn bước: Selection → Expansion → Simulation → Backpropagation
"""
import math
from src.game.board import Board, X, O
from src.mcts.node import MCTSNode
from src.mcts.rollout import random_rollout


class MCTSAgent:
    """
    MCTS + UCT agent.

    Parameters
    ----------
    iterations : int    — số vòng lặp MCTS mỗi lần gọi get_move
    c          : float  — hằng số khám phá (lý thuyết: sqrt(2) ≈ 1.414)
    rollout_fn : callable(Board) -> float
                  Nhận board sau expansion, trả về kết quả từ góc nhìn người chơi
                  vừa đánh: 1.0 = thắng, 0.5 = hòa, 0.0 = thua.
    """

    def __init__(
        self,
        iterations: int = 1000,
        c: float = math.sqrt(2),
        rollout_fn=None,
    ):
        self.iterations = iterations
        self.c = c
        self.rollout_fn = rollout_fn or random_rollout

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_move(self, board: Board) -> tuple[int, int]:
        """Trả về (row, col) — nước đi tốt nhất."""
        root = MCTSNode(board.clone())

        for _ in range(self.iterations):
            node = self._select(root)

            if not node.is_terminal:
                if not node.is_fully_expanded:
                    node = node.expand()   # Expansion
                result = self.rollout_fn(node.board, node.player)
            else:
                result = self._terminal_result(node.board, node.player)

            self._backpropagate(node, result)

        best = root.most_visited_child()
        return best.move

    def get_root_stats(self, board: Board) -> list[dict]:
        """
        Chạy MCTS và trả về thống kê W, N, W/N của các nút con gốc.
        Dùng cho thực nghiệm và report.
        """
        root = MCTSNode(board.clone())
        for _ in range(self.iterations):
            node = self._select(root)
            if not node.is_terminal:
                if not node.is_fully_expanded:
                    node = node.expand()
                result = self.rollout_fn(node.board, node.player)
            else:
                result = self._terminal_result(node.board, node.player)
            self._backpropagate(node, result)

        stats = []
        for ch in root.children:
            stats.append({
                "move": ch.move,
                "W": ch.W,
                "N": ch.N,
                "W/N": ch.W / ch.N if ch.N > 0 else 0,
            })
        return sorted(stats, key=lambda s: s["N"], reverse=True)

    # ------------------------------------------------------------------
    # Bốn bước MCTS
    # ------------------------------------------------------------------

    def _select(self, node: MCTSNode) -> MCTSNode:
        """Selection: đi xuống cây theo UCT cho đến nút lá."""
        while not node.is_terminal:
            if not node.is_fully_expanded:
                return node      # Expansion sẽ xử lý
            node = node.best_child(self.c)
        return node

    # Expansion nằm trong get_move (node.expand())

    def _backpropagate(self, node: MCTSNode, result: float):
        """
        Backpropagation: cập nhật W, N ngược lên gốc.

        result = kết quả từ góc nhìn của node.player.
        Mỗi bước lên cha: góc nhìn đổi → result = 1 - result.

        Quy ước W tại mỗi nút:
          - W lưu số điểm thắng của người ĐÃ ĐÁNH nước dẫn đến nút này (node.player).
          - Khi UCT tính W/N tại nút con, nó đại diện cho "nước này tốt như thế nào
            với người đã chọn nước đó".
          - Cha chọn con có UCT cao nhất → cha muốn con có W/N cao từ góc nhìn cha.
          - Vì cha và con là đối thủ nhau, nên khi backprop lên cha phải đảo result.
        """
        current = node
        current_result = result
        while current is not None:
            current.N += 1
            # Chỉ cộng W nếu nút này có player (không phải root rỗng)
            if current.move is not None:
                current.W += current_result
            current_result = 1.0 - current_result   # đổi góc nhìn khi lên cha
            current = current.parent

    # ------------------------------------------------------------------
    # Tiện ích
    # ------------------------------------------------------------------

    @staticmethod
    def _terminal_result(board: Board, player: int) -> float:
        """Kết quả từ góc nhìn player khi trạng thái kết thúc."""
        if board.winner == player:
            return 1.0
        if board.is_draw:
            return 0.5
        return 0.0
