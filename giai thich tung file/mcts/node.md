# MCTSNode — Nút trong cây MCTS

Mỗi nút đại diện cho một **trạng thái bàn cờ** cùng thống kê tích lũy từ các lần mô phỏng đi qua nút đó.

## Thuộc tính

| Thuộc tính | Kiểu | Ý nghĩa |
|---|---|---|
| `board` | Board | Trạng thái bàn cờ tại nút này |
| `parent` | MCTSNode \| None | Nút cha; None nếu là gốc |
| `move` | (row, col) \| None | Nước đi dẫn đến nút này; None nếu là gốc |
| `children` | list[MCTSNode] | Danh sách nút con đã mở rộng |
| `W` | float | Tổng điểm tích lũy (1=thắng, 0.5=hòa, 0=thua) |
| `N` | int | Số lần nút này được thăm |
| `untried` | list | Nước hợp lệ chưa có nút con tương ứng |
| `player` | int | Người chơi **đã đánh** nước dẫn đến nút này |

**Lưu ý `player`**: Sau `make_move()`, board đổi lượt sang người tiếp theo, nên `player = -board.current_player`. Cần thiết để backpropagation biết W tích vào nút này là từ góc nhìn của ai.

---

## UCT Score & Các biến thể

Công thức chuẩn (`variant="standard"`):

```
UCT_i = W_i/N_i  +  c × √(ln(N_parent) / N_i)
```

| Thành phần | Tên | Ý nghĩa |
|---|---|---|
| `W_i/N_i` | Exploitation | Tỷ lệ thắng — khai thác nút đã biết tốt |
| `c × √(...)` | Exploration | Khuyến khích thăm nút ít được ghé |

- Nút chưa được thăm (`N = 0`) → trả về `+∞` để được ưu tiên tuyệt đối.
- `c = √2 ≈ 1.414` theo lý thuyết UCB1 — có thể điều chỉnh qua thực nghiệm.

Ngoài ra `uct_score(c, variant)` hỗ trợ thêm 4 biến thể để thực nghiệm:
- `no_sqrt`: `W/N + c * (ln(N_p) / N)` (bỏ căn)
- `no_ln`: `W/N + c * sqrt(N_p / N)` (bỏ `ln`)
- `linear`: `W/N + c * (N_p / N)` (bỏ cả căn và `ln`)
- `progressive_bias`: `W/N + c * sqrt(ln(N_p) / N) + H / (N + 1)` với `H = 0.5 + 0.5 * tanh(evaluate / 5000)` (lazy-cache trong `_get_heuristic()`), định hướng giai đoạn đầu rồi tắt dần khi `N` lớn.

---

## Các phương thức

### `is_fully_expanded`
`True` khi `untried` rỗng — tất cả nước đi hợp lệ đã có nút con. → Selection sẽ đi sâu hơn thay vì dừng để Expand.

### `is_terminal`
Truyền thẳng từ `board.is_terminal`.

### `best_child(c) → MCTSNode`
Trả về con có UCT score cao nhất. Dùng trong bước **Selection** để dẫn đường xuống cây.

### `most_visited_child() → MCTSNode`
Trả về con được thăm nhiều nhất (`N` lớn nhất). Dùng khi **chọn nước đi thực tế** sau khi MCTS hoàn tất — ổn định hơn UCT score vì ít bị nhiễu bởi một vài simulation may mắn.

### `expand() → MCTSNode`
Lấy một nước từ `untried` (pop), tạo board mới, tạo MCTSNode con và thêm vào `children`. Trả về nút con để tiếp tục bước Simulation.

### `update(result)`
Cập nhật `N += 1` và `W += result`. Phương thức phụ — backpropagation thực tế được xử lý tập trung trong `MCTSAgent._backpropagate()`.
