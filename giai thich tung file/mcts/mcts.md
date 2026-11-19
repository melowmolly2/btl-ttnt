# MCTSAgent — Monte Carlo Tree Search với UCT

MCTS xây dựng cây tìm kiếm dần dần qua các vòng lặp, tập trung vào **nhánh hứa hẹn** thay vì duyệt đều toàn bộ cây như Minimax.

## Khởi tạo

| Tham số | Mặc định | Ý nghĩa |
|---|---|---|
| `iterations` | 1000 | Số vòng lặp 4 bước mỗi lần gọi `get_move` |
| `c` | √2 ≈ 1.414 | Hằng số khám phá trong UCT |
| `rollout_fn` | `random_rollout` | Hàm simulation; thay bằng `heuristic_rollout` để mạnh hơn |

---

## `get_move(board) → (row, col)`

1. Tạo **root node** từ board hiện tại.
2. Lặp `iterations` lần, mỗi vòng thực hiện 4 bước MCTS.
3. Trả về nước đi của **con được thăm nhiều nhất** (`most_visited_child`).

Dùng số lần thăm (N) thay vì UCT score khi chọn nước cuối cùng vì N ổn định hơn — ít bị ảnh hưởng bởi một vài simulation may mắn hay xui rủi.

---

## 4 Bước MCTS

### 1 — Selection (`_select`)

Đi xuống cây theo **UCT score** cho đến khi gặp:
- Nút **chưa fully expanded** → dừng để Expand.
- Nút **terminal** → dừng, tính kết quả trực tiếp.

Không fully expanded nghĩa là còn nước chưa thử → có thể mở rộng thêm.

### 2 — Expansion (`node.expand()`)

Lấy một nước từ `untried`, tạo board mới, thêm nút con vào cây. Trả về nút con để tiếp tục Simulation.

### 3 — Simulation (`rollout_fn`)

Từ nút mới, mô phỏng đến khi ván kết thúc bằng `rollout_fn`. Trả về `{1.0, 0.5, 0.0}` từ góc nhìn `node.player`.

Nếu nút là terminal ngay → tính kết quả trực tiếp qua `_terminal_result`, không cần rollout.

### 4 — Backpropagation (`_backpropagate`)

Cập nhật `N` và `W` từ nút vừa expand **ngược lên đến gốc**:

- Mỗi bước lên cha: `result = 1 - result` (đổi góc nhìn — cha và con là đối thủ nhau).
- Nút gốc chỉ cập nhật `N`, không cộng `W` (gốc không có nước đi nên không thuộc về ai).

**Tại sao đảo result khi backprop?** W tại mỗi nút lưu điểm từ góc nhìn **người đã đánh nước dẫn đến nút đó** (`node.player`). Khi UCT chọn con, nó tìm con tốt nhất cho cha — mà cha và con là đối thủ nhau — nên cần đảo kết quả khi đi ngược lên.

---

## `get_root_stats() → list[dict]`

Chạy MCTS và trả về thống kê `{move, W, N, W/N}` của các nút con gốc, sắp xếp theo `N` giảm dần. Dùng để phân tích và so sánh trong thực nghiệm.

---

## So sánh với Minimax

| | Minimax / Alpha-Beta | MCTS |
|---|---|---|
| Chiến lược | Duyệt cây hệ thống (DFS) | Lấy mẫu có hướng dẫn (UCT) |
| Cần hàm evaluate | Bắt buộc | Không bắt buộc (rollout thay thế) |
| Đảm bảo tối ưu | Có (nếu đủ depth) | Không (hội tụ khi iterations → ∞) |
| Bàn lớn | Chậm (bùng nổ tổ hợp) | Tốt hơn (tập trung nhánh hứa hẹn) |
| Điều chỉnh | `depth`, `eval_fn` | `iterations`, `c`, `rollout_fn` |
