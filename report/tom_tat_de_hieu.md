# Tóm tắt toàn bộ Report (bản tự giải thích từ gốc, dễ hiểu)

## 1. Bài toán & Khái niệm nền tảng

### Trò chơi mình làm là gì?

Làm AI chơi **Tic-Tac-Toe** trên 2 kích thước:

- **Bàn 3×3** (3 quân thẳng hàng là thắng): tổng số trạng thái rất nhỏ (tối đa 9 nước), máy có thể tính hết toàn bộ khả năng → dùng để **kiểm chứng lý thuyết** (xem AI có thực sự "không bao giờ thua" không).
- **Bàn 15×15** (5 quân thẳng hàng — cờ caro / Gomoku): không gian trạng thái khổng lồ → dùng để **thử thách thuật toán** trong điều kiện thực tế.

### Cây trò chơi (Game Tree) & Branching Factor là gì?

- **Cây trò chơi**: Hình dung từ bàn cờ hiện tại (gốc cây), mỗi nước đi hợp lệ đẻ ra một nhánh con (trạng thái mới). Từ mỗi nhánh con, đối thủ lại có các nước đi đẻ ra nhánh cháu... cứ thế tạo thành một cái cây.
- **Branching factor ($b$)** (hệ số phân nhánh): Số nước đi hợp lệ trung bình ở mỗi lượt.
  - Trên bàn 3×3: $b \le 9$, độ sâu tối đa $d = 9$ → tổng số nút tối đa vài trăm nghìn, máy tính duyệt hết trong tích tắc.
  - Trên bàn 15×15: có 225 ô. Nếu không lọc, $b \approx 200$, chỉ cần nhìn trước 4 nước ($d = 4$) đã có $200^4 = 1{,}6 \text{ tỷ}$ trạng thái → **bùng nổ tổ hợp**, máy tính không thể duyệt hết.

### Mẹo giảm không gian tìm kiếm trong `Board.get_legal_moves()`

- Nếu bàn cờ trống → bắt buộc đánh ô trung tâm `(7, 7)` (vì mọi hướng đều đối xứng và rộng nhất).
- Nếu đã có quân → chỉ xét các ô trống nằm trong **bán kính 2 ô** (khoảng cách Chebyshev $\le 2$, tức hình vuông $5\times 5$ quanh mỗi quân đã đặt).
- *Tại sao bán kính 2 mà không phải 1?* Vì trong cờ caro hay có nước đánh cách 1 ô trống (kiểu `_ O _ O _`) để tạo bẫy. Bán kính 1 sẽ bỏ sót nước này, còn bán kính 2 giữ lại được mà vẫn giảm $b$ từ ~200 xuống còn ~20–40 ô.

---

## 2. Thuật toán 1: Minimax + Alpha-Beta + Hàm `evaluate`

### Minimax hoạt động thế nào?

Minimax giả định **cả hai bên đều chơi thông minh nhất có thể**:

- Lượt của mình (**MAX**): chọn nước đi cho điểm **cao nhất**.
- Lượt đối thủ (**MIN**): đối thủ sẽ chọn nước làm điểm của mình **thấp nhất**.

Thuật toán dùng **DFS (Depth-First Search — tìm kiếm theo chiều sâu)**: đi thẳng xuống một nhánh đến độ sâu giới hạn `max_depth` (hoặc đến khi có người thắng/hòa), chấm điểm ở đáy, rồi truyền ngược điểm lên trên (tầng MIN lấy `min`, tầng MAX lấy `max`).

### Cắt tỉa Alpha-Beta là gì? (Ví dụ cụ thể)

Alpha-Beta cho ra **kết quả giống hệt 100% Minimax**, nhưng bỏ qua những nhánh chắc chắn vô ích bằng cách nhớ 2 con số:

- **$\alpha$ (alpha)**: Điểm tốt nhất mà **MAX** đã chắc chắn nắm trong tay tính đến lúc này (khởi tạo $-\infty$).
- **$\beta$ (beta)**: Điểm thấp nhất mà **MIN** đã chắc chắn ép được tính đến lúc này (khởi tạo $+\infty$).

