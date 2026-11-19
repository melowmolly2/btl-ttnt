# Evaluate — Hàm lượng giá (Heuristic)

Dùng cho Minimax (trả về điểm khi hết `depth`) và rollout heuristic trong MCTS khi cần ước lượng tình thế bàn cờ mà không cần duyệt đến trạng thái kết thúc.

---

## Ý tưởng tổng quan

```
evaluate(board, perspective) = my_total_score − opponent_total_score
```

Quét toàn bộ bàn cờ theo 4 hướng (ngang, dọc, chéo chính, chéo phụ). Trên mỗi đường, tìm các chuỗi quân liên tiếp rồi tra bảng điểm theo `(độ_dài, số_đầu_mở)`.

---

## Bảng điểm

| Độ dài chuỗi | Số đầu mở | Điểm |
|:---:|:---:|---:|
| 5 | 1 hoặc 2 | 100,000 |
| 4 | 2 | 50,000 |
| 4 | 1 | 5,000 |
| 3 | 2 | 2,000 |
| 3 | 1 | 200 |
| 2 | 2 | 100 |
| 2 | 1 | 10 |
| 1 | 2 | 5 |
| 1 | 1 | 1 |

### Tại sao điểm tăng phi tuyến theo độ dài?

Chuỗi dài không chỉ "dài hơn" mà **nguy hiểm hơn theo cấp số nhân**. Chuỗi 4 mở 2 đầu gần như thắng chắc (50,000) trong khi chuỗi 2 gần như vô hại (10) — khoảng cách điểm lớn ép Minimax ưu tiên đúng mức độ đe dọa.

### Tại sao mở 2 đầu chênh gấp 10× so với mở 1 đầu?

Mở 2 đầu có nghĩa đối thủ phải **chặn cả hai đầu** nhưng chỉ có **một nước** để đánh. Ví dụ: `_ X X X X _` — đối thủ không thể chặn cả hai đầu trong một lượt → thua chắc.

---

## `_count_space(line, pos, direction) → int`

Đếm số ô EMPTY liên tiếp từ `pos` theo hướng `direction` (+1 hoặc -1). Dùng để tính không gian trống ở hai phía chuỗi.

---

## `_score_line(line, player, win_len) → int`

Tính điểm cho `player` trên một đường 1D.

**Thuật toán:**

1. Quét từ trái sang phải, tìm vị trí bắt đầu chuỗi quân của `player`.
2. Đếm độ dài chuỗi `length`.
3. Đếm ô trống hai phía: `space_left`, `space_right`.
4. Nếu `length + total_space < win_len` → chuỗi bị chặn hoàn toàn, không thể thắng → bỏ qua (0 điểm).
5. Đếm số đầu mở (đầu kề ô EMPTY).
6. Nếu `length + total_space == win_len` → chỉ đủ chỗ đi một hướng → tối đa 1 đầu mở.
7. Tra bảng điểm theo `(min(length, 5), open_ends)`.

**Ví dụ (win_len = 5):**

| Tình huống | total_space | open_ends | Điểm |
|---|:---:|:---:|---:|
| `O X X X O` | 0 | 0 | 0 (bị chặn 2 đầu, 0+3 < 5) |
| `O . X X X . O` | 2 | 2 → min(2,1)=1 | 200 (3,1) |
| `O . X X X . .` | 3 | 2 | 2,000 (3,2) |
| `. . X X X . .` | 4 | 2 | 2,000 (3,2) |

---

## `_total_score(board, player) → int`

Tổng điểm của `player` trên toàn bộ bàn cờ, quét 4 hướng:
- **Ngang**: từng hàng `b[r, :]`
- **Dọc**: từng cột `b[:, c]`
- **Chéo chính (↘)**: `b.diagonal(k)` cho các k đủ dài
- **Chéo phụ (↙)**: lật bảng ngang (`np.fliplr`) rồi lấy chéo chính

---

## `evaluate(board, perspective) → float`

Hàm lượng giá cuối cùng, trả về:

| Tình huống | Kết quả |
|---|---:|
| `perspective` thắng | +1,000,000 |
| `perspective` thua | −1,000,000 |
| Hòa | 0 |
| Chưa kết thúc | `my_score − opp_score` |

Điểm tuyệt đối (±1,000,000) lớn hơn mọi điểm heuristic có thể có → đảm bảo Minimax luôn ưu tiên thắng/tránh thua hơn bất kỳ lợi thế vị trí nào.
