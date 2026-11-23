"""
ui.py — Giao diện Tkinter cho Tic-Tac-Toe AI.
Chạy: python ui.py
"""
import math
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from src.game.board import Board, X, O
from src.minimax.minimax import MinimaxAgent
from src.minimax.alpha_beta import AlphaBetaAgent
from src.mcts.mcts import MCTSAgent
from src.mcts.rollout import random_rollout, heuristic_rollout
from src.utils.evaluate import evaluate

# ── Màu sắc ──────────────────────────────────────────────────────────────────
BG         = "#1e1e2e"
BOARD_BG   = "#313244"
LINE_COLOR = "#585b70"
X_COLOR    = "#f38ba8"
O_COLOR    = "#89b4fa"
LAST_MOVE  = "#a6e3a1"
TEXT_COLOR = "#cdd6f4"
BTN_BG     = "#45475a"
BTN_ACTIVE = "#585b70"
WIN_COLOR  = "#f9e2af"
PANEL_BG   = "#181825"
STATS_BG   = "#11111b"
DIM_COLOR  = "#6c7086"

CELL   = 40
MARGIN = 20


# ── Wrapper agent — trả về move + stats ──────────────────────────────────────

class AgentWrapper:
    """
    Bọc agent gốc, sau mỗi lần get_move lưu stats để UI hiển thị.
    stats là dict với các key tuỳ loại agent:
      Minimax/AB : {"nodes": int, "move": tuple}
      MCTS       : {"top": list[dict], "move": tuple}
    """
    def __init__(self, agent, kind):
        self.agent = agent
        self.kind  = kind   # "minimax" | "alphabeta" | "mcts"
        self.stats = {}

    def get_move(self, board):
        move = self.agent.get_move(board)
        if self.kind in ("minimax", "alphabeta"):
            self.stats = {
                "nodes": self.agent.nodes_visited,
                "move":  move,
            }
        else:  # mcts — đọc stats từ chính lần search vừa chạy
            top = self.agent.last_root_stats[:3]
            self.stats = {"top": top, "move": move}
        return move


# ── Setup screen ──────────────────────────────────────────────────────────────

