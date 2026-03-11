
import sys, os, json, tkinter as tk
from tkinter import ttk, messagebox

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.learning import record_override, get_stats
from utils.reports import generate_daily_report, list_reports

SCHED_CFG = os.path.join(os.path.dirname(__file__), "..", "config", "scheduler.json")
NOTIF_CFG = os.path.join(os.path.dirname(__file__), "..", "config", "notifier.json")

class ControlPanel(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SmartBot Control Panel")
        self.geometry("700x520")
        self.configure(bg="#1e1e2e")
        self._build()

    def _btn(self, parent, text, cmd):
        return tk.Button(parent, text=text, command=cmd, bg="#89b4fa", fg="#1e1e2e",
                         font=("Helvetica",10,"bold"), relief="flat", padx=12, pady=6)

    def _build(self):
        tk.Label(self, text="SmartBot Control Panel", font=("Helvetica",16,"bold"),
                 fg="#cdd6f4", bg="#1e1e2e").pack(pady=(15,5))
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=15, pady=10)

        # Tasks tab
        tf = tk.Frame(nb, bg="#181825"); nb.add(tf, text=" Tasks ")
        cfg = json.load(open(SCHED_CFG))
        self._task_vars = {}
        tk.Label(tf, text="Enable / Disable Tasks", bg="#181825", fg="#a6adc8",
                 font=("Helvetica",11,"bold")).pack(pady=10)
        for name, tcfg in cfg.get("tasks",{}).items():
            var = tk.BooleanVar(value=tcfg.get("enabled", False))
            self._task_vars[name] = var
            row = tk.Frame(tf, bg="#181825"); row.pack(fill="x", padx=20, pady=2)
            tk.Checkbutton(row, text=name, variable=var, bg="#181825", fg="#cdd6f4",
                           selectcolor="#313244", activebackground="#181825",
                           font=("Helvetica",10)).pack(side="left")
            tk.Label(row, text=tcfg.get("description",""), bg="#181825", fg="#585b70",
                     font=("Helvetica",9)).pack(side="left", padx=8)
        self._btn(tf, "Save Task Settings", self._save_tasks).pack(pady=12)

        # Notifications tab
        nf = tk.Frame(nb, bg="#181825"); nb.add(nf, text=" Notifications ")
        ncfg = json.load(open(NOTIF_CFG))
        self._notif_vars = {}
        tk.Label(nf, text="Notification Channels", bg="#181825", fg="#a6adc8",
                 font=("Helvetica",11,"bold")).pack(pady=10)
        for ch in ["desktop","email","slack"]:
            var = tk.BooleanVar(value=ncfg.get(ch,{}).get("enabled",False))
            self._notif_vars[ch] = var
            tk.Checkbutton(nf, text=f"Enable {ch.title()}", variable=var, bg="#181825",
                           fg="#cdd6f4", selectcolor="#313244", activebackground="#181825",
                           font=("Helvetica",10)).pack(anchor="w", padx=25, pady=3)
        self._btn(nf, "Save", self._save_notif).pack(pady=12)

        # Override tab
        of = tk.Frame(nb, bg="#181825"); nb.add(of, text=" Override Learning ")
        tk.Label(of, text="Record Manual Override", bg="#181825", fg="#a6adc8",
                 font=("Helvetica",11,"bold")).pack(pady=10)
        self._ov_entries = {}
        for label, placeholder in [
            ("Module","file_organizer"), ("Original Action","move to /images"),
            ("Override Action","move to /projects"), ("Target","report.pdf"), ("Reason","")
        ]:
            row = tk.Frame(of, bg="#181825"); row.pack(fill="x", padx=25, pady=3)
            tk.Label(row, text=label, width=18, anchor="w", bg="#181825", fg="#a6adc8",
                     font=("Helvetica",10)).pack(side="left")
            e = tk.Entry(row, bg="#313244", fg="#cdd6f4", insertbackground="#cdd6f4",
                         font=("Helvetica",10), width=32)
            e.insert(0, placeholder); e.pack(side="left", padx=4)
            self._ov_entries[label] = e
        self._btn(of, "Record Override", self._save_override).pack(pady=10)
        s = get_stats()
        tk.Label(of, text=f"Overrides: {s.get('total_overrides',0)}  Rules: {s.get('model_rules',0)}",
                 bg="#181825", fg="#585b70", font=("Helvetica",9)).pack()

        # Reports tab
        rf = tk.Frame(nb, bg="#181825"); nb.add(rf, text=" Reports ")
        tk.Label(rf, text="Available Reports", bg="#181825", fg="#a6adc8",
                 font=("Helvetica",11,"bold")).pack(pady=10)
        lb_frame = tk.Frame(rf, bg="#181825"); lb_frame.pack(fill="both", expand=True, padx=20)
        sb = tk.Scrollbar(lb_frame); sb.pack(side="right", fill="y")
        lb = tk.Listbox(lb_frame, bg="#313244", fg="#cdd6f4", font=("Courier",10),
                        selectbackground="#585b70", yscrollcommand=sb.set)
        for r in list_reports(): lb.insert("end", r)
        lb.pack(fill="both", expand=True); sb.config(command=lb.yview)
        self._btn(rf, "Generate Today's Report", lambda: messagebox.showinfo(
            "Done", generate_daily_report())).pack(pady=10)

    def _save_tasks(self):
        cfg = json.load(open(SCHED_CFG))
        for name, var in self._task_vars.items():
            if name in cfg["tasks"]:
                cfg["tasks"][name]["enabled"] = var.get()
        json.dump(cfg, open(SCHED_CFG,"w"), indent=2)
        messagebox.showinfo("Saved", "Task settings saved. Restart bot to apply.")

    def _save_notif(self):
        cfg = json.load(open(NOTIF_CFG))
        for ch, var in self._notif_vars.items():
            if ch in cfg: cfg[ch]["enabled"] = var.get()
        json.dump(cfg, open(NOTIF_CFG,"w"), indent=2)
        messagebox.showinfo("Saved", "Notification settings saved.")

    def _save_override(self):
        e = self._ov_entries
        record_override(e["Module"].get(), e["Original Action"].get(),
                        e["Override Action"].get(), e["Target"].get(), e["Reason"].get())
        messagebox.showinfo("Recorded", "Override saved and model updated.")

if __name__ == "__main__":
    ControlPanel().mainloop()