# Bài tập lớn cho học phần AI để đánh giá giữa kỳ

## Các yêu cầu (có thể điều chỉnh)

- **Thời hạn làm:** 5 tuần (có thể điều chỉnh thêm) (deadline: 10/12/2026)
- **Sản phẩm:** report viết theo form IEEE conference paper (mặc định tiếng Anh) (min 4-5 trang) + GitHub repo.
- **Hình thức kiểm tra:** vấn đáp + hỏi code (~10-15 phút) + demo (tic-tac-toe)
- **Trần điểm:** Làm phần bắt buộc (Bài 1 + các nội dung trong phần gợi ý): 8-8.5 điểm. Làm thêm phần bonus: 10 điểm
- **Định nghĩa bonus:**
  - Phân tích rõ cơ sở toán học/lý thuyết của công thức UCT
  - Thử nghiệm các biến thể công thức UCT khác nhau (bỏ căn, $\ln$, ...)
  - Cải tiến công thức UCT
  - Làm thêm cờ tướng
  - Cải tiến thuật toán tính mô phỏng
  - Làm hẳn 1 bài toán mới, ưu tiên bài toán thực tế áp dụng AI (chính là bài 2)

## Bài 1 (Bắt buộc)

Viết chương trình trò chơi Tic-Tac-Toe (5 quân thẳng hàng thì thắng). Yêu cầu:

1. Sử dụng thuật toán MiniMax + Cắt tỉa Alpha-beta cho trò chơi trên.
2. Mở rộng bằng MCTS + UCT (Monte Carlo Tree Search + Upper Confidence Bound applied to Trees) cho Tic-Tac-Toe, kiểm chứng rằng với Tic-Tac-Toe, thuật toán không bao giờ thua.

$$
UCT_i = \underbrace{\frac{W_i}{N_i}}_{\text{Exploitation}} + c\,\underbrace{\sqrt{\frac{\ln N_{parent}}{N_i}}}_{\text{Exploration}}
$$

Trong đó:

- **Số hạng 1 (khai thác):** ưu tiên nước có tỷ lệ thắng cao.
- **Số hạng 2 (khám phá):** ưu tiên nước ít được thử. Số hạng này tăng dần khi nút cha được thăm nhiều mà nút con bị bỏ quên.
- **$c$:** hằng số cân bằng giữa hai số hạng. Giá trị lý thuyết là $\sqrt{2}$; thực tế cần tinh chỉnh.

Giải thích công thức của thuật toán:

- $i$: bước đi $i$ trong tổng số các bước có thể thực hiện trong trạng thái hiện tại.
- $W_i$: Số lần mà việc thực hiện bước $i$ sẽ dẫn đến chiến thắng.
- $N_i$: Tổng số lần bước $i$ được thử trong lượt đi ở trạng thái hiện tại.
- $N_{parent}$: Tổng số bước đã được thử ở trạng thái hiện tại.

### Ví dụ áp dụng thuật toán UCT

#### 1. Bản chất của UCT: Câu chuyện "Quán ăn ngon"

Hãy tưởng tượng bạn chuyển đến một thành phố mới và muốn tìm quán ăn ngon nhất:

- **Tận dụng (Exploitation):** Bạn đã ăn ở quán A 3 lần và thấy rất ngon. Bạn muốn tiếp tục quay lại quán A để đảm bảo có một bữa ăn ngon (chọn nước đi có tỷ lệ thắng cao nhất hiện tại).
- **Khai phá (Exploration):** Có quán B bạn chưa từng thử bao giờ. Biết đâu quán B còn ngon hơn quán A? Bạn chấp nhận rủi ro ăn thử quán B (khám phá các nước đi mới, ít được chọn).

Thuật toán UCT ra đời để **cân bằng hoàn hảo** hai yếu tố này qua công thức tính điểm cho mỗi nước đi:

$$
\text{Điểm UCT} = \frac{W_i}{N_i} + c \times \sqrt{\frac{\ln N}{N_i}}
$$

- **Phần 1: $\dfrac{W_i}{N_i}$ (Tận dụng: exploit)** — Tỷ lệ thắng hiện tại của nước đi đó (số trận thắng $W_i$ / số lần thử $N_i$). Phần này lớn nếu nước đi này "ngon".
- **Phần 2: $c \times \sqrt{\dfrac{\ln N}{N_i}}$ (Khai phá: explore)** — $N$ là tổng số lần bạn đã thử nghiệm tất cả các quán ăn, $N_i$ là số lần thử quán ăn cụ thể này. Nếu một quán ăn **rất ít được thử ($N_i$ nhỏ)**, phần Khai phá này sẽ trở nên **rất lớn**, ép máy tính phải vào thử quán đó xem sao.
- **$c$ là hằng số** (thường chọn bằng $\sqrt{2} \approx 1.41$), quyết định máy tính thích "an toàn" hay "phiêu lưu".

