# Evaluate - Hàm lượng giá (evaluation / heuristic)

Dùng cho Minimax (trả về điểm khi hết depth) và Rollout heuristic trong MCTS

Ý tưởng:

- Quét toàn bộ các đường (ngang, dọc, chéo chính, chéo phụ)
- Mỗi đường -> tìm chuỗi quan liên tiếp -> Tra bảng điểm.
- `evaluate = my_total_score - opponent_total_score`

Bảng điểm


| Độ dài chuỗi | Số đầu mở | Điểm |
| ---------------- | ------------- | ------ |
| 5                | 1             | 100000 |
| 5                | 2             | 100000 |
| 4                | 2             | 50000  |
| 4                | 1             | 5000   |
| 3                | 2             | 2000   |
| 3                | 1             | 200    |
| 2                | 1             | 10     |
| 1                | 2             | 5      |
| 1                | 1             | 1      |

Giải thích cách chọn bảng điểm:
Có 2 yếu tố:

- Độ dài chuỗi
- Số đầu mở

Yếu tố 1: Độ dài chuỗi

- Càng dài thì càng nguy hiểm
- Điểm tăng theo cấp số nhân
  (VD: Chuỗi 4 không phải gấp đôi chuỗi 2, chuỗi 4 nếu không chặn thì sẽ thua còn chuỗi 2 gần như không đáng sợ gì cả).
- Khoảng cách điểm lớn ép minimax ưu tiên đúng mức độ nguy hiểm

Yếu tố 2: Số đầu mở

- Mở 2 đầu chênh gấp nhiều lần so với mở 1 đầu (10x)
- Mở 2 đầu tức là đối thủ phải chặn cả hai đầu nhưng chỉ có 1 nước để chặn.
- Trường hợp 4 mở 2 đầu: 50000 điểm so với 5 mở 1 đầu : 100000. 4 mở 2 đầu gần như thắng chắc vì không thể chặn 2 đầu cùng 1 lúc được, chỉ thua nếu đối thủ có nước 4 mở 1 hoặc 2 đầu ngay trước đấy

`_count_space`: Đếm số ô trống liên tiếp từ pos theo direction

`_score_line`: Tính điểm cho player trên một đường thẳng

Một đầu được coi là mở khi ô kề trống. Nhưng nếu khoảng trái + độ dài chuỗi hiện tại + khoảng phải < độ dài để thắng thì chuỗi không thể thắng theo hướng này -> chuỗi bị chặn hoàn toàn.

VD với win_len=5:

- O.XXX.O -> `total_space=1+1=2,length=3`-> 2+3=5>=5, có thể thắng nhưng `left_space=right_space=1`, không đầu nào rộng hơn -> cả hai đầu đều bị hạn chế -> tính (3,1)=200
- ..XXX.O -> `space_left=2,space_right=1, total=6>=5, trái có 2 chỗ, phải có 1 đầu -> 2 đầu kề empty -> (3,2)=2000 (vẫn là nước đôi)
- O.XXX.. -> đối xứng với trường hợp trên -> (3,2)=2000
- OXXXO -> `total=3<5`-> 0 điểm
- O.XXXO -> `total=4<5`-> 0 điểm

Hàm chạy như sau:

- Đếm độ dài chuỗi
- Đếm khoảng trống 2 phía
- Nếu không đủ chỗ để thắng (`space_left+space_right+length<win_len`) thì  bỏ qua
- Đầu nào kề ô trống thì coi là mở, nếu tổng chỗ trống vừa đúng đủ `win_len` thì chỉ có thể đi 1 hướng -> tính như 1 đầu mở
- Trả về kết quả điểm tra theo bảng điểm

`_total_score`: Tổng điểm của player trên toàn bộ bàn cờ (4 hướng)

`evaluate`: Hàm lượng giá trạng thái bàn cờ từ góc nhìn perspective (X hoặc O).

Trả về: +1tr nếu perspective thắng, -1tr nếu perspective thua,   0 nếu hòa, nếu chưa ai thắng thua hoặc hòa trả về tổng điểm của mình trừ tổng điểm đối thủ
