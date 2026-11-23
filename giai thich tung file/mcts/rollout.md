# Rollout — Bước Simulation trong MCTS

Sau khi Expansion tạo nút mới, Simulation **mô phỏng ván đấu tối đa `MAX_ROLLOUT_STEPS = 30` nước** để ước lượng giá trị của nút đó mà không cần duyệt toàn bộ cây.

Trả về: `1.0` (thắng), `0.5` (hòa hoặc hết 30 bước chưa phân thắng bại), `0.0` (thua) từ góc nhìn `player` truyền vào.

---

## `random_rollout(board, player) → float`

Mỗi lượt chọn ngẫu nhiên một nước hợp lệ cho đến khi ván kết thúc hoặc đạt `MAX_ROLLOUT_STEPS = 30` nước.

- **Ưu điểm**: Đơn giản, rất nhanh mỗi iteration.
- **Nhược điểm**: Cần nhiều iterations để hội tụ — trên bàn 15×15, phần lớn simulation chạm giới hạn 30 bước trước khi có 5 quân thẳng hàng nên trả về `0.5`.

---

## `heuristic_rollout(board, player) → float`

Mỗi lượt chọn nước theo thứ tự ưu tiên (tối đa `MAX_ROLLOUT_STEPS = 30` nước):

1. **Thắng ngay**: Có nước nào đánh vào là thắng → chọn ngay.
2. **Chặn đối thủ thắng**: Đối thủ có nước thắng ngay → chặn.
3. **Ngẫu nhiên**: Không có trường hợp đặc biệt → chọn random.

- **Ưu điểm**: Mô phỏng sát thực tế hơn, hội tụ nhanh hơn, win rate cao hơn với cùng số iterations.
- **Nhược điểm**: Mỗi iteration chậm hơn do phải kiểm tra thắng/thua cho từng nước.
- **Nguồn gốc**: Tiền thân của policy network và value network trong AlphaGo/AlphaZero.

---

## `_pick_smart_move(board)` (nội bộ)

Hàm phụ trợ cho `heuristic_rollout`:

- **Ưu tiên 1**: Với mỗi nước hợp lệ, ghi tay quân mình vào `board.board[r,c]` và `move_history`, gọi `_check_win` → nếu thắng thì hoàn tác và trả về ngay.
- **Ưu tiên 2**: Tương tự với quân đối thủ → nếu đối thủ thắng thì hoàn tác và trả về nước đó để chặn.

**Tại sao không dùng `clone` hay `make_move`?** `clone` tạo bản sao cho mọi nước rất chậm; `make_move` đổi `current_player`. Ghi tay rồi hoàn tác thủ công tránh cả hai overhead.

---

## `_result(board, player) → float` (nội bộ)

Chuyển đổi trạng thái sau rollout thành điểm số:

```
1.0  nếu  board.winner == player       # thắng
0.0  nếu  board.winner is not None     # đối thủ thắng
0.5                                    # hòa hoặc hết MAX_ROLLOUT_STEPS chưa ai thắng
```
