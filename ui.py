"""
ui.py — Giao diện Tkinter cho Tic-Tac-Toe AI.
Chạy: python ui.py
"""
import math
import time
import threading
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

LOGS_DIR = os.path.join(os.path.dirname(__file__), "logs")

from src.game.board import Board, X, O
from src.minimax.minimax import MinimaxAgent
from src.minimax.alpha_beta import AlphaBetaAgent
from src.mcts.mcts import MCTSAgent
from src.mcts.node import UCT_VARIANTS
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
MARGIN = 28


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

        # uct variant
        vf = tk.Frame(sub, bg=BG)
        vf.pack(fill="x")
        tk.Label(vf, text="UCT:", bg=BG, fg=TEXT_COLOR, width=6, anchor="w").pack(side="left")
        vv = tk.StringVar(value="standard")
        setattr(self, f"{attr}_variant", vv)
        ttk.Combobox(vf, textvariable=vv, values=list(UCT_VARIANTS),
                     state="readonly", width=15).pack(side="left")

        self._refresh(attr)

    def _refresh(self, attr):
        t   = getattr(self, f"{attr}_type").get()
        sub = getattr(self, f"{attr}_sub")
        children = sub.winfo_children()   # [depth_f, iters_f, c_f, heur_f, variant_f]

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
            iters   = getattr(self, f"{attr}_iters").get()
            c       = getattr(self, f"{attr}_c").get()
            heur    = getattr(self, f"{attr}_heur").get()
            variant = getattr(self, f"{attr}_variant").get()
            rollout = heuristic_rollout if heur else random_rollout
            ag      = MCTSAgent(iterations=iters, c=c, rollout_fn=rollout, uct_variant=variant)
            rname   = "heur" if heur else "rand"
            vtag    = f",{variant}" if variant != "standard" else ""
            label   = f"MCTS(i={iters},c={c:.2f},{rname}{vtag})"
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
        self._game_id   = 0

        self._build_ui()
        self._init_log()
        self._draw_board()
        self._update_status()
        self._clear_stats()
        self._maybe_ai_move()

    # ── Ghi log ván đấu ──────────────────────────────────────────────────────

    def _init_log(self):
        os.makedirs(LOGS_DIR, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_path = os.path.join(LOGS_DIR, f"game_{ts}_{self._game_id}.log")
        self._write_log(
            f"=== VÁN MỚI ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')}) ===\n"
            f"Bàn cờ : {self.board_size}x{self.board_size} (win_len={self.win_len})\n"
            f"X      : {self.name_x}\n"
            f"O      : {self.name_o}\n"
            f"{'-'*50}"
        )

    def _write_log(self, text: str):
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(text + "\n")

    def _log_move(self, player: int, move: tuple[int, int], elapsed_ms: float | None = None, wrapper=None):
        step = len(self.board.move_history)
        sym = "X" if player == X else "O"
        if wrapper is None:
            self._write_log(f"#{step:>3} [{sym}] Human -> {move}")
            return
        s = wrapper.stats
        t_str = f"{elapsed_ms:.1f} ms" if elapsed_ms is not None else ""
        if wrapper.kind in ("minimax", "alphabeta"):
            detail = f"nodes={s.get('nodes', 0):,}"
        else:
            top_str = ", ".join(
                f"{r['move']}(N={r['N']},W/N={r['W/N']:.3f})"
                for r in s.get("top", [])
            )
            detail = f"top=[{top_str}]"
        self._write_log(f"#{step:>3} [{sym}] {move} | {t_str} | {detail}")

    def _log_result_if_over(self):
        if not self.board.is_terminal:
            return
        if self.board.winner == X:
            res = f"X THẮNG ({self.name_x})"
        elif self.board.winner == O:
            res = f"O THẮNG ({self.name_o})"
        else:
            res = "HÒA"
        self._write_log(f"{'-'*50}\nKẾT QUẢ: {res} | Tổng số nước: {len(self.board.move_history)}")

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

        # === Stats boxes (riêng cho X và O để xem được cả 2 khi AI vs AI) ===
        self.stats_vars = {}
        for player, title, color in [(X, "X Stats", X_COLOR), (O, "O Stats", O_COLOR)]:
            tk.Label(panel, text=title, bg=PANEL_BG, fg=color,
                     font=("Consolas", 9, "bold")).pack(anchor="w", padx=14)
            box = tk.Frame(panel, bg=STATS_BG, bd=0)
            box.pack(fill="x", padx=10, pady=(2, 6))
            var = tk.StringVar(value="—")
            self.stats_vars[player] = var
            tk.Label(box, textvariable=var, bg=STATS_BG, fg=TEXT_COLOR,
                     font=("Consolas", 8), wraplength=185, justify="left",
                     anchor="nw", padx=6, pady=5
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

        # Đánh số hàng (trái) và cột (trên)
        coord_color = "#a6adc8"
        for i in range(n):
            cx = MARGIN + i * CELL + CELL / 2
            cy = MARGIN + i * CELL + CELL / 2
            self.canvas.create_text(cx, MARGIN / 2, text=str(i),
                                    fill=coord_color, font=("Consolas", 9))
            self.canvas.create_text(MARGIN / 2, cy, text=str(i),
                                    fill=coord_color, font=("Consolas", 9))

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

    def _clear_stats(self, player=None):
        if player is None:
            for var in self.stats_vars.values():
                var.set("—")
        else:
            self.stats_vars[player].set("—")

    def _show_stats(self, player: int, wrapper: AgentWrapper):
        s = wrapper.stats
        if not s:
            self._clear_stats(player)
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

        self.stats_vars[player].set(txt)

    # ── Click ─────────────────────────────────────────────────────────────────

    def _on_click(self, event):
        if self.game_over or self.ai_thinking:
            return
        player = self.board.current_player
        agent = self.ai_x if player == X else self.ai_o
        if agent is not None:
            return

        c = (event.x - MARGIN) // CELL
        r = (event.y - MARGIN) // CELL
        if 0 <= r < self.board_size and 0 <= c < self.board_size:
            if self.board.make_move(r, c):
                self.last_move = (r, c)
                self.stats_vars[player].set(f"Human: {(r, c)}")
                self._log_move(player, (r, c))
                self._log_result_if_over()
                self._draw_board()
                self._update_status()
                if not self.game_over:
                    self._maybe_ai_move()

    # ── AI move ───────────────────────────────────────────────────────────────

    def _maybe_ai_move(self):
        if self.game_over:
            return
        player = self.board.current_player
        wrapper = self.ai_x if player == X else self.ai_o
        if wrapper is None:
            return

        self.ai_thinking = True
        p = "X" if player == X else "O"
        self.turn_var.set(f"⏳ {p} đang suy nghĩ...")

        gid = self._game_id
        board_snap = self.board.clone()

        def run():
            t0 = time.perf_counter()
            move = wrapper.get_move(board_snap)
            elapsed_ms = (time.perf_counter() - t0) * 1000.0
            self.root.after(0, lambda: self._apply_ai_move(player, move, wrapper, gid, elapsed_ms))

        threading.Thread(target=run, daemon=True).start()

    def _apply_ai_move(self, player, move, wrapper, gid, elapsed_ms):
        if gid != self._game_id or self.game_over:
            return
        self.board.make_move(*move)
        self.last_move   = move
        self.ai_thinking = False
        self._log_move(player, move, elapsed_ms, wrapper)
        self._log_result_if_over()
        self._draw_board()
        self._update_status()
        self._show_stats(player, wrapper)
        if not self.game_over:
            self._maybe_ai_move()

    # ── Điều hướng ───────────────────────────────────────────────────────────

    def _new_game(self):
        self._game_id   += 1
        self.board       = Board(self.board_size, self.win_len)
        self.last_move   = None
        self.game_over   = False
        self.ai_thinking = False
        self.status_var.set("")
        self._init_log()
        self._draw_board()
        self._update_status()
        self._clear_stats()
        self._maybe_ai_move()

    def _open_setup(self):
        self._game_id += 1
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
