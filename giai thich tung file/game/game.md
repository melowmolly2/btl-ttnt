# Game - vòng lặp game chính 
`player_symbol`: Ký tự đại diện cho người chơi (X hoặc O)
`human_move()`: Nhập nước đi từ bàn phím

`play_game`: Vòng lặp game chính
(ai_x,ai_o: AI cho quân x/o, truyền none nếu là người chơi, verbose: có in bàn cờ ra terminal không)
- Lặp lại cho đến khi trạng thái dừng:
 - In bàn cờ (nếu verbose)
 - Nhìn vào `agents[board.curent_player]` xem là `None` hoặc AI
  - Nếu là `None` (người chơi) thì gọi `human_move()` chờ người nhập từ bàn phím
  - Nếu là AI thì gọi `agent(board)` lấy nước đi rồi `make_move()`. 