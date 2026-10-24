#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
merge_txt_gui.py
将指定目录（不含子目录）下的 .txt 文件合并为一个 .txt 文件，
新文件名默认使用目录名。带图形界面（tkinter，无需额外依赖）。

用法：
    直接双击运行，或在命令行执行：
        python merge_txt_gui.py
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext


def safe_read(path):
    """尝试以 UTF-8 读取，失败回退 GBK（Windows 常见中文 txt 编码）。"""
    with open(path, "rb") as f:
        raw = f.read()
    for enc in ("utf-8", "gbk", "utf-8-sig"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    # 最后手段：忽略无法解码的字节
    return raw.decode("utf-8", errors="ignore")


def collect_txt_files(directory, sort_mode):
    """收集目录下一层（不含子目录）的所有 .txt 文件，按指定方式排序。"""
    entries = []
    for name in os.listdir(directory):
        full = os.path.join(directory, name)
        if os.path.isfile(full) and name.lower().endswith(".txt"):
            entries.append(full)

    if sort_mode == "name_asc":
        entries.sort(key=lambda p: os.path.basename(p))
    elif sort_mode == "name_desc":
        entries.sort(key=lambda p: os.path.basename(p), reverse=True)
    elif sort_mode == "mtime":
        entries.sort(key=lambda p: os.path.getmtime(p))
    return entries


class MergeApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("TXT 合并工具")
        self.geometry("720x560")
        try:
            self.iconbitmap()  # 无图标则忽略
        except Exception:
            pass

        self.dir_var = tk.StringVar()
        self.out_var = tk.StringVar()
        self.sort_var = tk.StringVar(value="name_asc")
        self.sep_var = tk.StringVar(value="单空行")
        self.var_strip = tk.BooleanVar(value=True)

        self._build_ui()
        self._center_window()

    # ---------- UI ----------
    def _build_ui(self):
        pad = {"padx": 10, "pady": 6}

        # 1) 选择目录
        f1 = ttk.LabelFrame(self, text="1. 选择要合并的目录（仅该层，不含子目录）", padding=8)
        f1.pack(fill="x", **pad)
        ttk.Entry(f1, textvariable=self.dir_var, width=70).pack(side="left", fill="x", expand=True)
        ttk.Button(f1, text="浏览…", command=self._choose_dir).pack(side="left", padx=(6, 0))

        # 2) 选项
        f2 = ttk.LabelFrame(self, text="2. 合并选项", padding=8)
        f2.pack(fill="x", **pad)
        ttk.Label(f2, text="排序方式:").grid(row=0, column=0, sticky="w")
        ttk.Combobox(
            f2, textvariable=self.sort_var, width=18, state="readonly",
            values=["name_asc", "name_desc", "mtime"],
        ).grid(row=0, column=1, sticky="w", padx=6)
        ttk.Label(f2, text="文件名升序 / 文件名降序 / 修改时间").grid(row=0, column=2, sticky="w")

        ttk.Label(f2, text="文件间分隔:").grid(row=1, column=0, sticky="w", pady=(6, 0))
        ttk.Combobox(
            f2, textvariable=self.sep_var, width=18, state="readonly",
            values=["无", "单空行", "双空行", "文件名标题"],
        ).grid(row=1, column=1, sticky="w", padx=6, pady=(6, 0))
        ttk.Label(f2, text="(标题模式会在每个文件前加一行文件名)").grid(row=1, column=2, sticky="w", pady=(6, 0))
        ttk.Checkbutton(f2, text="去除每个文件内的空行（章内无空行，章间保留一个空行）", variable=self.var_strip).grid(row=2, column=0, columnspan=3, sticky="w", pady=(6, 0))

        # 3) 文件预览
        f3 = ttk.LabelFrame(self, text="3. 待合并文件（按上述顺序）", padding=8)
        f3.pack(fill="both", expand=True, **pad)
        self.preview = scrolledtext.ScrolledText(f3, height=12, state="disabled", wrap="none")
        self.preview.pack(fill="both", expand=True)

        # 4) 输出文件名
        f4 = ttk.LabelFrame(self, text="4. 输出文件", padding=8)
        f4.pack(fill="x", **pad)
        ttk.Label(f4, text="保存为:").pack(side="left")
        ttk.Entry(f4, textvariable=self.out_var, width=70).pack(side="left", fill="x", expand=True, padx=(6, 0))
        ttk.Button(f4, text="另存为…", command=self._choose_out).pack(side="left", padx=(6, 0))

        # 5) 操作
        f5 = ttk.Frame(self)
        f5.pack(fill="x", **pad)
        ttk.Button(f5, text="开始合并", command=self._merge).pack(side="right")
        ttk.Button(f5, text="刷新预览", command=self._refresh).pack(side="right", padx=(0, 8))
        self.status = ttk.Label(f5, text="请先选择目录")
        self.status.pack(side="left")

    def _center_window(self):
        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    # ---------- 交互 ----------
    def _choose_dir(self):
        d = filedialog.askdirectory(title="选择包含 txt 的目录")
        if not d:
            return
        self.dir_var.set(d)
        # 默认输出：父目录 / <目录名>.txt
        default_out = os.path.join(os.path.dirname(d), os.path.basename(d) + ".txt")
        self.out_var.set(default_out)
        self._refresh()

    def _choose_out(self):
        if not self.dir_var.get():
            messagebox.showwarning("提示", "请先选择目录")
            return
        d = filedialog.asksaveasfilename(
            title="选择输出文件",
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")],
            initialfile=os.path.basename(self.out_var.get() or "output.txt"),
        )
        if d:
            self.out_var.set(d)

    def _refresh(self):
        directory = self.dir_var.get()
        if not directory or not os.path.isdir(directory):
            self.status.config(text="目录无效")
            return
        files = collect_txt_files(directory, self.sort_var.get())
        self.preview.config(state="normal")
        self.preview.delete("1.0", "end")
        if not files:
            self.preview.insert("end", "（该目录下没有找到 .txt 文件）")
        else:
            for i, f in enumerate(files, 1):
                self.preview.insert("end", f"{i:>3}. {os.path.basename(f)}\n")
        self.preview.config(state="disabled")
        self.status.config(text=f"找到 {len(files)} 个 txt 文件")

    def _sep_text(self):
        return {"无": "", "单空行": "\n", "双空行": "\n\n", "文件名标题": None}[self.sep_var.get()]

    def _merge(self):
        directory = self.dir_var.get()
        out = self.out_var.get()
        if not directory or not os.path.isdir(directory):
            messagebox.showerror("错误", "请先选择有效的目录")
            return
        if not out:
            messagebox.showerror("错误", "请指定输出文件")
            return

        files = collect_txt_files(directory, self.sort_var.get())
        if not files:
            messagebox.showwarning("提示", "该目录下没有 .txt 文件，无需合并")
            return

        sep = self._sep_text()
        strip = self.var_strip.get()
        try:
            with open(out, "w", encoding="utf-8") as out_f:
                first = True
                for f in files:
                    content = safe_read(f)
                    # 去除每个文件内的所有空行（仅空白的行），章内不留空行
                    if strip:
                        # 先把 \r\n / \r 统一为 \n，避免拆分后残留 \r
                        content = content.replace("\r\n", "\n").replace("\r", "\n")
                        content = "\n".join(ln for ln in content.split("\n") if ln.strip())
                    if not content:
                        continue  # 跳过完全为空的章节，避免产生多余空行
                    if not first and sep is not None:
                        out_f.write(sep)  # 章间分隔（默认单空行 = 一个空行）
                    first = False
                    if sep is None:  # 文件名标题模式
                        out_f.write(f"===== {os.path.basename(f)} =====\n\n")
                    out_f.write(content)
                    # 确保文件内容以换行结尾
                    if not content.endswith("\n"):
                        out_f.write("\n")
            size = os.path.getsize(out)
            self.status.config(text=f"完成：已合并 {len(files)} 个文件 → {out}（{size:,} 字节）")
            messagebox.showinfo("完成", f"已合并 {len(files)} 个文件\n保存到：\n{out}")
        except Exception as e:
            messagebox.showerror("合并失败", str(e))
            self.status.config(text="合并失败：" + str(e))


def main():
    app = MergeApp()
    app.mainloop()


if __name__ == "__main__":
    main()
