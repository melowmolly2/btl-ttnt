# UI — Giao diện đồ họa Tkinter

Giao diện desktop chạy bằng `python ui.py` (dùng `tkinter` có sẵn trong Python, không cần cài thêm thư viện).

---

## `AgentWrapper`

Bọc các agent (`MinimaxAgent`, `AlphaBetaAgent`, `MCTSAgent`) để lưu thống kê sau mỗi nước đi mà không làm thay đổi API của agent gốc:

- **Minimax / Alpha-Beta**: lưu `nodes_visited` và nước đã chọn.
- **MCTS**: đọc `agent.last_root_stats[:3]` (top 3 nước có `N` cao nhất từ chính lần tìm kiếm vừa chạy, không chạy lại lần hai).

---

## `SetupScreen` — Màn hình cài đặt

Cửa sổ modal mở đầu tiên trước khi vào ván:

- **Bàn cờ**: chỉnh `size` (3–19, mặc định 15) và `win_len` (3–9, mặc định 5); kiểm tra `win_len <= size`.
- **Người chơi X / O**: chọn độc lập `Human`, `Minimax`, `Alpha-Beta`, hoặc `MCTS`.
- `_refresh(attr)`: tự động ẩn/hiện ô nhập tham số tương ứng (`Depth` cho Minimax/Alpha-Beta; `Iterations`, `C`, `Heuristic rollout` cho MCTS).

---

## `GameScreen` — Màn hình chơi chính

- **Panel trái**: hiển thị cấu hình X/O, trạng thái thắng/hòa/thua, lượt hiện tại, tọa độ nước trước và hộp **AI Stats** (`Nút duyệt` hoặc bảng `Move / N / W/N`).
- **Canvas bàn cờ**: vẽ lưới `n × n`, highlight ô vừa đánh bằng màu xanh nhạt (`LAST_MOVE`), click chuột để đặt quân khi đến lượt Human.
- **Chạy AI trên thread riêng** (`_maybe_ai_move`): gọi `wrapper.get_move(board)` trong `threading.Thread(daemon=True)` rồi cập nhật UI qua `root.after(0, ...)` để cửa sổ không bị đơ khi AI đang suy nghĩ.
- **Điều hướng**: nút `Ván mới` (reset cùng cấu hình), `Cài đặt` (quay lại `SetupScreen`), `Thoát`.