**Ví dụ trực quan:**

```
Gốc (MAX)
├── Nhánh A (MIN) → đã tính xong, trả về 5  ⇒  MAX chắc chắn có ít nhất α = 5
└── Nhánh B (MIN) → đang xét các con của B:
    ├── Con B1 → điểm 8  (MIN tạm có β = 8)
    ├── Con B2 → điểm 3  (MIN cập nhật β = 3)
    └── Con B3, B4... → CẮT BỎ! Không cần xem nữa.
```

*Tại sao cắt được B3, B4?* Vì tại B là lượt MIN, MIN đã thấy nước B2 cho điểm `3`, nên giá trị cuối cùng của nhánh B **chắc chắn $\le 3$**. Trong khi đó ở Gốc, MAX đã có nhánh A cho `5` rồi → MAX đời nào chọn nhánh B ($\le 3$) thay vì nhánh A (`5`)! Vậy xem tiếp B3, B4 là vô nghĩa.

Điều kiện cắt tổng quát: hễ thấy **$\alpha \ge \beta$** thì dừng duyệt nhánh đó ngay. Nếu thứ tự duyệt nước tốt, độ phức tạp giảm từ $\mathcal{O}(b^d)$ xuống $\mathcal{O}(b^{d/2})$ — tức cùng thời gian chạy, Alpha-Beta nhìn sâu gấp đôi Minimax.

### Hàm lượng giá `evaluate` (chấm điểm khi hết `max_depth`)

Vì trên bàn 15×15 không thể đi đến hết ván, khi chạm `max_depth` ta phải ước lượng xem bàn cờ đang nghiêng về ai. Hàm `evaluate` quét toàn bộ bàn cờ theo 4 hướng (ngang, dọc, chéo chính, chéo phụ), tìm các chuỗi quân liên tiếp của mình và đối thủ, rồi tính:

$$
\text{Điểm} = \text{Tổng điểm của mình} - \text{Tổng điểm của đối thủ}
$$

Bảng điểm theo `(độ dài chuỗi, số đầu mở)`:

- Thắng (5 quân): `100,000` (nếu ván đã kết thúc hẳn thì trả `±1,000,000`)
- 4 quân mở 2 đầu: `50,000` | mở 1 đầu: `5,000`
- 3 quân mở 2 đầu: `2,000` | mở 1 đầu: `200`
- 2 quân mở 2 đầu: `100` | mở 1 đầu: `10`
- 1 quân mở 2 đầu: `5` | mở 1 đầu: `1`

**3 điểm thiết kế quan trọng:**

1. **Điểm tăng theo cấp số nhân (phi tuyến)**: Chuỗi 4 nguy hiểm hơn chuỗi 2 gấp hàng trăm lần. Nếu cho điểm tuyến tính (ví dụ chuỗi 2 = 20, chuỗi 4 = 40), AI có thể ham tạo 3 chuỗi 2 (= 60 điểm) mà bỏ mặc đối thủ tạo chuỗi 4 (= 40 điểm) rồi thua ngay lượt sau.
2. **Mở 2 đầu gấp 10× mở 1 đầu**: Chuỗi 4 mở 2 đầu (`_ X X X X _`) gần như thắng chắc vì đối thủ chỉ có 1 nước đi, không thể bịt cả 2 đầu cùng lúc.
3. **Kiểm tra đủ chỗ thắng**: Nếu một chuỗi bị kẹp 2 đầu không đủ 5 ô trống để kéo dài thành 5 quân (ví dụ `O X X X O` hoặc `O . X X X O`) → cho `0` điểm luôn vì chuỗi đó đã "chết".

---

## 3. Thuật toán 2: MCTS + UCT & Cơ sở toán học (giải thích từ gốc)

