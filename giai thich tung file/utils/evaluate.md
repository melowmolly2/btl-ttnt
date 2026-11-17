# Evaluate - Hàm lượng giá (evaluation / heuristic)

Dùng cho Minimax (trả về điểm khi hết depth) và Rollout heuristic trong MCTS

Ý tưởng: 
- Quét toàn bộ các đường (ngang, dọc, chéo chính, chéo phụ)
- Mỗi đường -> tìm chuỗi quan liên tiếp -> Tra bảng điểm. 
- `evaluate = my_total_score - opponent_total_score`

Bảng điểm

|Độ dài chuỗi|Số đầu mở|Điểm|
|-|-|-|
|5|1|100000|
|5|2|100000|
|4|2|50000|
|4|1|5000|
|3|2|2000|
|3|1|200|
|2|1|10|
|1|2|5|
|1|1|1|

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


