# BTL Trí Tuệ Nhân Tạo — Tic-Tac-Toe AI

**Môn học:** Trí Tuệ Nhân Tạo  
**Deadline:** 10/12/2026  
**Hình thức:** Report IEEE + GitHub repo + Demo + Vấn đáp

---

## Cấu trúc thư mục

```
btl-ttnt/
├── src/
│   ├── game/           # Logic bàn cờ, luật chơi
│   │   ├── board.py        # Lớp Board: trạng thái bàn cờ, kiểm tra thắng/thua
│   │   └── game.py         # Vòng lặp game chính, giao diện console
│   ├── minimax/        # Thuật toán Minimax + Alpha-Beta
│   │   ├── minimax.py      # Minimax thuần
│   │   └── alpha_beta.py   # Minimax + cắt tỉa Alpha-Beta
│   ├── mcts/           # Thuật toán MCTS + UCT
│   │   ├── node.py         # Lớp Node của cây MCTS
│   │   ├── mcts.py         # MCTS với UCT chính
│   │   └── rollout.py      # Rollout ngẫu nhiên và heuristic
│   └── utils/          # Tiện ích chung
│       ├── evaluate.py     # Hàm lượng giá (evaluation function)
│       └── visualize.py    # Vẽ đồ thị kết quả thực nghiệm
├── experiments/        # Script chạy thực nghiệm, lưu kết quả
│   ├── run_minimax_experiment.py   # So sánh Minimax vs Alpha-Beta (số nút)
│   ├── run_mcts_experiment.py      # Khảo sát c, iterations, tỷ lệ thắng
│   ├── run_rollout_experiment.py   # So sánh rollout ngẫu nhiên vs heuristic
│   └── results/            # CSV / JSON kết quả thực nghiệm
├── report/             # Bản report IEEE conference paper
│   └── report.md           # Draft report tiếng Anh
├── assets/
│   └── figures/        # Đồ thị, ảnh demo cho report
├── main.py             # Entry point: chọn chế độ chơi, chọn AI
├── requirements.txt    # Thư viện Python cần thiết
└── README.md           # File này
```

---

## Yêu cầu cài đặt

```bash
pip install -r requirements.txt
```

## Chạy game

```bash
# Chơi với AI (chọn chế độ khi chạy)
python main.py

# Chạy thực nghiệm Minimax vs Alpha-Beta
python experiments/run_minimax_experiment.py

# Chạy thực nghiệm MCTS (khảo sát c và iterations)
python experiments/run_mcts_experiment.py

# So sánh rollout ngẫu nhiên vs heuristic
python experiments/run_rollout_experiment.py
```

---

## Các thuật toán triển khai

### 1. Minimax + Alpha-Beta Pruning
- Duyệt cây trò chơi đệ quy (Minimax)
- Cắt tỉa Alpha-Beta để giảm số nút cần duyệt
- Có giới hạn độ sâu (depth limit) + hàm lượng giá

### 2. MCTS + UCT
Lặp lại 4 bước:
1. **Selection:** chọn nút lá theo UCT
2. **Expansion:** mở rộng nút mới
3. **Simulation:** rollout ngẫu nhiên / heuristic
4. **Backpropagation:** cập nhật ngược W, N

Công thức UCT:
$$UCT_i = \frac{W_i}{N_i} + c \sqrt{\frac{\ln N_{parent}}{N_i}}$$

---

## Kết quả thực nghiệm cần có (cho report)

- [ ] Bảng số nút Minimax vs Alpha-Beta
- [ ] Bảng thắng/hòa/thua MCTS (3×3 và bàn 5 quân thẳng hàng)
- [ ] Đồ thị: số iterations – tỷ lệ thắng, với c ∈ {0.5, 1.0, 1.4, 2.0}
- [ ] Bảng W, N, W/N tại nút gốc
- [ ] So sánh rollout ngẫu nhiên vs heuristic
- [ ] Giải thích vì sao chọn theo N lớn nhất thay vì W/N lớn nhất

---

## Checklist hoàn thành

- [ ] Tic-Tac-Toe 5 quân thẳng hàng (bàn NxN)
- [ ] Minimax cơ bản
- [ ] Alpha-Beta Pruning
- [ ] MCTS + UCT
- [ ] Thực nghiệm c ∈ {0.5, 1.0, 1.4, 2.0}
- [ ] Rollout heuristic
- [ ] Đồ thị kết quả
- [ ] Report ≥ 4–5 trang IEEE format
- [ ] Demo
- [ ] (Bonus) Phân tích toán học UCT
- [ ] (Bonus) Biến thể UCT
