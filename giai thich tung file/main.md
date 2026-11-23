# Main — Giao diện dòng lệnh (CLI)

Entry point chạy game trên terminal (`python main.py`). Cho phép chọn người chơi (Human hoặc AI), cấu hình bàn cờ và chạy benchmark nhiều ván AI vs AI.

---

## Tạo Agent

| Hàm | Tham số nhập | Agent tạo ra |
|---|---|---|
| `make_minimax_agent()` | `depth` (mặc định 3) | `MinimaxAgent(max_depth=depth, eval_fn=evaluate)` |
| `make_ab_agent()` | `depth` (mặc định 3) | `AlphaBetaAgent(max_depth=depth, eval_fn=evaluate)` |
| `make_mcts_agent()` | `iterations` (1000), `c` (1.414), `heuristic` (y/N) | `MCTSAgent` với `random_rollout` hoặc `heuristic_rollout` |

Mỗi hàm trả về một closure `lambda board: agent.get_move(board)` để truyền trực tiếp vào `play_game()`.

---

## Menu & Cấu hình

- `pick_player(label)`: Hiện menu 4 lựa chọn (`Human`, `Minimax`, `Alpha-Beta`, `MCTS`), trả về `(agent_or_None, tên)`.
- `ask_board()`: Nhập `size` (mặc định 15) và `win_len` (mặc định 5).
- `ask_benchmark()`: Chỉ hỏi số ván `n` khi **cả hai bên đều là AI** (nếu có Human thì mặc định `n = 1`).

---

## `run_benchmark(ai_x, ai_o, n, board_size, win_len)`

Chạy `n` ván liên tiếp qua `play_game()`:
- Nếu `n == 1`: bật `verbose=True` để in bàn cờ từng nước.
- Nếu `n > 1`: tắt `verbose`, chỉ in kết quả từng ván và tổng kết số ván X thắng / O thắng / Hòa.