Mỗi lần máy tính cần quyết định, nó sẽ tính điểm UCT cho tất cả các lựa chọn có sẵn, và **chọn lựa chọn có điểm UCT cao nhất**.

#### 2. Bốn bước hoạt động của MCTS / UCT

Thuật toán UCT chạy lặp đi lặp lại hàng nghìn lần qua 4 bước sau để xây dựng một cây quyết định:

1. **Selection (Lựa chọn):** Từ trạng thái bàn cờ hiện tại, máy tính dùng công thức UCT để chọn các nước đi tiếp theo, đi xuống sâu dần cho đến khi gặp một "nút lá" (một nước đi chưa được khám phá hết các nhánh con).
2. **Expansion (Mở rộng):** Tại nút lá đó, máy tính tạo ra thêm một hoặc nhiều nước đi hợp lệ tiếp theo.
3. **Simulation (Mô phỏng / Rollout):** Từ nước đi mới tạo, máy tính sẽ **đánh ngẫu nhiên** (cả ta và địch đều đi bừa) cho đến khi trận đấu kết thúc (Thắng, Thua hoặc Hòa).
4. **Backpropagation (Cập nhật ngược):** Lấy kết quả của trận đấu ngẫu nhiên đó (ví dụ: Thắng = 1 điểm, Hòa = 0.5 điểm, Thua = 0 điểm) rồi cộng ngược lên tất cả các nước đi đã dẫn đến kết quả này. Tăng số lần thử $N_i$ lên 1, tăng $W_i$ nếu thắng.

#### 3. Thực hiện UCT trên trò chơi Tic-Tac-Toe

Hãy xem cách UCT vận hành trong một tình huống cụ thể của trò chơi Tic-Tac-Toe.

**Trạng thái ban đầu (Bàn cờ hiện tại)**

Đến lượt quân **X** đi. Bàn cờ đang như sau:

```text
 O | X | .
-----------
 . | O | .
-----------
 X | . | .
```

Lúc này, quân **X** có 5 vị trí trống để đi (ta gọi là 5 lựa chọn).

**Giả sử thuật toán đã chạy được một số vòng ($N = 20$ lần thử tổng cộng)**

Cây quyết định hiện tại trong bộ nhớ của máy tính lưu thông số của 5 lựa chọn này như sau (với $c = 1.41$):

- **Lựa chọn 1 (Ô giữa dưới):** Đã thử $N_1 = 10$ lần, thắng $W_1 = 7$ lần.
- **Lựa chọn 2 (Ô giữa trái):** Đã thử $N_2 = 8$ lần, thắng $W_2 = 2$ lần.
- **Lựa chọn 3 (Ô dưới phải):** Đã thử $N_3 = 1$ lần, thắng $W_3 = 0$ lần.
- **Lựa chọn 4 (Ô giữa phải):** Chưa thử bao giờ ($N_4 = 0$).
- **Lựa chọn 5 (Ô trên phải):** Chưa thử bao giờ ($N_5 = 0$).

**Thuật toán xử lý vòng tiếp theo (Vòng thứ 21)**

**Bước 1 & 2: Selection & Expansion**

- Theo quy tắc, các nước đi chưa từng thử bao giờ ($N = 0$) sẽ được **ưu tiên tối cao** để mở rộng cây. Máy tính thấy Lựa chọn 4 chưa thử.
- Máy tính quyết định **chọn Lựa chọn 4** (đặt X vào ô giữa phải).

**Bước 3: Simulation (Mô phỏng)**

Từ bàn cờ sau khi đi Lựa chọn 4:

```text
 O | X | .
-----------
 . | O | X  <-- Nước vừa chọn thử
-----------
 X | . | .
```

Máy tính bắt đầu tự đóng giả cả 2 người chơi và **đánh hoàn toàn ngẫu nhiên** (không tính toán) cho đến khi hết bài:

- Lượt O: đi ngẫu nhiên vào ô giữa trái.
- Lượt X: đi ngẫu nhiên vào ô trên phải.
- ... Giả sử sau vài nước đi ngẫu nhiên, **O thắng** (tức là X thua). Kết quả trận đấu này là **0 điểm** cho X.

**Bước 4: Backpropagation (Cập nhật ngược)**

Máy tính cập nhật lại dữ liệu của Lựa chọn 4:

- Số lần thử của Lựa chọn 4 tăng lên: $N_4 = 1$.
- Số trận thắng của Lựa chọn 4 giữ nguyên: $W_4 = 0$.
- Tổng số lần thử của toàn bộ hệ thống tăng lên: $N = 21$.

**Chuyện gì xảy ra ở vòng tiếp theo (Vòng thứ 22)?**

Bây giờ, tất cả các lựa chọn từ 1 đến 5 đều đã từng được thử ít nhất 1 lần. Máy tính sẽ dùng công thức UCT để so sánh.

