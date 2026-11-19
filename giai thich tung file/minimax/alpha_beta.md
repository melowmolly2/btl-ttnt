# Minimax với cắt tỉa Alpha-Beta

Cùng logic với Minimax thuần nhưng thêm hai tham số `alpha` và `beta` để **bỏ qua các nhánh không thể ảnh hưởng đến kết quả**. Không thay đổi nước đi được chọn, chỉ giảm số nút cần duyệt.

## Khởi tạo

Giống `MinimaxAgent`: `max_depth`, `eval_fn`, `nodes_visited`.

---

## `get_move(board) → (row, col)`

Tương tự Minimax, đỉnh gốc là Max. Điểm khác: khởi tạo `alpha = -∞`, `beta = +∞` và truyền vào `_alpha_beta`. Cập nhật `alpha` sau mỗi nước con ở tầng gốc.

---

## `_alpha_beta(board, depth, alpha, beta, is_maximizing, me) → float`

### Ý nghĩa alpha, beta

| Biến | Ý nghĩa |
|---|---|
| `alpha` | Điểm tốt nhất **Max** đảm bảo được (tính từ gốc đến đây). Khởi đầu `-∞`. |
| `beta` | Điểm tốt nhất **Min** đảm bảo được (tính từ gốc đến đây). Khởi đầu `+∞`. |

### Tại đỉnh Max

Duyệt từng con, cập nhật `alpha = max(alpha, score_con)`.

Nếu `alpha >= beta` → **cắt tỉa beta**: Min ở nút cha đã có lựa chọn tốt hơn (≤ alpha cũ), Max không thể "leo lên" được nhánh này → bỏ qua toàn bộ anh em còn lại.

### Tại đỉnh Min

Duyệt từng con, cập nhật `beta = min(beta, score_con)`.

Nếu `alpha >= beta` → **cắt tỉa alpha**: Max ở nút cha đã có lựa chọn tốt hơn (≥ beta cũ) → Min không cần xét thêm.

### Ví dụ trực quan

```
Root (Max, alpha=-∞)
├── A (Min) → trả về 5   →  alpha = 5
└── B (Min, beta=+∞)
    ├── con1 → 8          →  beta  = 8   [chưa cắt, 8 > alpha=5]
    └── con2 → 3          →  beta  = 3   →  beta(3) ≤ alpha(5)  →  CẮT!
```

Min tại B sẽ chọn ≤ 3, nhưng Max ở Root đã có nhánh A cho 5 → B sẽ không bao giờ được chọn → không cần duyệt thêm con của B.

---

## Hiệu quả

| Trường hợp | Độ phức tạp |
|---|---|
| Tốt nhất (nhánh sắp xếp tối ưu) | O(b^(d/2)) — độ sâu hiệu dụng tăng gấp đôi |
| Trung bình | O(b^(3d/4)) |
| Xấu nhất (nhánh sắp xếp ngược) | O(b^d) — giống Minimax thuần |

Trong cờ caro, thứ tự duyệt nước ảnh hưởng lớn đến số nhánh bị cắt — đây là lý do sắp xếp nước đi (move ordering) là kỹ thuật quan trọng kết hợp với Alpha-Beta.
