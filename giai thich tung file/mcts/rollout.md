# Rollout — Bước Simulation trong MCTS

Sau khi Expansion tạo nút mới, Simulation **mô phỏng ván đấu đến khi kết thúc** để ước lượng giá trị của nút đó mà không cần duyệt toàn bộ cây.

Trả về: `1.0` (thắng), `0.5` (hòa), `0.0` (thua) từ góc nhìn `player` truyền vào.

---

## `random_rollout(board, player) → float`

Mỗi lượt chọn ngẫu nhiên một nước hợp lệ cho đến khi ván kết thúc.

- **Ưu điểm**: Đơn giản, rất nhanh mỗi iteration.
- **Nhược điểm**: Cần nhiều iterations để hội tụ — đặc biệt trên bàn lớn, một nước thắng ngay lập tức có thể bị bỏ qua vì chọn ngẫu nhiên.

---

## `heuristic_rollout(board, player) → float`

Mỗi lượt chọn nước theo thứ tự ưu tiên:

1. **Thắng ngay**: Có nước nào đánh vào là thắng → chọn ngay.
2. **Chặn đối thủ thắng**: Đối thủ có nước thắng ngay → chặn.
3. **Ngẫu nhiên**: Không có trường hợp đặc biệt → chọn random.

- **Ưu điểm**: Mô phỏng sát thực tế hơn, hội tụ nhanh hơn, win rate cao hơn với cùng số iterations.
- **Nhược điểm**: Mỗi iteration chậm hơn do phải kiểm tra thắng/thua cho từng nước.
- **Nguồn gốc**: Tiền thân của policy network và value network trong AlphaGo/AlphaZero.

---

## `_pick_smart_move(board)` (nội bộ)

Hàm phụ trợ cho `heuristic_rollout`:

- **Ưu tiên 1**: Thử từng nước hợp lệ, clone board, `make_move` → nếu `winner == me` thì trả về ngay.
- **Ưu tiên 2**: Với mỗi nước, ghi trực tiếp quân đối thủ vào `board.board[r,c]` và `move_history`, gọi `_check_win` → nếu đối thủ thắng thì hoàn tác và trả về nước đó để chặn.

**Tại sao không dùng `make_move` cho ưu tiên 2?** `make_move` đổi `current_player`, làm sai logic kiểm tra. Code ghi trực tiếp rồi hoàn tác thủ công để tránh tác dụng phụ.

---

## `_result(board, player) → float` (nội bộ)

Chuyển đổi trạng thái kết thúc thành điểm số:

```
1.0  nếu  board.winner == player   # thắng
0.5  nếu  board.is_draw            # hòa
0.0                                # thua
```