class SetupScreen(tk.Toplevel):
    def __init__(self, master, on_start):
        super().__init__(master)
        self.title("Cài đặt ván đấu")
        self.configure(bg=BG)
        self.resizable(False, False)
        self.on_start = on_start
        self.grab_set()

        pad = {"padx": 10, "pady": 6}

        # Bàn cờ
        bf = tk.LabelFrame(self, text="Bàn cờ", bg=BG, fg=TEXT_COLOR,
                           font=("Consolas", 10, "bold"))
        bf.grid(row=0, column=0, columnspan=2, sticky="ew", **pad)

        tk.Label(bf, text="Kích thước (n×n):", bg=BG, fg=TEXT_COLOR).grid(row=0, column=0, sticky="w", **pad)
        self.size_var = tk.IntVar(value=15)
        tk.Spinbox(bf, from_=3, to=19, textvariable=self.size_var,
                   width=5, bg=BTN_BG, fg=TEXT_COLOR, buttonbackground=BTN_BG
                   ).grid(row=0, column=1, sticky="w", **pad)

        tk.Label(bf, text="Số quân thẳng hàng:", bg=BG, fg=TEXT_COLOR).grid(row=1, column=0, sticky="w", **pad)
        self.win_var = tk.IntVar(value=5)
        tk.Spinbox(bf, from_=3, to=9, textvariable=self.win_var,
                   width=5, bg=BTN_BG, fg=TEXT_COLOR, buttonbackground=BTN_BG
                   ).grid(row=1, column=1, sticky="w", **pad)

        # Người chơi
        for col, (label, attr) in enumerate([
            ("Người chơi X (đi trước)", "x"),
            ("Người chơi O (đi sau)",   "o"),
        ]):
            color = X_COLOR if attr == "x" else O_COLOR
            frame = tk.LabelFrame(self, text=label, bg=BG, fg=color,
                                  font=("Consolas", 10, "bold"))
            frame.grid(row=1, column=col, sticky="nsew", **pad)
            self._build_player_panel(frame, attr)

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
                           activebackground=BG,
                           command=lambda a=attr: self._refresh(a)
                           ).pack(anchor="w", **pad)

        sub = tk.Frame(frame, bg=BG)
        sub.pack(fill="x", **pad)
        setattr(self, f"{attr}_sub", sub)

        # depth
        df = tk.Frame(sub, bg=BG)
        df.pack(fill="x")
        tk.Label(df, text="Depth:", bg=BG, fg=TEXT_COLOR, width=14, anchor="w").pack(side="left")
        dv = tk.IntVar(value=3)
        setattr(self, f"{attr}_depth", dv)
        tk.Spinbox(df, from_=1, to=6, textvariable=dv,
                   width=4, bg=BTN_BG, fg=TEXT_COLOR, buttonbackground=BTN_BG).pack(side="left")

        # iterations
        itf = tk.Frame(sub, bg=BG)
        itf.pack(fill="x")
        tk.Label(itf, text="Iterations:", bg=BG, fg=TEXT_COLOR, width=14, anchor="w").pack(side="left")
        iv = tk.IntVar(value=1000)
        setattr(self, f"{attr}_iters", iv)
        tk.Spinbox(itf, from_=50, to=10000, increment=50, textvariable=iv,
                   width=6, bg=BTN_BG, fg=TEXT_COLOR, buttonbackground=BTN_BG).pack(side="left")

        # c
        cf = tk.Frame(sub, bg=BG)
        cf.pack(fill="x")
        tk.Label(cf, text="C:", bg=BG, fg=TEXT_COLOR, width=14, anchor="w").pack(side="left")
        cv = tk.DoubleVar(value=1.414)
        setattr(self, f"{attr}_c", cv)
        tk.Entry(cf, textvariable=cv, width=6,
                 bg=BTN_BG, fg=TEXT_COLOR, insertbackground=TEXT_COLOR).pack(side="left")

        # heuristic
        hf = tk.Frame(sub, bg=BG)
        hf.pack(fill="x")
        hv = tk.BooleanVar(value=True)
        setattr(self, f"{attr}_heur", hv)
        tk.Checkbutton(hf, text="Heuristic rollout", variable=hv,
                       bg=BG, fg=TEXT_COLOR, selectcolor=BOARD_BG,
                       activebackground=BG).pack(anchor="w")

        self._refresh(attr)

    def _refresh(self, attr):
        t   = getattr(self, f"{attr}_type").get()
        sub = getattr(self, f"{attr}_sub")
        children = sub.winfo_children()   # [depth_f, iters_f, c_f, heur_f]

        for w in children:
            w.pack_forget()

        if t in ("Minimax", "Alpha-Beta"):
            children[0].pack(fill="x")
        elif t == "MCTS":
            for w in children[1:]:
                w.pack(fill="x")

    def _build_agent(self, attr):
        t = getattr(self, f"{attr}_type").get()
        if t == "Human":
            return None, "Human"
        elif t in ("Minimax", "Alpha-Beta"):
            d  = getattr(self, f"{attr}_depth").get()
            ag = (MinimaxAgent if t == "Minimax" else AlphaBetaAgent)(
                max_depth=d, eval_fn=evaluate)
            kind  = "minimax" if t == "Minimax" else "alphabeta"
            label = f"{t}(d={d})"
            return AgentWrapper(ag, kind), label
        else:  # MCTS
            iters = getattr(self, f"{attr}_iters").get()
            c     = getattr(self, f"{attr}_c").get()
            heur  = getattr(self, f"{attr}_heur").get()
            rollout = heuristic_rollout if heur else random_rollout
            ag    = MCTSAgent(iterations=iters, c=c, rollout_fn=rollout)
            rname = "heur" if heur else "rand"
            label = f"MCTS(i={iters},c={c:.2f},{rname})"
            return AgentWrapper(ag, "mcts"), label

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
    def __init__(self, root, ai_x, ai_o, name_x, name_o, board_size, win_len):
        self.root       = root
        self.ai_x       = ai_x    # AgentWrapper | None
        self.ai_o       = ai_o
        self.name_x     = name_x
        self.name_o     = name_o
        self.board_size = board_size
        self.win_len    = win_len
        self.board      = Board(board_size, win_len)
        self.last_move  = None
        self.game_over  = False
        self.ai_thinking = False

        self._build_ui()
        self._draw_board()
        self._update_status()
        self._clear_stats()
        self._maybe_ai_move()

    # ── Build UI ─────────────────────────────────────────────────────────────

    def _build_ui(self):
        self.root.configure(bg=BG)
        self.root.title("Tic-Tac-Toe AI")

        # === Panel trái ===
        panel = tk.Frame(self.root, bg=PANEL_BG, width=210)
        panel.pack(side="left", fill="y", padx=(10, 0), pady=10)
        panel.pack_propagate(False)

        tk.Label(panel, text="TIC-TAC-TOE", bg=PANEL_BG, fg=TEXT_COLOR,
                 font=("Consolas", 13, "bold")).pack(pady=(16, 2))
        tk.Label(panel, text="AI Project", bg=PANEL_BG, fg=DIM_COLOR,
                 font=("Consolas", 9)).pack()

        ttk.Separator(panel, orient="horizontal").pack(fill="x", pady=10, padx=10)

        # Người chơi
        tk.Label(panel, text="X (đi trước)", bg=PANEL_BG, fg=X_COLOR,
                 font=("Consolas", 10, "bold")).pack(anchor="w", padx=14)
        tk.Label(panel, text=self.name_x, bg=PANEL_BG, fg=TEXT_COLOR,
                 font=("Consolas", 8), wraplength=185, justify="left"
                 ).pack(anchor="w", padx=14, pady=(0, 6))

        tk.Label(panel, text="O (đi sau)", bg=PANEL_BG, fg=O_COLOR,
                 font=("Consolas", 10, "bold")).pack(anchor="w", padx=14)
        tk.Label(panel, text=self.name_o, bg=PANEL_BG, fg=TEXT_COLOR,
                 font=("Consolas", 8), wraplength=185, justify="left"
                 ).pack(anchor="w", padx=14, pady=(0, 6))

        ttk.Separator(panel, orient="horizontal").pack(fill="x", pady=10, padx=10)

        # Status / lượt
        self.status_var = tk.StringVar()
        tk.Label(panel, textvariable=self.status_var, bg=PANEL_BG, fg=WIN_COLOR,
                 font=("Consolas", 10, "bold"), wraplength=185, justify="center"
                 ).pack(pady=2)

        self.turn_var = tk.StringVar()
        tk.Label(panel, textvariable=self.turn_var, bg=PANEL_BG, fg=TEXT_COLOR,
                 font=("Consolas", 9), wraplength=185, justify="center"
                 ).pack(pady=2)

        self.last_var = tk.StringVar()
        tk.Label(panel, textvariable=self.last_var, bg=PANEL_BG, fg=LAST_MOVE,
                 font=("Consolas", 9), wraplength=185
                 ).pack(pady=2)

        ttk.Separator(panel, orient="horizontal").pack(fill="x", pady=10, padx=10)

        # === Stats box ===
        tk.Label(panel, text="AI Stats", bg=PANEL_BG, fg=DIM_COLOR,
                 font=("Consolas", 9, "bold")).pack(anchor="w", padx=14)

        stats_box = tk.Frame(panel, bg=STATS_BG, bd=0)
        stats_box.pack(fill="x", padx=10, pady=4)

        self.stats_var = tk.StringVar(value="—")
        tk.Label(stats_box, textvariable=self.stats_var, bg=STATS_BG, fg=TEXT_COLOR,
                 font=("Consolas", 8), wraplength=185, justify="left",
                 anchor="nw", padx=6, pady=6
                 ).pack(fill="x")

        ttk.Separator(panel, orient="horizontal").pack(fill="x", pady=10, padx=10)

        # Nút
        bcfg = dict(bg=BTN_BG, fg=TEXT_COLOR, relief="flat", font=("Consolas", 10),
                    cursor="hand2", activebackground=BTN_ACTIVE, activeforeground=TEXT_COLOR)
        tk.Button(panel, text="↺  Ván mới",  command=self._new_game,   **bcfg
                  ).pack(fill="x", padx=14, pady=3, ipady=4)
        tk.Button(panel, text="⚙  Cài đặt", command=self._open_setup,  **bcfg
                  ).pack(fill="x", padx=14, pady=3, ipady=4)
        tk.Button(panel, text="✕  Thoát",   command=self.root.quit,    **bcfg
                  ).pack(fill="x", padx=14, pady=3, ipady=4)

        # === Canvas bàn cờ ===
        cs = self.board_size * CELL + 2 * MARGIN
        self.canvas = tk.Canvas(self.root, width=cs, height=cs,
                                bg=BOARD_BG, highlightthickness=0)
        self.canvas.pack(side="left", padx=10, pady=10)
        self.canvas.bind("<Button-1>", self._on_click)

    # ── Vẽ bàn cờ ────────────────────────────────────────────────────────────

    def _draw_board(self):
        self.canvas.delete("all")
        n    = self.board_size
        size = n * CELL + 2 * MARGIN

        for i in range(n + 1):
            x = MARGIN + i * CELL
            y = MARGIN + i * CELL
            self.canvas.create_line(MARGIN, y, size - MARGIN, y, fill=LINE_COLOR)
            self.canvas.create_line(x, MARGIN, x, size - MARGIN, fill=LINE_COLOR)

        if self.last_move:
            r, c = self.last_move
            x0 = MARGIN + c * CELL
            y0 = MARGIN + r * CELL
            self.canvas.create_rectangle(x0, y0, x0 + CELL, y0 + CELL,
                                         fill=LAST_MOVE, outline="", stipple="gray25")

        pad = 6
        fs  = max(8, CELL // 2 - 2)
        for r in range(n):
            for c in range(n):
                val = self.board.board[r, c]
                if val == 0:
                    continue
                cx = MARGIN + c * CELL + CELL / 2
                cy = MARGIN + r * CELL + CELL / 2
                color = X_COLOR if val == X else O_COLOR
                self.canvas.create_text(cx, cy,
                                        text="X" if val == X else "O",
                                        fill=color,
                                        font=("Consolas", fs, "bold"))

    # ── Status ───────────────────────────────────────────────────────────────

    def _update_status(self):
        if self.board.is_terminal:
            self.game_over = True
            if self.board.winner == X:
                self.status_var.set("🏆 X THẮNG!")
            elif self.board.winner == O:
                self.status_var.set("🏆 O THẮNG!")
            else:
                self.status_var.set("🤝 HÒA!")
            self.turn_var.set("")
            self.last_var.set(f"Nước cuối: {self.last_move}" if self.last_move else "")
        else:
            self.status_var.set("")
            p    = "X" if self.board.current_player == X else "O"
            name = self.name_x if self.board.current_player == X else self.name_o
            self.turn_var.set(f"Lượt: {p} ({name})")
            self.last_var.set(f"Nước trước: {self.last_move}" if self.last_move else "")

    # ── Stats ─────────────────────────────────────────────────────────────────

    def _clear_stats(self):
        self.stats_var.set("—")

    def _show_stats(self, wrapper: AgentWrapper):
        s = wrapper.stats
        if not s:
            self._clear_stats()
            return

        if wrapper.kind in ("minimax", "alphabeta"):
            txt = (f"Nước chọn : {s.get('move')}\n"
                   f"Nút duyệt : {s.get('nodes', 0):,}")

        else:  # mcts
            lines = [f"Nước chọn : {s.get('move')}",
                     f"{'Move':<10} {'N':>5}  {'W/N':>6}"]
            for row in s.get("top", []):
                wn = f"{row['W/N']:.3f}"
                lines.append(f"{str(row['move']):<10} {row['N']:>5}  {wn:>6}")
            txt = "\n".join(lines)

        self.stats_var.set(txt)

    # ── Click ─────────────────────────────────────────────────────────────────

    def _on_click(self, event):
        if self.game_over or self.ai_thinking:
            return
        agent = self.ai_x if self.board.current_player == X else self.ai_o
        if agent is not None:
            return

        c = (event.x - MARGIN) // CELL
        r = (event.y - MARGIN) // CELL
        if 0 <= r < self.board_size and 0 <= c < self.board_size:
            if self.board.make_move(r, c):
                self.last_move = (r, c)
                self._clear_stats()
                self._draw_board()
                self._update_status()
                if not self.game_over:
                    self._maybe_ai_move()

    # ── AI move ───────────────────────────────────────────────────────────────

    def _maybe_ai_move(self):
        if self.game_over:
            return
        wrapper = self.ai_x if self.board.current_player == X else self.ai_o
        if wrapper is None:
            return

        self.ai_thinking = True
        p = "X" if self.board.current_player == X else "O"
        self.turn_var.set(f"⏳ {p} đang suy nghĩ...")
        self._clear_stats()

        def run():
            move = wrapper.get_move(self.board)
            self.root.after(0, lambda: self._apply_ai_move(move, wrapper))

        threading.Thread(target=run, daemon=True).start()

    def _apply_ai_move(self, move, wrapper):
        self.board.make_move(*move)
        self.last_move   = move
        self.ai_thinking = False
        self._draw_board()
        self._update_status()
        self._show_stats(wrapper)
        if not self.game_over:
            self._maybe_ai_move()

    # ── Điều hướng ───────────────────────────────────────────────────────────

    def _new_game(self):
        self.board       = Board(self.board_size, self.win_len)
        self.last_move   = None
        self.game_over   = False
        self.ai_thinking = False
        self.status_var.set("")
        self._draw_board()
        self._update_status()
        self._clear_stats()
        self._maybe_ai_move()

    def _open_setup(self):
        for w in self.root.winfo_children():
            w.destroy()
        _show_setup(self.root)


# ── Entry point ───────────────────────────────────────────────────────────────

def _show_setup(root):
    def on_start(ai_x, ai_o, name_x, name_o, size, win_len):
        for w in root.winfo_children():
            w.destroy()
        GameScreen(root, ai_x, ai_o, name_x, name_o, size, win_len)

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
