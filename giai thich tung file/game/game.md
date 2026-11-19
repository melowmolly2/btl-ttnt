# Game — Vòng lặp ván đấu

Module điều phối một ván đấu hoàn chỉnh: Human vs Human, Human vs AI, hoặc AI vs AI.

## Hàm tiện ích

### `player_symbol(player) → str`
Chuyển `X (1)` → `"X"`, `O (-1)` → `"O"`. Dùng để in thông báo ra terminal.

---

### `human_move(board)`
Đọc nước đi từ bàn phím (định dạng `hàng cột`, ví dụ `7 7`).

Lặp lại cho đến khi nhận được nước hợp lệ — bắt cả lỗi định dạng (`ValueError`) lẫn ô đã có quân.

---

## `play_game` — Vòng lặp chính

```python
play_game(ai_x=None, ai_o=None, board_size=15, win_len=5, verbose=True) → int
```

Chạy một ván đấu hoàn chỉnh, trả về `X (1)`, `O (-1)`, hoặc `0` (hòa).

| Tham số | Ý nghĩa |
|---|---|
| `ai_x` | `None` = người chơi; `callable(board) → (row, col)` = AI điều khiển quân X |
| `ai_o` | Tương tự cho quân O |
| `board_size` | Kích thước bàn cờ |
| `win_len` | Số quân liên tiếp để thắng |
| `verbose` | In bàn cờ và thông báo ra terminal sau mỗi nước |

**Luồng xử lý:**

1. Tạo `Board` mới.
2. Map `{X: ai_x, O: ai_o}` để tra agent theo lượt hiện tại.
3. Lặp cho đến `board.is_terminal`:
   - In bàn cờ nếu `verbose`.
   - Nhìn vào `agents[board.current_player]`:
     - `None` → gọi `human_move()`, chờ người nhập.
     - callable → gọi `agent(board)` lấy `(row, col)`, rồi `make_move()`.
4. In kết quả cuối và trả về `board.winner` (hoặc `0` nếu hòa).

**Lưu ý khi in tên người chơi vừa đánh:** Sau `make_move()`, `current_player` đã đổi sang người tiếp theo, nên phải lấy `-board.current_player` để in đúng tên người vừa đánh.
