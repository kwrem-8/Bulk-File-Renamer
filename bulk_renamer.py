import tkinter as tk
from tkinter import filedialog, messagebox
import os
import re


DARK = {
    "bg": "#1e1e1e",
    "panel": "#252525",
    "card": "#2d2d2d",
    "border": "#3a3a3a",
    "text": "#e0e0e0",
    "muted": "#888888",
    "accent": "#4a90d9",
    "accent_hover": "#357abd",
    "danger": "#d9534a",
    "success": "#4aad6f",
    "input_bg": "#333333",
}


class FileRenamer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Bulk File Renamer")
        self.geometry("920x620")
        self.minsize(760, 500)
        self.configure(bg=DARK["bg"])

        self.folder = None
        self.files = []
        self.history = []

        self._build_ui()

    def _build_ui(self):
        top = tk.Frame(self, bg=DARK["bg"])
        top.pack(fill=tk.X, padx=16, pady=(14, 0))

        tk.Button(
            top, text="Klasör Seç",
            command=self.pick_folder,
            bg=DARK["accent"], fg="#ffffff",
            activebackground=DARK["accent_hover"], activeforeground="#ffffff",
            relief=tk.FLAT, font=("Segoe UI", 9), padx=12, pady=6, cursor="hand2"
        ).pack(side=tk.LEFT)

        self.folder_label = tk.Label(
            top, text="Henüz klasör seçilmedi",
            bg=DARK["bg"], fg=DARK["muted"],
            font=("Segoe UI", 9)
        )
        self.folder_label.pack(side=tk.LEFT, padx=12)

        body = tk.Frame(self, bg=DARK["bg"])
        body.pack(fill=tk.BOTH, expand=True, padx=16, pady=12)

        left = tk.Frame(body, bg=DARK["panel"], width=280)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left.pack_propagate(False)

        right = tk.Frame(body, bg=DARK["bg"])
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._build_preview(right)
        self._build_controls(left)
        self._build_bottom()

    def _label(self, parent, text):
        tk.Label(
            parent, text=text,
            bg=DARK["panel"], fg=DARK["muted"],
            font=("Segoe UI", 8)
        ).pack(anchor="w", padx=12, pady=(10, 2))

    def _entry(self, parent, var):
        e = tk.Entry(
            parent, textvariable=var,
            bg=DARK["input_bg"], fg=DARK["text"],
            insertbackground=DARK["text"],
            relief=tk.FLAT, font=("Segoe UI", 9),
            bd=0
        )
        e.pack(fill=tk.X, padx=12, ipady=5)
        e.bind("<KeyRelease>", self._refresh_preview)
        return e

    def _build_controls(self, parent):
        tk.Label(
            parent, text="YENIDEN ADLANDIR",
            bg=DARK["panel"], fg=DARK["muted"],
            font=("Segoe UI", 8, "bold")
        ).pack(anchor="w", padx=12, pady=(14, 0))

        tk.Frame(parent, bg=DARK["border"], height=1).pack(fill=tk.X, padx=12, pady=6)

        self.mode_var = tk.StringVar(value="prefix")

        modes = [
            ("prefix",  "Önek ekle"),
            ("suffix",  "Sonek ekle"),
            ("replace", "Bul & Değiştir"),
            ("regex",   "Regex"),
            ("number",  "Numaralandır"),
        ]

        for value, label in modes:
            tk.Radiobutton(
                parent, text=label, variable=self.mode_var, value=value,
                command=self._on_mode_change,
                bg=DARK["panel"], fg=DARK["text"],
                selectcolor=DARK["panel"], activebackground=DARK["panel"],
                activeforeground=DARK["text"],
                font=("Segoe UI", 9)
            ).pack(anchor="w", padx=14, pady=1)

        tk.Frame(parent, bg=DARK["border"], height=1).pack(fill=tk.X, padx=12, pady=8)

        self.input1_var = tk.StringVar()
        self.input2_var = tk.StringVar()
        self.input3_var = tk.StringVar()

        self.label1 = tk.Label(parent, bg=DARK["panel"], fg=DARK["muted"], font=("Segoe UI", 8))
        self.label1.pack(anchor="w", padx=12, pady=(0, 2))
        self.entry1 = self._entry(parent, self.input1_var)

        self.label2 = tk.Label(parent, bg=DARK["panel"], fg=DARK["muted"], font=("Segoe UI", 8))
        self.label2.pack(anchor="w", padx=12, pady=(8, 2))
        self.entry2 = self._entry(parent, self.input2_var)

        self.label3 = tk.Label(parent, bg=DARK["panel"], fg=DARK["muted"], font=("Segoe UI", 8))
        self.label3.pack(anchor="w", padx=12, pady=(8, 2))
        self.entry3 = self._entry(parent, self.input3_var)

        tk.Frame(parent, bg=DARK["border"], height=1).pack(fill=tk.X, padx=12, pady=8)

        self._label(parent, "UZANTI FİLTRESİ  (örn: .jpg .png)")
        self.ext_var = tk.StringVar()
        e = tk.Entry(
            parent, textvariable=self.ext_var,
            bg=DARK["input_bg"], fg=DARK["text"],
            insertbackground=DARK["text"],
            relief=tk.FLAT, font=("Segoe UI", 9), bd=0
        )
        e.pack(fill=tk.X, padx=12, ipady=5)
        e.bind("<KeyRelease>", self._refresh_preview)

        self._on_mode_change()

    def _build_preview(self, parent):
        header = tk.Frame(parent, bg=DARK["bg"])
        header.pack(fill=tk.X, pady=(0, 6))

        tk.Label(
            header, text="ÖNCEKİ AD",
            bg=DARK["bg"], fg=DARK["muted"],
            font=("Segoe UI", 8, "bold"), width=38, anchor="w"
        ).pack(side=tk.LEFT)

        tk.Label(
            header, text="YENİ AD",
            bg=DARK["bg"], fg=DARK["muted"],
            font=("Segoe UI", 8, "bold"), anchor="w"
        ).pack(side=tk.LEFT)

        frame = tk.Frame(parent, bg=DARK["card"], bd=0)
        frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(frame, bg=DARK["card"], troughcolor=DARK["card"], bd=0)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.listbox = tk.Listbox(
            frame,
            bg=DARK["card"], fg=DARK["text"],
            selectbackground=DARK["accent"],
            activestyle="none",
            relief=tk.FLAT, bd=0,
            font=("Consolas", 9),
            yscrollcommand=scrollbar.set
        )
        self.listbox.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        scrollbar.config(command=self.listbox.yview)

        self.status_label = tk.Label(
            parent, text="",
            bg=DARK["bg"], fg=DARK["muted"],
            font=("Segoe UI", 8)
        )
        self.status_label.pack(anchor="w", pady=(4, 0))

    def _build_bottom(self):
        bar = tk.Frame(self, bg=DARK["panel"])
        bar.pack(fill=tk.X, padx=16, pady=(0, 14))

        tk.Button(
            bar, text="Uygula",
            command=self.apply,
            bg=DARK["success"], fg="#ffffff",
            activebackground="#3d9960", activeforeground="#ffffff",
            relief=tk.FLAT, font=("Segoe UI", 9, "bold"),
            padx=16, pady=7, cursor="hand2"
        ).pack(side=tk.LEFT, padx=(0, 8))

        tk.Button(
            bar, text="Geri Al",
            command=self.undo,
            bg=DARK["card"], fg=DARK["text"],
            activebackground=DARK["border"], activeforeground=DARK["text"],
            relief=tk.FLAT, font=("Segoe UI", 9),
            padx=14, pady=7, cursor="hand2"
        ).pack(side=tk.LEFT)

        self.result_label = tk.Label(
            bar, text="",
            bg=DARK["panel"], fg=DARK["muted"],
            font=("Segoe UI", 9)
        )
        self.result_label.pack(side=tk.RIGHT, padx=8)

    def _on_mode_change(self, *_):
        mode = self.mode_var.get()

        configs = {
            "prefix":  [("Eklenecek önek", "", None, None, None, None)],
            "suffix":  [("Eklenecek sonek (uzantı hariç)", "", None, None, None, None)],
            "replace": [("Aranacak metin", ""), ("Yeni metin", "")],
            "regex":   [("Regex deseni", ""), ("Yeni metin  ($1, $2 grup ref.)", ""), ("Bayraklar  (i=büyük/küçük harf, g=hepsi)", "")],
            "number":  [("Başlangıç numarası", "1"), ("Şablon  ({n} = numara, {name} = orijinal ad)", "{n}_{name}")],
        }

        labels = [self.label1, self.label2, self.label3]
        entries = [self.entry1, self.entry2, self.entry3]
        vars_ = [self.input1_var, self.input2_var, self.input3_var]

        rows = configs[mode]

        for i, lbl in enumerate(labels):
            if i < len(rows):
                lbl.config(text=rows[i][0])
                lbl.pack(anchor="w", padx=12, pady=(8 if i > 0 else 0, 2))
                entries[i].pack(fill=tk.X, padx=12, ipady=5)
                if rows[i][1] is not None:
                    vars_[i].set(rows[i][1])
            else:
                lbl.pack_forget()
                entries[i].pack_forget()

        self._refresh_preview()

    def pick_folder(self):
        path = filedialog.askdirectory()
        if not path:
            return
        self.folder = path
        self.folder_label.config(text=path, fg=DARK["text"])
        self._load_files()

    def _load_files(self):
        if not self.folder:
            return
        try:
            self.files = sorted([
                f for f in os.listdir(self.folder)
                if os.path.isfile(os.path.join(self.folder, f))
            ])
        except Exception as e:
            messagebox.showerror("Hata", str(e))
            return
        self._refresh_preview()

    def _filtered_files(self):
        raw = self.ext_var.get().strip()
        if not raw:
            return self.files
        exts = [x.strip().lower() for x in raw.split() if x.strip()]
        return [f for f in self.files if os.path.splitext(f)[1].lower() in exts]

    def _compute_new_name(self, filename, index):
        mode = self.mode_var.get()
        name, ext = os.path.splitext(filename)

        try:
            if mode == "prefix":
                prefix = self.input1_var.get()
                return prefix + filename

            if mode == "suffix":
                suffix = self.input1_var.get()
                return name + suffix + ext

            if mode == "replace":
                find = self.input1_var.get()
                replace = self.input2_var.get()
                if not find:
                    return filename
                new_name = filename.replace(find, replace)
                return new_name

            if mode == "regex":
                pattern = self.input1_var.get()
                replacement = self.input2_var.get()
                flags_str = self.input3_var.get().lower()
                if not pattern:
                    return filename
                flags = 0
                if "i" in flags_str:
                    flags |= re.IGNORECASE
                replacement = replacement.replace("$", "\\")
                new_name = re.sub(pattern, replacement, filename, flags=flags)
                return new_name

            if mode == "number":
                try:
                    start = int(self.input1_var.get() or "1")
                except ValueError:
                    start = 1
                template = self.input2_var.get() or "{n}_{name}"
                n = start + index
                new_name = template.replace("{n}", str(n)).replace("{name}", name)
                return new_name + ext

        except Exception:
            return filename

        return filename

    def _refresh_preview(self, *_):
        if not hasattr(self, 'listbox'):
            return
        self.listbox.delete(0, tk.END)
        files = self._filtered_files()

        if not files:
            self.status_label.config(text="Dosya bulunamadı")
            return

        changed = 0
        for i, filename in enumerate(files):
            new_name = self._compute_new_name(filename, i)
            if new_name != filename:
                changed += 1
                line = f"{filename:<40}  →  {new_name}"
                self.listbox.insert(tk.END, line)
                self.listbox.itemconfig(tk.END, fg=DARK["accent"])
            else:
                line = f"{filename:<40}  —"
                self.listbox.insert(tk.END, line)
                self.listbox.itemconfig(tk.END, fg=DARK["muted"])

        self.status_label.config(
            text=f"{len(files)} dosya  |  {changed} değişecek"
        )

    def apply(self):
        if not self.folder:
            messagebox.showwarning("Uyarı", "Önce bir klasör seçin.")
            return

        files = self._filtered_files()
        if not files:
            messagebox.showinfo("Bilgi", "Yeniden adlandırılacak dosya yok.")
            return

        batch = []
        for i, filename in enumerate(files):
            new_name = self._compute_new_name(filename, i)
            if new_name != filename:
                src = os.path.join(self.folder, filename)
                dst = os.path.join(self.folder, new_name)
                if os.path.exists(dst):
                    messagebox.showerror("Hata", f"Hedef dosya zaten var:\n{new_name}")
                    return
                batch.append((src, dst, filename, new_name))

        if not batch:
            messagebox.showinfo("Bilgi", "Değiştirilecek dosya bulunamadı.")
            return

        confirmed = messagebox.askyesno(
            "Onayla",
            f"{len(batch)} dosya yeniden adlandırılacak. Devam edilsin mi?"
        )
        if not confirmed:
            return

        done = []
        try:
            for src, dst, old, new in batch:
                os.rename(src, dst)
                done.append((dst, src, new, old))
        except Exception as e:
            for dst, src, _, _ in done:
                try:
                    os.rename(dst, src)
                except Exception:
                    pass
            messagebox.showerror("Hata", f"İşlem başarısız:\n{e}\nDeğişiklikler geri alındı.")
            return

        self.history.append(done)
        self.result_label.config(
            text=f"✓ {len(done)} dosya yeniden adlandırıldı",
            fg=DARK["success"]
        )
        self._load_files()

    def undo(self):
        if not self.history:
            messagebox.showinfo("Bilgi", "Geri alınacak işlem yok.")
            return

        batch = self.history.pop()
        errors = []

        for dst, src, _, _ in reversed(batch):
            try:
                os.rename(dst, src)
            except Exception as e:
                errors.append(str(e))

        if errors:
            messagebox.showerror("Hata", "\n".join(errors))
        else:
            self.result_label.config(
                text=f"↩ {len(batch)} işlem geri alındı",
                fg=DARK["muted"]
            )

        self._load_files()


if __name__ == "__main__":
    app = FileRenamer()
    app.mainloop()
