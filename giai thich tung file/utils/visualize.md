# Visualize — Vẽ đồ thị kết quả thực nghiệm

Module tạo và lưu đồ thị so sánh các thuật toán bằng `matplotlib`. Ảnh lưu vào `assets/figures/` (tạo tự động nếu chưa tồn tại).

---

## `plot_winrate_vs_iterations(data, save=True)`

**Mục đích**: So sánh tỷ lệ thắng của MCTS theo số iterations với nhiều giá trị `c` khác nhau.

**Input**: `data = {c_value: {iterations: winrate}}`

Mỗi giá trị `c` vẽ một đường trên đồ thị (trục X: iterations, trục Y: tỷ lệ thắng %).

**Output**: File `winrate_vs_iterations.png` và hiển thị cửa sổ đồ thị.

Dùng để trả lời: *Cần bao nhiêu iterations để MCTS đủ mạnh? Giá trị `c` nào cho kết quả tốt nhất?*

---

## `plot_nodes_comparison(minimax_nodes, ab_nodes, save=True)`

**Mục đích**: So sánh số nút phải duyệt giữa Minimax và Alpha-Beta theo từng depth.

**Input**:
- `minimax_nodes = {depth: số_nút}`
- `ab_nodes = {depth: số_nút}`

Vẽ **biểu đồ cột đôi** (grouped bar chart) — mỗi depth một cặp cột song song.

**Output**: File `nodes_minimax_vs_ab.png` và hiển thị cửa sổ đồ thị.

Dùng để minh họa trực quan hiệu quả cắt tỉa: cùng depth, Alpha-Beta duyệt ít nút hơn đáng kể.

---

## `FIGURES_DIR`

```
src/utils/visualize.py  →  ../../assets/figures/
                        =  assets/figures/  (từ gốc project)
```

Thư mục được tạo tự động bằng `os.makedirs(..., exist_ok=True)` nếu chưa tồn tại.