Khác với Minimax duyệt đều mọi nhánh đến một độ sâu cố định, **MCTS (Monte Carlo Tree Search)** xây dựng cây **bất đối xứng**: nhánh nào hứa hẹn thì đào rất sâu, nhánh nào tệ thì bỏ qua sớm.

### 4 bước lặp đi lặp lại `iterations` lần

1. **Selection (Lựa chọn)**: Bắt đầu từ gốc, đi xuống theo công thức UCT (chọn con có điểm UCT cao nhất) cho đến khi gặp một nút chưa mở rộng hết các nước con (hoặc nút kết thúc ván).
2. **Expansion (Mở rộng)**: Lấy 1 nước chưa từng thử ở nút đó, tạo ra 1 nút con mới gắn vào cây.
3. **Simulation / Rollout (Mô phỏng)**: Từ nút con mới tạo, cho hai bên tự đánh thử đến khi kết thúc ván (hoặc tối đa 30 bước) để lấy kết quả: `1.0` (thắng), `0.5` (hòa / chưa phân thắng bại), `0.0` (thua).
4. **Backpropagation (Cập nhật ngược)**: Đi ngược từ nút vừa mô phỏng lên tới gốc. Ở mỗi nút đi qua:
   - Tăng số lần thăm: $N \leftarrow N + 1$.
   - Cộng điểm thắng: $W \leftarrow W + r$ (trừ nút gốc vì gốc không có nước đi dẫn vào).
   - **Đảo góc nhìn**: $r \leftarrow 1.0 - r$ mỗi khi bước lên nút cha. *Tại sao phải đảo?* Vì nút con lưu điểm cho người vừa đánh nước dẫn tới nút con (ví dụ X), còn nút cha là lượt trước đó (của O). X thắng (`1.0`) thì với O là thua (`1.0 - 1.0 = 0.0`).

### Công thức UCT

$$
UCT_i = \underbrace{\frac{W_i}{N_i}}_{\text{Khai thác (Exploitation)}} + c\,\underbrace{\sqrt{\frac{\ln N_{\mathrm{parent}}}{N_i}}}_{\text{Khám phá (Exploration)}}
$$

- $W_i$: tổng điểm thắng tích lũy của nước đi $i$.
- $N_i$: số lần nước đi $i$ đã được thử.
- $N_{\mathrm{parent}}$: tổng số lần nút cha đã được thăm (bằng tổng $N_i$ của các con + 1).
- $c$: hằng số điều chỉnh độ "liều" (càng lớn càng thích thử nước mới).
- Nếu $N_i = 0$ (chưa thử bao giờ) → gán $UCT_i = +\infty$ để ép máy thử mỗi nước ít nhất 1 lần trước khi so sánh.

---

### Giải thích từ gốc: Multi-Armed Bandit, UCB1 và Bất đẳng thức Hoeffding là gì?

Đây là phần toán học đằng sau công thức UCT (phần bonus trong report). Đọc theo 4 bước sau là hiểu trọn vẹn:

#### Bước 1: Bài toán Multi-Armed Bandit (MAB — Máy đánh bạc nhiều tay) là gì?

Hãy tưởng tượng bạn đứng trước $K$ cái máy đánh bạc (slot machine) trong sòng bài. Mỗi máy $i$ có một tỷ lệ trúng thưởng thật $\mu_i \in [0, 1]$ nhưng **bạn không biết trước con số này**. Bạn có $N$ đồng xu để chơi thử:

- Nếu chỉ chơi mãi cái máy đầu tiên thấy trúng → có thể bỏ lỡ một máy khác ngon hơn nhiều (**thiếu khám phá**).
- Nếu cứ đổi máy liên tục để thử → tốn tiền vào mấy máy dở (**thiếu khai thác**).

Tại mỗi nút trong cây MCTS, việc chọn 1 trong $K$ nước đi hợp lệ **chính xác là bài toán Multi-Armed Bandit**: mỗi nước đi là một cái máy, mỗi lần mô phỏng (rollout) là một lần kéo cần để xem kết quả thắng/thua.

#### Bước 2: Regret (Sự hối tiếc) là gì?

