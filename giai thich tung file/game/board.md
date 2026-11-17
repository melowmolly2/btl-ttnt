# Board - Bàn cờ caro

Khởi tạo: 
- `size`: Kích thước bàn cờ (mặc định 15)
- `win_len`: Cần bao nhiêu quân thẳng hàng liên tiếp để thắng (mặc định 5)
- `board`:  Mảng 2d lưu trạng thái bàn cờ
- `current_player`: Người chơi hiện tại, ban đầu là X(1) đi trước
- `move_history`: Danh sách các nước đã đi của cả hai người chơi
- `_winner`: Người thắng, (mặc định chưa có)

`def clone(self)`: Trả về bản sao độc lập của bàn cờ 
`def get_legal_moves(self)`: Trả về danh sách ô trống, ưu tiên ô gần quân đã đặt (giảm không gian tìm kiếm)
- Nếu bàn cờ trống, chỉ cho phép ô trung tâm
 - Ô trung tâm có nhiều hướng tấn công nhất (4 hướng đều đủ dài)
 - Kiểm soát trung tâm tạo lợi thế chiến lược
 - Rút ngắn không gian tìm kiếm ngay từ đầu thay vì duyệt toàn bộ các ô
- Lấy các ô trống trong vùng lân cận 2 ô quanh các quân đã đi
 - Các nước đi thực tế đều nằm gần các quân đã đặt (tấn công, phòng thủ)
 - Giảm không gian tìm kiếm xuống
 - Nước đi xa thực sự vô nghĩa, đặt quân cách xa quân đã có không tạo mối đe dọa hay phòng thủ ngay lập tức. 
 - Radius = 2 để AI có thể nhìn thấy các nước dạo đầu như tạo cặp quân cách nhau 1 ô - đủ để phát hiện chiến thuật _O_O_

Ý tưởng : Giảm không gian tìm kiếm xuống trong khi bảo đảm độ chính xác

`get_all_empty(self)`: Trả về mọi ô trống, không lọc vùng lân cận
`make_move(self, row:int, col:int) -> bool`: Đặt quân, trả về true nếu hợp lệ và false nếu không
`undo_move(self):` Hủy nước đi cuối cùng (dùng trong Minimax không clone)
- Minimax duyệt cây theo DFS, sau khi duyệt xong một nhánh muốn duyệt sang nhánh khác thì phải hủy nước đi tại nhánh này để duyệt tiếp.
- Nếu không hủy thì các nhánh tiếp theo tính trên trạng thái sai

`_check_win(self, row:int, col:int)`: Kiểm tra quân vừa đặt có tạo một chuỗi thắng không

`winner(self)`: X,O hoặc None nếu chưa kết thúc
`is_draw(self)`: Hòa nếu tất cả các ô đã đi và không có người thắng
`is_terminal`: Trạng thái dừng khi có người thắng hoặc hòa 
`__str__(self)`: In bảng


