# merge_txt_gui — TXT 批量合并工具

把指定目录（不含子目录）下的所有 `.txt` 文件合并为一个 `.txt` 文件，
输出文件名默认取目录名。tkinter GUI，无第三方依赖。

## 用法

双击 `merge_txt_gui.bat`，或：

```bash
python merge_txt_gui.py
```

## 功能

- 选择源目录 → 自动列出待合并文件 → 一键合并
- 读取时自动尝试 UTF-8，失败回退 GBK（兼容 Windows 常见中文 txt 编码）
- 合并结果保存为 `<目录名>.txt`
