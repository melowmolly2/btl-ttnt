# Minimax

Thuật toán tìm kiếm cây trò chơi kinh điển. Duyệt DFS toàn bộ cây đến `max_depth`, chọn nước đi tối ưu với giả định **cả hai bên đều chơi tốt nhất**.

## Khởi tạo

| Tham số | Mặc định | Ý nghĩa |
|---|---|---|
| `max_depth` | 3 | Giới hạn độ sâu tìm kiếm |
| `eval_fn` | None | Hàm lượng giá `(Board, perspective) → float`; dùng hàm đơn giản nếu None |
| `nodes_visited` | 0 | Đếm số nút đã duyệt — reset mỗi lần gọi `get_move`, dùng để so sánh thực nghiệm với Alpha-Beta |

---

## `get_move(board) → (row, col)`

Trả về nước đi tốt nhất. **Đỉnh gốc luôn là đỉnh Max** (ta đang tìm nước tốt nhất cho mình).

Với mỗi nước hợp lệ từ trạng thái hiện tại:
1. Clone board, thực hiện nước đó.
2. Gọi `_minimax` với `depth = max_depth - 1`, `is_maximizing = False` (lượt đối thủ).
3. Chọn nước có điểm cao nhất.

---

## `_minimax(board, depth, is_maximizing, me) → float`

Hàm đệ quy DFS chính.

**Điều kiện dừng**: `board.is_terminal` hoặc `depth == 0` → trả về `_evaluate(board, me)`.

**Đỉnh Max** (`is_maximizing = True` — lượt của ta):
- Duyệt tất cả nước hợp lệ, gọi đệ quy với `is_maximizing = False`.
- Trả về **max** trong các điểm con.

**Đỉnh Min** (`is_maximizing = False` — lượt đối thủ):
- Duyệt tất cả nước hợp lệ, gọi đệ quy với `is_maximizing = True`.
- Trả về **min** trong các điểm con (đối thủ chọn nước tệ nhất cho ta).

```
get_move (Max, depth=3)
├── nước A → _minimax (Min, depth=2)
│           ├── nước A1 → _minimax (Max, depth=1)
│           │             ├── nước A1a → evaluate()
│           │             └── nước A1b → evaluate()
│           └── nước A2 → _minimax (Max, depth=1) → ...
└── nước B → _minimax (Min, depth=2) → ...
```

---

## `_evaluate(board, me) → float`

Nếu có `eval_fn` → dùng nó. Nếu không, dùng hàm mặc định:
- `+1_000_000` nếu `me` thắng
- `-1_000_000` nếu `me` thua
- `0` các trường hợp còn lại

Trong project này `eval_fn = evaluate` từ `utils/evaluate.py`, cho điểm trung gian phản ánh tình thế bàn cờ.
