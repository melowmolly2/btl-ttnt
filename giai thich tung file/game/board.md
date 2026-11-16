# Board - Bàn cờ caro

Khởi tạo: 
`size`: Kích thước bàn cờ (mặc định 15)
`win_len`: Cần bao nhiêu quân thẳng hàng liên tiếp để thắng
`current_player`: Người chơi hiện tại, ban đầu là X(1) đi trước
`move_history`: list


```Python
 def __init__(self, size: int = 15, win_len: int = 5):
        self.size = size
        self.win_len = win_len
        self.board = np.zeros((size, size), dtype=np.int8)
        self.current_player = X      # X đi trước
        self.move_history: list[tuple[int, int]] = []
        self._winner = None
```