Giả sử máy tốt nhất có tỷ lệ thắng thật là $\mu^*$. Nếu bạn biết trước thì bạn đã chơi máy đó cả $N$ lần và thu được $N \cdot \mu^*$. Nhưng vì không biết nên bạn phải thử các máy khác, tổng số tiền bị hụt đi so với người biết trước gọi là **Regret (hối tiếc)** $R(N)$.

- Nếu chọn bừa: $R(N)$ tăng tuyến tính theo $N$ (càng chơi càng lỗ đều).
- Lai & Robbins (1985) chứng minh: bất kỳ thuật toán nào cũng không thể làm tốt hơn mức $R(N) \propto \ln N$ (tăng cực chậm theo logarit). Thuật toán nào đạt được $R(N) = \mathcal{O}(\ln N)$ được gọi là **tối ưu về mặt toán học**.

#### Bước 3: Bất đẳng thức Hoeffding là gì? (Tại sao lại xuất hiện $\sqrt{\cdot}$ và $\ln$?)

Khi bạn mới thử máy $i$ được $N_i$ lần và thấy tỷ lệ thắng trung bình là $\bar{X}_i = W_i / N_i$, con số này có thể bị lệch so với tỷ lệ thật $\mu_i$ do may rủi. **Bất đẳng thức Hoeffding** là một định lý xác suất cho biết *xác suất bị lệch quá một khoảng $\epsilon$* nhỏ đến mức nào:

$$
P\left(\mu_i - \frac{W_i}{N_i} \ge \epsilon\right) \le e^{-2 N_i \epsilon^2}
$$

Nói nôm na:

- $N_i$ càng lớn (thử càng nhiều) → xác suất bị lệch giảm theo hàm mũ cực nhanh.
- Muốn sai số $\epsilon$ nhỏ đi một nửa → phải thử nhiều gấp 4 lần (vì có $\epsilon^2$ trong số mũ).

Bây giờ, thuật toán **UCB1** (Upper Confidence Bound — Auer et al., 2002) đặt yêu cầu: *xác suất đánh giá nhầm một máy tốt phải giảm nhanh theo tổng số lượt chơi $N_{\mathrm{parent}}$*, cụ thể đặt vế phải bằng $N_{\mathrm{parent}}^{-4}$:

$$
e^{-2 N_i \epsilon^2} = N_{\mathrm{parent}}^{-4}
$$

*(Tại sao lại chọn đúng số mũ $-4$ mà không phải $-2$ hay $-3$? Vì trong chứng minh regret, ở mỗi bước $t$ ta phải cộng xác suất sai qua mọi cặp số lần thử $(s, s_i)$ của máy tốt nhất và máy dở — tối đa $t \times t = t^2$ cặp. Nếu đặt xác suất đuôi là $t^{-\alpha}$, tổng sai số qua mọi bước là $\sum_{t=1}^{\infty} t^2 \cdot t^{-\alpha} = \sum_{t=1}^{\infty} t^{2-\alpha}$. Để chuỗi này hội tụ thành hằng số hữu hạn thay vì nổ ra $\infty$, ta cần $\alpha - 2 > 1 \iff \alpha > 3$. Số nguyên nhỏ nhất thỏa mãn là $\alpha = 4$, cho $\sum_{t=1}^{\infty} t^{-2} = \pi^2/6 < \infty$.)*

Lấy $\ln$ hai vế rồi giải tìm $\epsilon$:

$$
-2 N_i \epsilon^2 = -4 \ln N_{\mathrm{parent}} \implies \epsilon^2 = \frac{2 \ln N_{\mathrm{parent}}}{N_i} \implies \epsilon = \sqrt{\frac{2 \ln N_{\mathrm{parent}}}{N_i}}
$$

**Đó chính là nguồn gốc của $\sqrt{\cdot}$ và $\ln$!**