Hãy tính thử điểm UCT của **Lựa chọn 1** và **Lựa chọn 3** để xem máy tính chọn cái nào:

- **Điểm UCT của Lựa chọn 1 (nước đi có vẻ tốt):**

  $$
  UCT_1 = \frac{7}{10} + 1.41 \times \sqrt{\frac{\ln 21}{10}} = 0.70 + 1.41 \times \sqrt{\frac{3.04}{10}} = 0.70 + 0.77 = 1.47
  $$

- **Điểm UCT của Lựa chọn 3 (nước đi mới thử 1 lần và thua):**

  $$
  UCT_3 = \frac{0}{1} + 1.41 \times \sqrt{\frac{\ln 21}{1}} = 0.00 + 1.41 \times \sqrt{3.04} = 0.00 + 2.45 = 2.45
  $$

**Kết quả bất ngờ:** Điểm $UCT_3$ ($2.45$) lớn hơn $UCT_1$ ($1.47$). Máy tính sẽ chọn **Lựa chọn 3** để đi tiếp và mô phỏng tiếp, chứ không chọn Lựa chọn 1 dù Lựa chọn 1 có tỷ lệ thắng cao ($0.70$).

**Tại sao lại thế?** Vì Lựa chọn 3 mới thử đúng 1 lần ($N_3 = 1$). Thuật toán cho rằng: *"Có thể lần trước thua chỉ là do ăn may thôi, nước đi này mới thử 1 lần nên ta chưa biết rõ bản chất, cần phải khám phá thêm trước khi loại bỏ nó!"*.

Sau hàng ngàn vòng lặp như vậy, các nước đi thực sự tệ sẽ dần lộ diện (số lần thử tăng lên nhưng tỷ lệ thắng không tăng, làm điểm UCT giảm xuống), còn các nước đi tốt sẽ liên tục được củng cố. Khi hết thời gian suy nghĩ, máy tính sẽ nhìn vào cây và chọn nước đi có **số lần thử $N_i$ nhiều nhất** hoặc **tỷ lệ thắng cao nhất** để đánh ngoài đời thực.

### Vì sao lại có căn bậc 2 và $\ln$?

Chúng được chứng minh toán học nghiêm ngặt để giải quyết bài toán Multi-Armed Bandit (bài toán phân phối tài nguyên cho các lựa chọn rủi ro).

3. **Thực nghiệm:** khảo sát ảnh hưởng của $c \in \{0.5,\ 1.0,\ 1.4,\ 2.0\}$ lên tỷ lệ thắng. Vẽ đồ thị giữa số iteration và tỷ lệ thắng.
4. **Phân tích:** giải thích vì sao chọn nước theo $N$ lớn nhất thay vì $W/N$ lớn nhất.
5. **Mở rộng:** thay rollout ngẫu nhiên bằng heuristic đơn giản và đo mức cải thiện. Rút ra bài học: đây chính là tiền thân của value network.
6. **Mở rộng cho bài toán cờ tướng (\*)** → Xác định điểm trên 9

## Bài 2 (Bonus)

Các bài toán thực tế có thể giải quyết bằng AI.

### Các nội dung có trong report

**Tóm tắt (≤ 200 từ):** bài toán, phương pháp, kết quả chính có số liệu, kết luận.

**1. Giới thiệu**

Bối cảnh, mục tiêu và các câu hỏi…

**2. Phát biểu bài toán**

Định nghĩa hình thức trò chơi…

**3. Phương pháp**

- 3.1 Minimax + Alpha-Beta, hàm lượng giá.
- 3.2 MCTS-UCT: $UCT(i) = \dfrac{W_i}{N_i} + c\sqrt{\dfrac{\ln N_p}{N_i}}$.
- 3.3 Rollout ngẫu nhiên và rollout heuristic.

**4. Thiết lập thực nghiệm**

Thử trên 2 trò chơi: Tic-tac-toe và Cờ tướng.

Môi trường, đối thủ, độ đo (tỷ lệ thắng, số nút, thời gian), số ván ($\geq 50$, đổi lượt đi trước), $c \in \{0.5;\ 1.0;\ 1.4;\ 2.0\}$, $\text{iteration} \in \{100, \dots, 5000\}$.

**5. Kết quả**

- Bảng số nút Minimax vs Alpha-Beta.
- Bảng thắng/hòa/thua của MCTS ($3 \times 3$ và bàn 5 quân).
- Đồ thị: số iteration – tỷ lệ thắng, mỗi $c$ một đường.
- Bảng $W$, $N$, $W/N$ tại nút gốc.
- So sánh rollout ngẫu nhiên và heuristic.
- …

**6. Thảo luận**

Trả lời từng RQ; giải thích $N$ vs $W/N$; liên hệ heuristic rollout với value network; nêu hạn chế.