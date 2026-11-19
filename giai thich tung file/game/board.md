# Board — Bàn cờ Caro

Lớp trung tâm của toàn bộ project. Lưu trạng thái bàn cờ và cung cấp các thao tác cơ bản cho cả Minimax lẫn MCTS.

## Hằng số

| Hằng | Giá trị | Ý nghĩa |
|---|---|---|
| `EMPTY` | 0 | Ô trống |
| `X` | 1 | Người chơi 1 (đi trước) |
| `O` | -1 | Người chơi 2 / AI |

Dùng giá trị `+1/-1` thay vì `1/2` để đổi lượt chỉ bằng phép nhân: `current_player = -current_player`.

## Khởi tạo

| Tham số | Mặc định | Ý nghĩa |
|---|---|---|
| `size` | 15 | Kích thước bàn cờ (n × n) |
| `win_len` | 5 | Số quân liên tiếp để thắng (Gomoku / Cờ caro) |
| `board` | zeros(n,n) | Mảng numpy 2D lưu trạng thái |
| `current_player` | X | Người chơi hiện tại |
| `move_history` | [] | Danh sách các nước đã đi (cả hai bên) |
| `_winner` | None | Người thắng, None nếu chưa có |

---

## Các phương thức

### `clone()`
Trả về bản sao **độc lập** của bàn cờ. Dùng trong Minimax và MCTS để thử nước đi mà không ảnh hưởng board gốc.

Copy `board` bằng `numpy.copy()` và `move_history` bằng slice `[:]` — đảm bảo hai chiều đều độc lập.

---

### `get_legal_moves()`
Trả về danh sách ô trống hợp lệ — không phải toàn bộ ô trống mà **chỉ những ô gần quân đã đặt** (radius = 2).

**Tại sao lọc?**
- Bàn 15×15 có tối đa 225 ô; duyệt tất cả làm cây tìm kiếm bùng nổ tổ hợp.
- Trong thực tế, nước đi có nghĩa luôn nằm gần quân đã có (tấn công, phòng thủ).
- Nước đi xa hoàn toàn không tạo mối đe dọa hay phòng thủ ngay lập tức.
- Radius = 2 (không phải 1) để AI phát hiện được chiến thuật kiểu `_ O _ O _` (quân cách nhau 1 ô).

**Trường hợp đặc biệt — bàn trống:**
Chỉ cho phép duy nhất **ô trung tâm**. Lý do: ô trung tâm có nhiều hướng tấn công nhất (4 hướng đều đủ dài), kiểm soát trung tâm tạo lợi thế chiến lược và rút ngắn không gian tìm kiếm ngay từ nước đầu.

---

### `get_all_empty()`
Trả về **mọi** ô trống, không lọc vùng lân cận. Dùng cho các thực nghiệm cần duyệt toàn bộ.

---

### `make_move(row, col) → bool`
Đặt quân của `current_player` vào ô `(row, col)`.

- Kiểm tra ô chưa có quân và ván chưa kết thúc.
- Ghi vào `board`, thêm vào `move_history`, kiểm tra thắng, đổi lượt.
- Trả về `True` nếu hợp lệ, `False` nếu không.

---

### `undo_move()`
Hủy nước đi cuối cùng — hoàn lại `board`, `move_history`, `current_player` và `_winner`.

Dùng trong Minimax **không clone** (duyệt in-place thay vì tạo bản sao). Sau khi duyệt xong một nhánh, cần hủy nước đó để duyệt sang nhánh khác trên cùng trạng thái. Nếu không hủy, các nhánh tiếp theo sẽ tính trên trạng thái sai.

*(Trong cài đặt hiện tại, Minimax dùng clone thay vì undo — nhưng `undo_move` vẫn được giữ để linh hoạt.)*

---

### `_check_win(row, col) → bool`
Kiểm tra quân vừa đặt tại `(row, col)` có tạo `win_len` quân liên tiếp không.

Duyệt 4 hướng: ngang `(0,1)`, dọc `(1,0)`, chéo chính `(1,1)`, chéo phụ `(1,-1)`. Mỗi hướng đếm liên tiếp cả hai phía từ điểm vừa đặt. Chỉ cần một hướng đạt `≥ win_len` là thắng.

---

### Properties

| Property | Trả về | Ý nghĩa |
|---|---|---|
| `winner` | X, O, hoặc None | Người thắng; None nếu chưa kết thúc |
| `is_draw` | bool | True khi bàn đầy mà không ai thắng |
| `is_terminal` | bool | True khi có người thắng hoặc hòa |

---

### `__str__()`
In bàn cờ ra terminal với tiêu đề cột và số hàng, dùng ký tự `.` (trống), `X`, `O`.