- **$\sqrt{\cdot}$** xuất hiện vì trong bất đẳng thức Hoeffding có $\epsilon^2$.
- **$\ln N_{\mathrm{parent}}$** xuất hiện vì ta lấy logarit của xác suất đuôi $N_{\mathrm{parent}}^{-4}$.

Cộng sai số $\epsilon$ này vào trung bình mẫu $W_i / N_i$, ta được **cận trên tin cậy (Upper Confidence Bound)**:

$$
UCB1_i = \frac{W_i}{N_i} + \sqrt{\frac{2 \ln N_{\mathrm{parent}}}{N_i}}
$$

Nguyên lý của UCB1 là **"Lạc quan trước sự bất định"**: luôn chọn máy có *khả năng tốt nhất* (cận trên cao nhất). Nếu một máy ít được thử ($N_i$ nhỏ), khoảng tin cậy $\epsilon$ của nó rất rộng → cận trên cao → máy tính buộc phải thử nó. Nếu nó thực sự dở, $W_i/N_i$ thấp và $\epsilon$ co lại → nó tự động bị bỏ qua. Auer et al. chứng minh UCB1 đạt regret $\mathcal{O}(\ln N)$ — **chạm ngưỡng tối ưu lý thuyết**.

#### Bước 4: Từ UCB1 sang UCT (và tại sao phải chỉnh $c$)

Năm 2006, Kocsis & Szepesvári áp dụng UCB1 vào từng tầng của cây trò chơi và đặt tên là **UCT (UCB applied to Trees)**, thay số $\sqrt{2}$ cố định bằng tham số $c$ tùy chỉnh:

- Lý thuyết UCB1 giả định phần thưởng của mỗi máy là **đứng yên (stationary)** và nằm trong $[0, 1]$.
- Trong cây trò chơi, khi cây mọc sâu hơn, chất lượng rollout thay đổi theo thời gian (không đứng yên) → giá trị lý thuyết $c = \sqrt{2} \approx 1{,}414$ không phải lúc nào cũng tốt nhất, nên cần thử nghiệm thực tế để chọn $c$.
- Đây cũng là lý do code dùng điểm `{0.0, 0.5, 1.0}` thay vì `{-1, 0, +1}`: để phần thưởng nằm gọn trong $[0, 1]$ đúng giả định của Hoeffding/UCB1.

### Tại sao cuối cùng chọn nước có $N$ lớn nhất chứ không chọn $W/N$ lớn nhất?

- Một nước mới thử 1–2 lần mà ăn may thắng cả 2 thì $W/N = 1{,}0$ (100%), nhưng phương sai cực lớn, không đáng tin.
- Nước thực sự tốt sẽ được UCT chọn đi chọn lại hàng trăm lần → $N$ rất lớn, khoảng tin cậy $\epsilon$ co nhỏ lại, ước lượng ổn định nhất.
- Vì vậy chọn `most_visited_child()` (nhiều lượt thăm $N$ nhất) an toàn hơn hẳn chọn theo $W/N$.

---

## 4. Rollout ngẫu nhiên vs Rollout Heuristic

- **Random rollout**: Hai bên đánh bừa hoàn toàn.
- **Heuristic rollout**: Ở mỗi bước mô phỏng, kiểm tra nhanh:
  1. Có nước thắng ngay → đánh luôn.
  2. Đối thủ sắp thắng ngay → chặn luôn.
  3. Không có gì → đánh bừa.
- **Giới hạn 30 bước (`MAX_ROLLOUT_STEPS = 30`)**: Trên bàn 15×15, hai bên đánh bừa có thể kéo dài 100–200 nước không xong nên phải cắt ở 30 bước. Nếu hết 30 bước chưa ai thắng → trả `0.5` (coi như chưa phân thắng bại).
- **Liên hệ với AlphaGo**: Heuristic rollout chính là phiên bản "viết tay đơn giản" của **Policy Network & Value Network** trong AlphaGo (Silver et al., 2016) — thay vì đánh bừa đến hết ván (rất nhiễu và chậm), ta dùng tri thức/mạng neural để định hướng nước đi và chấm điểm vị trí ngay.

