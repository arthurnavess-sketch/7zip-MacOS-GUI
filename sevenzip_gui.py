#!/usr/bin/env python3
"""
7-Zip GUI para macOS (Intel) — versão autocontida
--------------------------------------------------
Interface gráfica em Tkinter para compactar/extrair arquivos nos formatos
.7z, .zip, .tar, .tar.gz e .tar.bz2.

Diferente da primeira versão, este app NÃO depende de nenhum binário
externo (como o 'p7zip' via Homebrew): usa a biblioteca Python pura
'py7zr' para o formato .7z, e os módulos padrão 'zipfile'/'tarfile' para
os demais formatos. Isso permite empacotar tudo dentro de um único .app
autossuficiente, ideal para gerar um .dmg distribuível.
"""

import os
import tarfile
import threading
import zipfile
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

try:
    import py7zr
except ImportError:  # tratado em tempo de execução na UI
    py7zr = None

APP_TITLE = "7-Zip GUI"
FORMATS = ["7z", "zip", "tar", "tar.gz", "tar.bz2"]


class SevenZipGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("640x480")
        self.minsize(560, 420)

        self.selected_paths = []

        self._build_widgets()

        if py7zr is None:
            self._log(
                "AVISO: módulo 'py7zr' não encontrado. O suporte a .7z ficará "
                "desativado até reinstalar as dependências (pip3 install py7zr).\n"
            )

    # ---------- UI ----------

    def _build_widgets(self):
        pad = {"padx": 10, "pady": 6}

        top_frame = ttk.Frame(self)
        top_frame.pack(fill="x", **pad)

        ttk.Button(top_frame, text="Selecionar arquivos...", command=self.pick_files).pack(
            side="left", padx=(0, 6)
        )
        ttk.Button(top_frame, text="Selecionar pasta...", command=self.pick_folder).pack(
            side="left", padx=(0, 6)
        )
        ttk.Button(top_frame, text="Limpar seleção", command=self.clear_selection).pack(
            side="left"
        )

        self.selection_var = tk.StringVar(value="Nenhum item selecionado.")
        ttk.Label(self, textvariable=self.selection_var, wraplength=600, foreground="#555").pack(
            fill="x", **pad
        )

        action_frame = ttk.LabelFrame(self, text="Ações")
        action_frame.pack(fill="x", **pad)

        compress_row = ttk.Frame(action_frame)
        compress_row.pack(fill="x", padx=8, pady=8)

        ttk.Label(compress_row, text="Formato:").pack(side="left")
        self.format_var = tk.StringVar(value="7z")
        ttk.Combobox(
            compress_row,
            textvariable=self.format_var,
            values=FORMATS,
            width=8,
            state="readonly",
        ).pack(side="left", padx=(6, 16))

        ttk.Button(compress_row, text="Compactar...", command=self.compress).pack(side="right")

        extract_row = ttk.Frame(action_frame)
        extract_row.pack(fill="x", padx=8, pady=(0, 8))
        ttk.Button(extract_row, text="Extrair arquivo...", command=self.extract).pack(side="left")

        log_frame = ttk.LabelFrame(self, text="Log")
        log_frame.pack(fill="both", expand=True, **pad)

        self.log_text = tk.Text(log_frame, height=12, wrap="word", state="disabled")
        self.log_text.pack(fill="both", expand=True, padx=6, pady=6)

        self.progress = ttk.Progressbar(self, mode="indeterminate")
        self.progress.pack(fill="x", padx=10, pady=(0, 10))

    # ---------- Seleção ----------

    def pick_files(self):
        paths = filedialog.askopenfilenames(title="Selecione arquivos")
        if paths:
            self.selected_paths = list(paths)
            self._update_selection_label()

    def pick_folder(self):
        path = filedialog.askdirectory(title="Selecione uma pasta")
        if path:
            self.selected_paths = [path]
            self._update_selection_label()

    def clear_selection(self):
        self.selected_paths = []
        self._update_selection_label()

    def _update_selection_label(self):
        if not self.selected_paths:
            self.selection_var.set("Nenhum item selecionado.")
        elif len(self.selected_paths) == 1:
            self.selection_var.set(f"Selecionado: {self.selected_paths[0]}")
        else:
            self.selection_var.set(f"{len(self.selected_paths)} itens selecionados.")

    # ---------- Compactar ----------

    def compress(self):
        if not self.selected_paths:
            messagebox.showwarning(APP_TITLE, "Selecione arquivos ou uma pasta primeiro.")
            return

        fmt = self.format_var.get()
        if fmt == "7z" and py7zr is None:
            messagebox.showerror(
                APP_TITLE, "Suporte a .7z indisponível (módulo py7zr ausente)."
            )
            return

        default_name = os.path.splitext(os.path.basename(self.selected_paths[0]))[0] or "arquivo"
        ext = "tar.gz" if fmt == "tar.gz" else "tar.bz2" if fmt == "tar.bz2" else fmt
        dest = filedialog.asksaveasfilename(
            title="Salvar arquivo compactado como",
            defaultextension=f".{ext}",
            initialfile=f"{default_name}.{ext}",
        )
        if not dest:
            return

        self._run_async(lambda: self._do_compress(fmt, dest), f"Compactando para {dest} ...")

    def _do_compress(self, fmt, dest):
        if fmt == "7z":
            with py7zr.SevenZipFile(dest, "w") as archive:
                for path in self.selected_paths:
                    arcname = os.path.basename(path)
                    archive.writeall(path, arcname)
        elif fmt == "zip":
            with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as zf:
                for path in self.selected_paths:
                    self._add_to_zip(zf, path)
        else:  # tar, tar.gz, tar.bz2
            mode = {"tar": "w", "tar.gz": "w:gz", "tar.bz2": "w:bz2"}[fmt]
            with tarfile.open(dest, mode) as tf:
                for path in self.selected_paths:
                    tf.add(path, arcname=os.path.basename(path))
        return f"Arquivo criado: {dest}"

    def _add_to_zip(self, zf, path):
        if os.path.isdir(path):
            base = os.path.dirname(path)
            for root, _dirs, files in os.walk(path):
                for f in files:
                    full = os.path.join(root, f)
                    zf.write(full, os.path.relpath(full, base))
        else:
            zf.write(path, os.path.basename(path))

    # ---------- Extrair ----------

    def extract(self):
        archive = filedialog.askopenfilename(
            title="Selecione o arquivo compactado",
            filetypes=[
                ("Arquivos compactados", "*.7z *.zip *.tar *.tar.gz *.tgz *.tar.bz2 *.tbz2"),
                ("Todos os arquivos", "*.*"),
            ],
        )
        if not archive:
            return

        out_dir = filedialog.askdirectory(title="Escolha a pasta de destino")
        if not out_dir:
            return

        self._run_async(
            lambda: self._do_extract(archive, out_dir), f"Extraindo {archive} para {out_dir} ..."
        )

    def _do_extract(self, archive, out_dir):
        lower = archive.lower()
        if lower.endswith(".7z"):
            if py7zr is None:
                raise RuntimeError("Suporte a .7z indisponível (módulo py7zr ausente).")
            with py7zr.SevenZipFile(archive, "r") as zf:
                zf.extractall(path=out_dir)
        elif lower.endswith(".zip"):
            with zipfile.ZipFile(archive, "r") as zf:
                zf.extractall(path=out_dir)
        elif lower.endswith((".tar", ".tar.gz", ".tgz", ".tar.bz2", ".tbz2")):
            with tarfile.open(archive, "r:*") as tf:
                tf.extractall(path=out_dir)
        else:
            raise RuntimeError("Formato não reconhecido.")
        return f"Extraído em: {out_dir}"

    # ---------- Execução assíncrona ----------

    def _run_async(self, func, start_message):
        self._log(f"\n{start_message}\n")
        self.progress.start(12)
        thread = threading.Thread(target=self._run_safe, args=(func,), daemon=True)
        thread.start()

    def _run_safe(self, func):
        try:
            message = func()
            self.after(0, self._on_done, True, message)
        except Exception as exc:
            self.after(0, self._on_done, False, str(exc))

    def _on_done(self, success, message):
        self.progress.stop()
        self._log(message + "\n")
        if success:
            self._log("✅ Concluído com sucesso.\n")
        else:
            self._log("❌ Erro. Veja a mensagem acima.\n")
            messagebox.showerror(APP_TITLE, message)

    def _log(self, text):
        self.log_text.configure(state="normal")
        self.log_text.insert("end", text)
        self.log_text.see("end")
        self.log_text.configure(state="disabled")


if __name__ == "__main__":
    app = SevenZipGUI()
    app.mainloop()
