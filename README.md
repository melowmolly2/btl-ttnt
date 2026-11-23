# BTL Trí Tuệ Nhân Tạo — Tic-Tac-Toe AI

**Môn học:** Trí Tuệ Nhân Tạo  
**Nhóm thực hiện:** Phạm Thiên Minh, Lục Gia Bảo (UET-VNU)  
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
│   │   └── rollout.py      # Rollout ngẫu nhiên và heuristic (MAX_ROLLOUT_STEPS=30)
│   └── utils/          # Tiện ích chung
│       ├── evaluate.py     # Hàm lượng giá (evaluation function)
│       └── visualize.py    # Vẽ đồ thị kết quả thực nghiệm
├── experiments/        # Script chạy thực nghiệm, lưu kết quả
│   ├── run_minimax_experiment.py     # So sánh Minimax vs Alpha-Beta (số nút)
│   ├── run_mcts_experiment.py        # Khảo sát c, iterations, tỷ lệ thắng
│   ├── run_rollout_experiment.py     # So sánh rollout ngẫu nhiên vs heuristic
│   ├── run_never_lose_experiment.py  # Kiểm chứng MCTS không thua trên 3×3
│   ├── run_root_stats.py             # Thống kê W, N, W/N tại nút gốc
│   ├── run_uct_variants_experiment.py # So sánh biến thể UCT & Progressive Bias
│   └── results/                      # JSON kết quả thực nghiệm
├── giai thich tung file/             # Tài liệu giải thích chi tiết từng module
├── report/                           # Bản report IEEE conference paper
│   ├── report.md                     # Bản nháp Markdown
│   ├── report.tex / report.pdf       # Bản IEEE tiếng Anh (nộp chính)
│   └── report_vi.tex / report_vi.pdf # Bản dịch tiếng Việt
├── assets/
│   └── figures/                      # Đồ thị kết quả cho report
├── main.py                           # Entry point CLI
├── ui.py                             # Giao diện đồ họa Tkinter
├── requirements.txt                  # Thư viện Python cần thiết
└── README.md                         # File này
```

---

## Yêu cầu cài đặt

```bash
pip install -r requirements.txt
```

## Chạy game & thực nghiệm

```bash
# Chơi với AI qua giao diện đồ họa Tkinter (khuyến nghị cho demo)
python ui.py

# Chơi với AI qua terminal (CLI)
python main.py

# Chạy thực nghiệm Minimax vs Alpha-Beta
python experiments/run_minimax_experiment.py

# Chạy thực nghiệm MCTS (khảo sát c và iterations)
python experiments/run_mcts_experiment.py

# So sánh rollout ngẫu nhiên vs heuristic
python experiments/run_rollout_experiment.py

# Kiểm chứng MCTS không thua trên 3×3 (vs Alpha-Beta depth 9 & Random)
python experiments/run_never_lose_experiment.py

# Xuất bảng W, N, W/N tại nút gốc
python experiments/run_root_stats.py

# So sánh các biến thể UCT và cải tiến Progressive Bias
python experiments/run_uct_variants_experiment.py
```

---

## Các thuật toán triển khai

### 1. Minimax + Alpha-Beta Pruning

- Duyệt cây trò chơi đệ quy (Minimax)
- Cắt tỉa Alpha-Beta để giảm số nút cần duyệt
- Có giới hạn độ sâu (`max_depth`) + hàm lượng giá (`evaluate`)

### 2. MCTS + UCT

Lặp lại 4 bước:

1. **Selection:** chọn nút lá theo UCT
2. **Expansion:** mở rộng nút mới
3. **Simulation:** rollout ngẫu nhiên / heuristic (giới hạn `MAX_ROLLOUT_STEPS = 30`)
4. **Backpropagation:** cập nhật ngược W, N

Công thức UCT:

$$
UCT_i = \frac{W_i}{N_i} + c \sqrt{\frac{\ln N_{parent}}{N_i}}
$$

---

## Checklist hoàn thành

- [x] Tic-Tac-Toe 5 quân thẳng hàng (bàn N×N)
- [x] Minimax cơ bản
- [x] Alpha-Beta Pruning
- [x] MCTS + UCT
- [x] Thực nghiệm c ∈ {0.5, 1.0, 1.4, 2.0} (3×3 và 15×15)
- [x] Kiểm chứng không thua trên 3×3 (vs Alpha-Beta depth 9 & Random)
- [x] Rollout heuristic
- [x] Đồ thị kết quả & bảng W, N, W/N tại nút gốc
- [x] Giao diện Tkinter (`ui.py`)
- [x] (Bonus) Phân tích toán học UCT (trong `report/report.md` & `report.tex`)
- [x] (Bonus) Thử nghiệm biến thể UCT & cải tiến Progressive Bias
- [x] Hoàn thiện PDF IEEE (`report/report.pdf` & `report/report_vi.pdf`)
- [ ] Demo & vấn đáp