---

## 5. Các biến thể UCT & Cải tiến Progressive Bias (Phần bonus)

Để kiểm chứng xem bỏ $\sqrt{\cdot}$ hay $\ln$ trong công thức UCT thì thuật toán hỏng thế nào, và thử cải tiến UCT, mình chạy 5 phiên bản:

1. **Standard UCT**: $\frac{W_i}{N_i} + c\sqrt{\frac{\ln N_p}{N_i}}$ (chuẩn)
2. **No-sqrt**: $\frac{W_i}{N_i} + c\frac{\ln N_p}{N_i}$ (bỏ căn)
3. **No-ln**: $\frac{W_i}{N_i} + c\sqrt{\frac{N_p}{N_i}}$ (bỏ $\ln$)
4. **Linear**: $\frac{W_i}{N_i} + c\frac{N_p}{N_i}$ (bỏ cả căn và $\ln$)
5. **Progressive Bias (Cải tiến UCT — Chaslot et al., 2008)**:
   $$
   UCT_{PB}(i) = \frac{W_i}{N_i} + c\sqrt{\frac{\ln N_p}{N_i}} + \frac{H_i}{N_i + 1}
   $$

   Trong đó $H_i = \frac{1 + \tanh(\text{evaluate}(s_i, p_i) / 5000)}{2} \in (0, 1)$ là điểm từ hàm `evaluate()` được nén về khoảng $(0, 1)$ và tính sẵn 1 lần cho mỗi nút.
   - Lúc mới mở nút ($N_i$ nhỏ): $\frac{H_i}{N_i + 1}$ lớn → dẫn MCTS đi thẳng vào các nước có thế cờ đẹp thay vì thử bừa 30–40 ô trống.
   - Khi đã thử nhiều ($N_i \to \infty$): $\frac{H_i}{N_i + 1} \to 0$ → tự tắt dần, trả lại đúng công thức UCT chuẩn nên **không làm mất tính tối ưu về dài hạn**.

---

## 6. Toàn bộ kết quả thực nghiệm (số liệu thật đã chạy)

### Bảng 1: Minimax vs Alpha-Beta (số nút phải duyệt)


| Bàn   | Depth | Minimax | Alpha-Beta | Giảm được |
| ------ | ----: | ------: | ---------: | ------------: |
| 3×3   |     1 |       7 |          7 |          0.0% |
| 3×3   |     2 |      49 |         32 |         34.7% |
| 3×3   |     3 |     259 |        132 |         49.0% |
| 3×3   |     4 |     979 |        276 |     **71.8%** |
| 15×15 |     1 |      36 |         36 |          0.0% |
| 15×15 |     2 |   1,634 |        410 |         74.9% |
| 15×15 |     3 |  85,290 |     10,257 |     **88.0%** |

→ **Ý nghĩa**: Bàn càng to, depth càng sâu thì Alpha-Beta cắt càng mạnh (tiết kiệm tới **88%** ở depth 3 bàn 15×15).

---

### Bảng 2: Kiểm chứng MCTS "không bao giờ thua" trên 3×3 (50 ván/cấu hình)

Đấu với **Alpha-Beta depth 9** (duyệt hết cây 3×3 → chơi hoàn hảo, giỏi nhất là hòa) và **Random**:


| Đối thủ       |           c | Iterations | Thắng |  Hòa |  Thua |
| ---------------- | ----------: | ---------: | -----: | ----: | ----: |
| Alpha-Beta (d=9) |         1.0 |        100 |      0 |    39 |    11 |
| Alpha-Beta (d=9) |         1.0 |        500 |      0 |    48 |     2 |
| Alpha-Beta (d=9) |         1.0 |   **1000** |      0 |    50 | **0** |
| Alpha-Beta (d=9) |         1.0 |   **2000** |      0 |    50 | **0** |
| Alpha-Beta (d=9) |       1.414 |        100 |      0 |    41 |     9 |
| Alpha-Beta (d=9) |       1.414 |        500 |      0 |    48 |     2 |
| Alpha-Beta (d=9) |       1.414 |   **1000** |      0 |    50 | **0** |
| Alpha-Beta (d=9) |       1.414 |   **2000** |      0 |    50 | **0** |
| Random           | 1.0 / 1.414 |     ≥ 500 | 40–44 | 6–10 | **0** |

