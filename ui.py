"""
ui.py — Giao diện Tkinter cho Tic-Tac-Toe AI.

Chạy: python ui.py
"""
import math
import threading
import tkinter as tk
from tkinter import ttk, messagebox

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from src.game.board import Board, X, O
from src.minimax.minimax import MinimaxAgent
from src.minimax.alpha_beta import AlphaBetaAgent
from src.mcts.mcts import MCTSAgent
from src.mcts.rollout import random_rollout, heuristic_rollout
from src.utils.evaluate import evaluate

# ── Màu sắc ──────────────────────────────────────────────────────────────────
BG          = "#1e1e2e"
BOARD_BG    = "#313244"
LINE_COLOR  = "#585b70"
X_COLOR     = "#f38ba8"
O_COLOR     = "#89b4fa"
LAST_MOVE   = "#a6e3a1"
TEXT_COLOR  = "#cdd6f4"
BTN_BG      = "#45475a"
BTN_ACTIVE  = "#585b70"
WIN_COLOR   = "#f9e2af"
PANEL_BG    = "#181825"

CELL        = 40   # pixel mỗi ô
MARGIN      = 20   # viền ngoài bàn cờ


# ── Setup screen ──────────────────────────────────────────────────────────────

class SetupScreen(tk.Toplevel):
    """Cửa sổ cấu hình trước khi bắt đầu ván."""

    def __init__(self, master, on_start):
        super().__init__(master)
        self.title("Cài đặt ván đấu")
        self.configure(bg=BG)
        self.resizable(False, False)
        self.on_start = on_start
        self.grab_set()  # modal

        pad = {"padx": 10, "pady": 6}

        # ── Cài đặt bàn cờ ───────────────────────────────────────────────────
        board_frame = tk.LabelFrame(self, text="Bàn cờ", bg=BG,
                                    fg=TEXT_COLOR, font=("Consolas", 10, "bold"))
        board_frame.grid(row=0, column=0, columnspan=2, sticky="ew", **pad)

        tk.Label(board_frame, text="Kích thước (n×n):", bg=BG, fg=TEXT_COLOR).grid(row=0, column=0, sticky="w", **pad)
        self.size_var = tk.IntVar(value=15)
        tk.Spinbox(board_frame, from_=3, to=19, textvariable=self.size_var,
                   width=5, bg=BTN_BG, fg=TEXT_COLOR, buttonbackground=BTN_BG).grid(row=0, column=1, sticky="w", **pad)

        tk.Label(board_frame, text="Số quân thẳng hàng:", bg=BG, fg=TEXT_COLOR).grid(row=1, column=0, sticky="w", **pad)
        self.win_var = tk.IntVar(value=5)
        tk.Spinbox(board_frame, from_=3, to=9, textvariable=self.win_var,
                   width=5, bg=BTN_BG, fg=TEXT_COLOR, buttonbackground=BTN_BG).grid(row=1, column=1, sticky="w", **pad)

        # ── Cài đặt người chơi ───────────────────────────────────────────────
        for col, (label, attr) in enumerate([("Người chơi X (đi trước)", "x"), ("Người chơi O (đi sau)", "o")]):
            frame = tk.LabelFrame(self, text=label, bg=BG,
                                  fg=X_COLOR if attr == "x" else O_COLOR,
                                  font=("Consolas", 10, "bold"))
            frame.grid(row=1, column=col, sticky="nsew", **pad)
            self._build_player_panel(frame, attr)

        # ── Nút bắt đầu ──────────────────────────────────────────────────────
        tk.Button(self, text="▶  Bắt đầu", command=self._start,
                  bg="#a6e3a1", fg="#1e1e2e", font=("Consolas", 11, "bold"),
                  relief="flat", cursor="hand2", activebackground="#94e2d5"
                  ).grid(row=2, column=0, columnspan=2, pady=14, ipadx=20, ipady=6)

    def _build_player_panel(self, frame, attr):
        pad = {"padx": 8, "pady": 4}
        type_var = tk.StringVar(value="Human")
        setattr(self, f"{attr}_type", type_var)

        for t in ["Human", "Minimax", "Alpha-Beta", "MCTS"]:
            tk.Radiobutton(frame, text=t, variable=type_var, value=t,
                           bg=BG, fg=TEXT_COLOR, selectcolor=BOARD_BG,
                           activebackground=BG, command=lambda a=attr: self._refresh(a)
                           ).pack(anchor="w", **pad)

        # Minimax / Alpha-Beta params
        sub = tk.Frame(frame, bg=BG)
        sub.pack(fill="x", **pad)
        setattr(self, f"{attr}_sub", sub)

        depth_frame = tk.Frame(sub, bg=BG)
        depth_frame.pack(fill="x")
        tk.Label(depth_frame, text="Depth:", bg=BG, fg=TEXT_COLOR, width=12, anchor="w").pack(side="left")
        depth_var = tk.IntVar(value=3)
        setattr(self, f"{attr}_depth", depth_var)
        tk.Spinbox(depth_frame, from_=1, to=6, textvariable=depth_var,
                   width=4, bg=BTN_BG, fg=TEXT_COLOR, buttonbackground=BTN_BG).pack(side="left")

        # MCTS params
        mcts_frame = tk.Frame(sub, bg=BG)
        mcts_frame.pack(fill="x")
        setattr(self, f"{attr}_mcts_frame", mcts_frame)

        tk.Label(mcts_frame, text="Iterations:", bg=BG, fg=TEXT_COLOR, width=12, anchor="w").pack(side="left")
        iters_var = tk.IntVar(value=1000)
        setattr(self, f"{attr}_iters", iters_var)
        tk.Spinbox(mcts_frame, from_=50, to=10000, increment=50,
                   textvariable=iters_var, width=6,
                   bg=BTN_BG, fg=TEXT_COLOR, buttonbackground=BTN_BG).pack(side="left")

        c_frame = tk.Frame(sub, bg=BG)
        c_frame.pack(fill="x")
        setattr(self, f"{attr}_c_frame", c_frame)

        tk.Label(c_frame, text="C:", bg=BG, fg=TEXT_COLOR, width=12, anchor="w").pack(side="left")
        c_var = tk.DoubleVar(value=1.414)
        setattr(self, f"{attr}_c", c_var)
        tk.Entry(c_frame, textvariable=c_var, width=6,
                 bg=BTN_BG, fg=TEXT_COLOR, insertbackground=TEXT_COLOR).pack(side="left")

        heur_frame = tk.Frame(sub, bg=BG)
        heur_frame.pack(fill="x")
        setattr(self, f"{attr}_heur_frame", heur_frame)

        heur_var = tk.BooleanVar(value=True)
        setattr(self, f"{attr}_heur", heur_var)
        tk.Checkbutton(heur_frame, text="Heuristic rollout",
                       variable=heur_var, bg=BG, fg=TEXT_COLOR,
                       selectcolor=BOARD_BG, activebackground=BG).pack(anchor="w")

        self._refresh(attr)

    def _refresh(self, attr):
        """Ẩn/hiện tham số theo loại agent."""
        t = getattr(self, f"{attr}_type").get()
        sub = getattr(self, f"{attr}_sub")

        show_depth = t in ("Minimax", "Alpha-Beta")
        show_mcts  = t == "MCTS"

        for widget in sub.winfo_children():
            widget.pack_forget()

        if show_depth:
            sub.winfo_children()[0].pack(fill="x")   # depth_frame
        if show_mcts:
            for w in sub.winfo_children()[1:]:        # mcts frames
                w.pack(fill="x")

    def _build_agent(self, attr):
        t = getattr(self, f"{attr}_type").get()
        if t == "Human":
            return None, "Human"
        elif t == "Minimax":
            d = getattr(self, f"{attr}_depth").get()
            ag = MinimaxAgent(max_depth=d, eval_fn=evaluate)
            return lambda b, a=ag: a.get_move(b), f"Minimax(d={d})"
        elif t == "Alpha-Beta":
            d = getattr(self, f"{attr}_depth").get()
            ag = AlphaBetaAgent(max_depth=d, eval_fn=evaluate)
            return lambda b, a=ag: a.get_move(b), f"AlphaBeta(d={d})"
        else:  # MCTS
            iters = getattr(self, f"{attr}_iters").get()
            c     = getattr(self, f"{attr}_c").get()
            heur  = getattr(self, f"{attr}_heur").get()
            rollout = heuristic_rollout if heur else random_rollout
            ag = MCTSAgent(iterations=iters, c=c, rollout_fn=rollout)
            rname = "heur" if heur else "rand"
            return lambda b, a=ag: a.get_move(b), f"MCTS(i={iters},c={c:.2f},{rname})"

    def _start(self):
        size    = self.size_var.get()
        win_len = self.win_var.get()
        if win_len > size:
            messagebox.showerror("Lỗi", "Số quân thẳng hàng không được lớn hơn kích thước bàn!")
            return
        ax, nx = self._build_agent("x")
        ao, no = self._build_agent("o")
        self.destroy()
        self.on_start(ax, ao, nx, no, size, win_len)


