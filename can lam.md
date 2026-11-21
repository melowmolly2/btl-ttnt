## Chưa làm / Chưa rõ ❓

### Bắt buộc (ảnh hưởng điểm)

1. **Chạy thực nghiệm thực sự** — các file experiment đã viết nhưng chưa rõ đã chạy và có kết quả chưa. Cần có số liệu thực trong `experiments/results/`.
2. **Kiểm chứng MCTS không bao giờ thua trên 3×3** — hướng dẫn ghi rõ *"kiểm chứng rằng với Tic-Tac-Toe, thuật toán không bao giờ thua"*. Cần chạy MCTS vs Random (hoặc vs Minimax) trên bàn 3×3 với đủ iterations và show kết quả.
3. **Report IEEE** — sản phẩm chính của bài, cần viết đủ 4–5 trang tiếng Anh gồm Abstract, Intro, Problem, Method, Experiments, Discussion.

### Bonus (nếu muốn > 8.5 điểm)

4. **Phân tích toán học UCT** — giải thích cơ sở từ Multi-Armed Bandit / UCB1, tại sao có `ln` và `√`.
5. **Thử biến thể UCT** — bỏ căn, thay `ln` bằng `log2`, so sánh winrate.
6. **Cải tiến thuật toán mô phỏng** — đã có heuristic rollout, nhưng nếu có thêm biến thể thứ 3 thì mạnh hơn.
7. **Cờ tướng** — bonus lớn nhất, xác định điểm trên 9