→ **Ý nghĩa**: Ít iterations (100–500) vẫn có thể thua máy chơi hoàn hảo vì cây chưa đủ sâu để thấy bẫy đôi. Từ **1000 iterations trở lên**, MCTS **không thua ván nào (0/50)** trước cả đối thủ hoàn hảo lẫn random.

---

### Bảng 3: Khảo sát `c` và `iterations` (đấu Random)

**Trên 3×3 (100 ván/cấu hình):**

- Từ `500` iterations trở lên, cả 4 giá trị `c ∈ {0.5, 1.0, 1.4, 2.0}` đều **0 ván thua**, tỷ lệ thắng bão hòa quanh **84–90%** (còn lại là hòa khi đi sau).

**Trên 15×15 (50 ván/cấu hình):**


|       c | 100 iters |  200 iters |  500 iters | Thời gian/nước (500 iters) |
| ------: | --------: | ---------: | ---------: | ----------------------------: |
| **0.5** | **64.0%** | **100.0%** |      98.0% |                         5.23s |
| **1.0** |     54.0% |      56.0% | **100.0%** |                         5.16s |
| **1.4** |     52.0% |      58.0% | **100.0%** |                         5.12s |
| **2.0** |     46.0% |      58.0% |      96.0% |                         5.67s |

→ **Ý nghĩa**: Khi ít iterations (100–200), `c = 0.5` thắng áp đảo vì tập trung khai thác nhanh thay vì đi lang thang. Khi đủ iterations (500), `c = 1.0` và `1.4` đạt **100% (50/50)**.

---

### Bảng 4: Thống kê `W, N, W/N` tại nút gốc (1000 iters, c=1.0)

- **Trên 3×3** (X ở giữa, O ở góc): MCTS dồn `299 + 246 = 545/1000` lượt thăm vào 2 nước mạnh nhất `(0,1)` (`W/N = 0.811`) và `(1,0)` (`W/N = 0.793`).
- **Trên 15×15** (khai cuộc 4 quân): Các nước đều có `N ≈ 29–31` và `W/N ≈ 0.50–0.53` vì rollout bị cắt ở 30 bước nên phần lớn trả về `0.5` (chưa phân thắng bại).

---

### Bảng 5: Random Rollout vs Heuristic Rollout (`c = √2`)


| Bàn   | Iters | Số ván | Random | Heuristic | Cải thiện | Thời gian/nước                  |
| ------ | ----: | -------: | -----: | --------: | ----------: | ---------------------------------- |
| 3×3   |   500 |      100 |  84.0% | **90.0%** |   **+6.0%** | 52ms vs 51ms                       |
| 15×15 |   200 |       50 |  76.0% | **92.0%** |  **+16.0%** | 3.65s vs 5.55s (chậm hơn 1.52×) |

→ **Ý nghĩa**: Heuristic rollout tăng tỷ lệ thắng rõ rệt (+16% trên 15×15) mà chỉ chậm hơn 1.52× (nhờ kiểm tra thắng/chặn trực tiếp trên bàn cờ không clone).

---

### Bảng 6: So sánh các biến thể UCT & Progressive Bias (`c = 1.0`)