# ── Game screen ───────────────────────────────────────────────────────────────

class GameScreen:
    """Màn hình chơi chính."""

    def __init__(self, root, ai_x, ai_o, name_x, name_o, board_size, win_len):
        self.root      = root
        self.ai_x      = ai_x
        self.ai_o      = ai_o
        self.name_x    = name_x
        self.name_o    = name_o
        self.board_size = board_size
        self.win_len   = win_len
        self.board     = Board(board_size, win_len)
        self.last_move = None
        self.game_over = False
        self.ai_thinking = False

        self._build_ui()
        self._draw_board()
        self._update_status()

        # Nếu X là AI → đi ngay
        self._maybe_ai_move()

    def _build_ui(self):
        self.root.configure(bg=BG)
        self.root.title("Tic-Tac-Toe AI")

        # Panel trái — info
        panel = tk.Frame(self.root, bg=PANEL_BG, width=200)
        panel.pack(side="left", fill="y", padx=(10, 0), pady=10)
        panel.pack_propagate(False)

        tk.Label(panel, text="TIC-TAC-TOE", bg=PANEL_BG, fg=TEXT_COLOR,
                 font=("Consolas", 13, "bold")).pack(pady=(20, 4))
        tk.Label(panel, text="AI Project", bg=PANEL_BG, fg=LINE_COLOR,
                 font=("Consolas", 9)).pack()

        ttk.Separator(panel, orient="horizontal").pack(fill="x", pady=12, padx=10)

        # Thông tin người chơi
        tk.Label(panel, text="X (đi trước)", bg=PANEL_BG, fg=X_COLOR,
                 font=("Consolas", 10, "bold")).pack(anchor="w", padx=16)
        tk.Label(panel, text=self.name_x, bg=PANEL_BG, fg=TEXT_COLOR,
                 font=("Consolas", 9), wraplength=170, justify="left").pack(anchor="w", padx=16, pady=(0, 8))

        tk.Label(panel, text="O (đi sau)", bg=PANEL_BG, fg=O_COLOR,
                 font=("Consolas", 10, "bold")).pack(anchor="w", padx=16)
        tk.Label(panel, text=self.name_o, bg=PANEL_BG, fg=TEXT_COLOR,
                 font=("Consolas", 9), wraplength=170, justify="left").pack(anchor="w", padx=16, pady=(0, 8))

        ttk.Separator(panel, orient="horizontal").pack(fill="x", pady=12, padx=10)

        # Status
        self.status_var = tk.StringVar(value="")
        tk.Label(panel, textvariable=self.status_var, bg=PANEL_BG, fg=WIN_COLOR,
                 font=("Consolas", 10, "bold"), wraplength=170, justify="center").pack(pady=4)

        # Lượt đi
        self.turn_var = tk.StringVar(value="")
        tk.Label(panel, textvariable=self.turn_var, bg=PANEL_BG, fg=TEXT_COLOR,
                 font=("Consolas", 10), wraplength=170, justify="center").pack(pady=2)

        # Nước đi cuối
        self.last_var = tk.StringVar(value="")
        tk.Label(panel, textvariable=self.last_var, bg=PANEL_BG, fg=LAST_MOVE,
                 font=("Consolas", 9), wraplength=170).pack(pady=2)

        ttk.Separator(panel, orient="horizontal").pack(fill="x", pady=12, padx=10)

        # Nút
        btn_cfg = dict(bg=BTN_BG, fg=TEXT_COLOR, relief="flat",
                       font=("Consolas", 10), cursor="hand2",
                       activebackground=BTN_ACTIVE, activeforeground=TEXT_COLOR)
        tk.Button(panel, text="↺  Ván mới", command=self._new_game, **btn_cfg
                  ).pack(fill="x", padx=16, pady=4, ipady=4)
        tk.Button(panel, text="⚙  Cài đặt", command=self._open_setup, **btn_cfg
                  ).pack(fill="x", padx=16, pady=4, ipady=4)
        tk.Button(panel, text="✕  Thoát", command=self.root.quit, **btn_cfg
                  ).pack(fill="x", padx=16, pady=4, ipady=4)

        # Canvas bàn cờ
        canvas_size = self.board_size * CELL + 2 * MARGIN
        self.canvas = tk.Canvas(self.root, width=canvas_size, height=canvas_size,
                                bg=BOARD_BG, highlightthickness=0)
        self.canvas.pack(side="left", padx=10, pady=10)
        self.canvas.bind("<Button-1>", self._on_click)

    # ── Vẽ bàn cờ ────────────────────────────────────────────────────────────

    def _draw_board(self):
        self.canvas.delete("all")
        n    = self.board_size
        size = n * CELL + 2 * MARGIN

        # Grid lines
        for i in range(n + 1):
            x = MARGIN + i * CELL
            y = MARGIN + i * CELL
            self.canvas.create_line(MARGIN, y, size - MARGIN, y, fill=LINE_COLOR, width=1)
            self.canvas.create_line(x, MARGIN, x, size - MARGIN, fill=LINE_COLOR, width=1)

        # Highlight ô cuối
        if self.last_move:
            r, c = self.last_move
            x0 = MARGIN + c * CELL
            y0 = MARGIN + r * CELL
            self.canvas.create_rectangle(x0, y0, x0 + CELL, y0 + CELL,
                                         fill=LAST_MOVE, outline="", stipple="gray25")

        # Quân cờ
        pad = 6
        for r in range(n):
            for c in range(n):
                val = self.board.board[r, c]
                if val == 0:
                    continue
                x0 = MARGIN + c * CELL + pad
                y0 = MARGIN + r * CELL + pad
                x1 = MARGIN + (c + 1) * CELL - pad
                y1 = MARGIN + (r + 1) * CELL - pad
                cx = (x0 + x1) / 2
                cy = (y0 + y1) / 2
                color = X_COLOR if val == X else O_COLOR
                font_size = max(8, CELL // 2 - 2)
                self.canvas.create_text(cx, cy, text="X" if val == X else "O",
                                        fill=color, font=("Consolas", font_size, "bold"))

    def _update_status(self):
        if self.board.is_terminal:
            self.game_over = True
            if self.board.winner == X:
                self.status_var.set("🏆 X THẮNG!")
                self.turn_var.set("")
            elif self.board.winner == O:
                self.status_var.set("🏆 O THẮNG!")
                self.turn_var.set("")
            else:
                self.status_var.set("🤝 HÒA!")
                self.turn_var.set("")
            self.last_var.set(f"Nước cuối: {self.last_move}" if self.last_move else "")
        else:
            self.status_var.set("")
            p = "X" if self.board.current_player == X else "O"
            color_name = self.name_x if self.board.current_player == X else self.name_o
            self.turn_var.set(f"Lượt: {p} ({color_name})")
            self.last_var.set(f"Nước trước: {self.last_move}" if self.last_move else "")

    # ── Xử lý click ──────────────────────────────────────────────────────────

    def _on_click(self, event):
        if self.game_over or self.ai_thinking:
            return
        agent = self.ai_x if self.board.current_player == X else self.ai_o
        if agent is not None:
            return  # lượt AI, không cho click

        c = (event.x - MARGIN) // CELL
        r = (event.y - MARGIN) // CELL
        if 0 <= r < self.board_size and 0 <= c < self.board_size:
            if self.board.make_move(r, c):
                self.last_move = (r, c)
                self._draw_board()
                self._update_status()
                if not self.game_over:
                    self._maybe_ai_move()

    # ── AI move (chạy thread riêng để không block UI) ─────────────────────────

    def _maybe_ai_move(self):
        if self.game_over:
            return
        agent = self.ai_x if self.board.current_player == X else self.ai_o
        if agent is None:
            return

        self.ai_thinking = True
        p = "X" if self.board.current_player == X else "O"
        self.turn_var.set(f"⏳ {p} đang suy nghĩ...")

        def run():
            move = agent(self.board)
            self.root.after(0, lambda: self._apply_ai_move(move))

        threading.Thread(target=run, daemon=True).start()

    def _apply_ai_move(self, move):
        self.board.make_move(*move)
        self.last_move = move
        self.ai_thinking = False
        self._draw_board()
        self._update_status()
        if not self.game_over:
            self._maybe_ai_move()

    # ── Điều hướng ───────────────────────────────────────────────────────────

    def _new_game(self):
        """Reset ván mới với cùng cài đặt."""
        self.board     = Board(self.board_size, self.win_len)
        self.last_move = None
        self.game_over = False
        self.ai_thinking = False
        self.status_var.set("")
        self._draw_board()
        self._update_status()
        self._maybe_ai_move()

    def _open_setup(self):
        """Mở lại màn hình cài đặt."""
        self.canvas.destroy()
        for widget in self.root.winfo_children():
            widget.destroy()
        _show_setup(self.root)


# ── Entry point ───────────────────────────────────────────────────────────────

def _show_setup(root):
    def on_start(ai_x, ai_o, name_x, name_o, size, win_len):
        for w in root.winfo_children():
            w.destroy()
        GameScreen(root, ai_x, ai_o, name_x, name_o, size, win_len)

    # Cửa sổ setup là Toplevel nhưng root ẩn đi
    root.withdraw()
    setup = SetupScreen(root, on_start=lambda *a: [root.deiconify(), on_start(*a)])
    setup.protocol("WM_DELETE_WINDOW", root.quit)


def main():
    root = tk.Tk()
    root.configure(bg=BG)
    root.resizable(False, False)
    _show_setup(root)
    root.mainloop()


if __name__ == "__main__":
    main()
