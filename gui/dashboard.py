
import sys, os, tkinter as tk
from tkinter import ttk, scrolledtext
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.logger import read_action_log
from utils.reports import get_summary_stats
from utils.learning import get_stats as learning_stats

class Dashboard(tk.Tk):
    REFRESH = 10_000

    def __init__(self):
        super().__init__()
        self.title("SmartBot Dashboard")
        self.geometry("900x600")
        self.configure(bg="#1e1e2e")
        self._build()
        self._refresh()
        self.after(self.REFRESH, self._schedule)

    def _build(self):
        top = tk.Frame(self, bg="#1e1e2e")
        top.pack(fill="x", padx=15, pady=(15,5))
        tk.Label(top, text="SmartBot Dashboard", font=("Helvetica",18,"bold"),
                 fg="#cdd6f4", bg="#1e1e2e").pack(side="left")
        self.status = tk.Label(top, text="● Running", font=("Helvetica",11),
                               fg="#a6e3a1", bg="#1e1e2e")
        self.status.pack(side="right")

        cards_frame = tk.Frame(self, bg="#1e1e2e")
        cards_frame.pack(fill="x", padx=15, pady=5)
        self.cards = {}
        for label in ["Total Actions", "Files Moved", "Overrides", "Active Jobs"]:
            f = tk.Frame(cards_frame, bg="#313244")
            f.pack(side="left", padx=5, expand=True, fill="both")
            tk.Label(f, text=label, bg="#313244", fg="#a6adc8", font=("Helvetica",9)).pack(pady=(8,2))
            v = tk.Label(f, text="—", bg="#313244", fg="#cba6f7", font=("Helvetica",20,"bold"))
            v.pack(pady=(0,8))
            self.cards[label] = v

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=15, pady=10)

        log_f = tk.Frame(nb, bg="#181825")
        nb.add(log_f, text=" Log ")
        self.log_box = scrolledtext.ScrolledText(log_f, bg="#181825", fg="#cdd6f4",
                                                  font=("Courier",10), state="disabled")
        self.log_box.pack(fill="both", expand=True, padx=5, pady=5)

        stats_f = tk.Frame(nb, bg="#181825")
        nb.add(stats_f, text=" Stats ")
        self.stats_box = scrolledtext.ScrolledText(stats_f, bg="#181825", fg="#cdd6f4",
                                                    font=("Courier",10), state="disabled")
        self.stats_box.pack(fill="both", expand=True, padx=5, pady=5)

        self.ts = tk.Label(self, text="", bg="#1e1e2e", fg="#585b70", font=("Helvetica",9))
        self.ts.pack(side="bottom", pady=(0,8))

    def _refresh(self):
        records = read_action_log()[-50:]
        lines = []
        for r in reversed(records):
            lines.append(f"{r.get('timestamp','')[:19]}  {r.get('level','').ljust(7)}  "
                         f"{r.get('module','').ljust(15)}  {r.get('action','')}: {r.get('detail','')}")
        self.log_box.config(state="normal")
        self.log_box.delete("1.0","end")
        self.log_box.insert("end", "\n".join(lines) or "No actions yet.")
        self.log_box.config(state="disabled")

        day = get_summary_stats()
        ls = learning_stats()
        self.cards["Total Actions"].config(text=str(day.get("total_actions",0)))
        self.cards["Files Moved"].config(text=str(day.get("by_action",{}).get("MOVE",0)))
        self.cards["Overrides"].config(text=str(ls.get("total_overrides",0)))
        try:
            import schedule
            self.cards["Active Jobs"].config(text=str(len(schedule.jobs)))
        except Exception:
            pass

        stats_lines = [
            "=== Today ===",
            f"Total : {day.get('total_actions',0)}",
            f"Modules: {day.get('by_module',{})}",
            f"Actions: {day.get('by_action',{})}",
            "", "=== Learning ===",
            f"Overrides : {ls.get('total_overrides',0)}",
            f"Rules     : {ls.get('model_rules',0)}",
        ]
        self.stats_box.config(state="normal")
        self.stats_box.delete("1.0","end")
        self.stats_box.insert("end", "\n".join(stats_lines))
        self.stats_box.config(state="disabled")
        self.ts.config(text=f"Refreshed: {datetime.now().strftime('%H:%M:%S')}")

    def _schedule(self):
        self._refresh()
        self.after(self.REFRESH, self._schedule)

if __name__ == "__main__":
    Dashboard().mainloop()