| Biến thể                        | 3×3 vs AB d=9 (300 iters, Không thua) | 3×3 vs Random (200 iters, Thắng / Không thua) | 15×15 vs Random (150 iters, Thắng / Thời gian) |
| --------------------------------- | --------------------------------------: | -----------------------------------------------: | ------------------------------------------------: |
| **Standard UCT**                  |                      **96.0%** (4 thua) |                                    88.0% / 98.0% |                                     52.0% / 2.71s |
| **No-sqrt** (bỏ căn)            |                          95.0% (5 thua) |                                    84.0% / 99.0% |                                     44.0% / 2.63s |
| **No-ln** (bỏ `ln`)              |                     **76.0%** (24 thua) |                                    88.0% / 97.0% |                                 **34.0%** / 3.04s |
| **Linear** (bỏ cả 2)            |                     **65.0%** (35 thua) |                                    83.0% / 93.0% |                                 **34.0%** / 3.07s |
| **Progressive Bias (Cải tiến)** |                          95.0% (5 thua) |                      **88.0% / 100.0% (0 thua)** |                         **98.0% (49/50) / 2.39s** |

→ **Ý nghĩa**:

- Bỏ `ln` (`no_ln`) hoặc bỏ cả 2 (`linear`) làm số hạng khám phá phình theo đa thức của $N_p$ → MCTS không chịu khai thác nước tốt → thua thảm (tụt từ 96% xuống 65% trên 3×3, từ 52% xuống 34% trên 15×15).
- Bỏ căn (`no_sqrt`) phạt quá nặng các nút ít thăm → giảm tỷ lệ thắng trên 15×15 từ 52% xuống 44%.
- **Progressive Bias** nhảy vọt từ **52.0% → 98.0% (+46%)** trên 15×15 ở budget thấp (150 iters), lại còn **nhanh hơn** (2.39s vs 2.71s) vì thắng sớm hơn!

---

## 7. Hạn chế của bài (nếu thầy hỏi "bài em còn yếu chỗ nào?")

1. **Cắt rollout ở 30 bước trả `0.5`**: Làm khai cuộc 15×15 ít tín hiệu phân biệt (`W/N` quanh 0.50–0.53). Nếu thay `0.5` bằng điểm `evaluate()` chuẩn hóa thì sẽ mạnh hơn nữa.
2. **Chưa tái sử dụng cây (Tree Reuse)**: Mỗi nước đi MCTS lại xây cây mới từ đầu.
3. **Alpha-Beta depth 3 trên 15×15**: Chưa có sắp xếp nước đi (move ordering) và hàm `evaluate` chưa bắt được đòn đôi (2 chuỗi 3 giao nhau), nên người chơi có kinh nghiệm vẫn bẫy được.

---

## 8. Mẹo trả lời nhanh khi vấn đáp

- **Hỏi: Tại sao MCTS dùng điểm `{0, 0.5, 1}` mà không dùng `{-1, 0, +1}`?**
  → Vì công thức UCB1 và bất đẳng thức Hoeffding yêu cầu phần thưởng nằm trong `[0, 1]` để `W/N` mang nghĩa xác suất thắng.
- **Hỏi: Tại sao chọn nước cuối theo `N` lớn nhất chứ không theo `W/N`?**
  → Vì `W/N` dễ bị nhiễu khi `N` nhỏ (thử 1 lần thắng 1 → 100%). `N` lớn nhất là nước được UCT tin tưởng quay lại nhiều nhất, phương sai thấp nhất.
- **Hỏi: Tại sao `c = 0.5` lại thắng `c = 1.4` ở 100–200 iterations trên 15×15?**
  → Vì bàn 15×15 có quá nhiều nước hợp lệ (~24–40 ô). Budget ít mà `c` to thì MCTS lo đi thử hết các ô rìa, chưa kịp đào sâu vào nước tốt.
- **Hỏi: Progressive Bias có làm mất tính tối ưu của UCT không?**
  → Không, vì số hạng `H / (N + 1)` tiến về `0` khi `N → ∞`, nên về dài hạn nó quay về đúng UCT chuẩn.
- **Hỏi: Tại sao chạy thực nghiệm dùng `ProcessPoolExecutor` mà không dùng `ThreadPoolExecutor`?**
  → Vì Python có GIL (Global Interpreter Lock), đa luồng không chạy song song thật trên nhiều nhân CPU cho tác vụ tính toán nặng như MCTS; phải dùng đa tiến trình (`ProcessPoolExecutor`).
