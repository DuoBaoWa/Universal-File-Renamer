# 通用文件重命名工具 / Universal File Renamer

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)![License](https://img.shields.io/badge/License-MIT-green)

## 📖 简介 / Introduction

一款基于Python Tkinter开发的跨平台文件批量重命名工具，支持多种重命名规则和撤销功能。提供直观的GUI界面，操作简单安全。

A cross-platform batch file renaming tool developed with Python Tkinter, supporting multiple renaming rules and undo functionality. Features an intuitive GUI interface with safe operation.



## ✨ 功能特性 / Features

### 核心功能 / Core Features

- **多重命名规则**：前缀/后缀、文本替换、正则表达式、序号生成、日期前缀
- **安全机制**：自动创建备份文件夹，支持完整操作撤销
- **实时预览**：在执行前显示重命名结果预览
- **批量处理**：支持同时处理数千个文件
- **跨平台**：支持Windows/macOS/Linux

### 规则说明 / Rule Details

| 规则类型 | 参数示例               | 效果示例                           |
| -------- | ---------------------- | ---------------------------------- |
| 添加前缀 | 前缀: "IMG_"           | photo.jpg → IMG_photo.jpg          |
| 正则替换 | 模式: `\d+`, 替换: NUM | file123.txt → fileNUM.txt          |
| 序号生成 | 格式: {n:03d}          | document.pdf → 001.pdf             |
| 日期前缀 | 格式: %Y%m%d           | report.docx → 20231025_report.docx |

## 🛠️ 安装与使用 / Installation & Usage

### 环境要求 / Requirements

- Python 3.8+
- Tkinter 库 (通常包含在标准Python安装中)

### 快速启动 / Quick Start

```bash
bash复制代码# 克隆仓库
git clone https://github.com/yourusername/file-renamer.git

# 进入目录
cd file-renamer

# 运行程序
python main.py
```

### 使用指南 / Step-by-Step Guide

1. 添加文件
   - 点击"添加文件"选择单个文件
   - 点击"添加目录"导入整个文件夹
2. 选择规则
   - 从下拉列表选择需要的重命名规则
   - 根据规则类型输入相应参数
3. 预览结果
   - 点击"预览"按钮查看重命名效果
   - 在文件列表中检查新旧文件名对比
4. 执行操作
   - 确认无误后点击"执行重命名"
   - 使用"撤销"按钮可回退最后一次操作

## ⚠️ 注意事项 / Important Notes

1. 备份机制：所有操作自动创建时间戳备份文件夹（格式：`rename_backup_%Y%m%d%H%M%S`）
2. 正则表达式：请使用Python标准正则语法，替换操作将应用于完整文件名
3. 序号生成：格式字符串需包含`{n}`占位符，如`{n:03d}`生成三位数字
4. 路径限制：建议避免使用包含特殊字符的文件路径

## 📜 开发计划 / Roadmap

-  增加文件过滤功能
-  支持自定义规则组合
-  添加历史记录查看功能
-  国际化支持（多语言界面）

## 🤝 贡献指南 / Contributing

欢迎通过Issue提交问题或建议，Pull Request请遵循以下规范：

1. 保持代码风格统一（PEP8）
2. 新功能需包含对应测试用例
3. 更新相关文档说明

------

# Universal File Renamer (English Version)

## 🌟 Key Features

- **Multiple Renaming Rules**: Prefix/Suffix, Text Replacement, Regex, Sequence Generation, Date Prefix
- **Safety First**: Automatic backup creation with full undo capability
- **Smart Preview**: Real-time renaming simulation before execution
- **Batch Processing**: Handle thousands of files in single operation
- **Cross-Platform**: Works seamlessly on Windows/macOS/Linux

## 🔧 Technical Details

- **Backup System**: Creates timestamped backup directory (format: `rename_backup_%Y%m%d%H%M%S`)
- **Undo Implementation**: Uses operation stack to track file movements
- **Regex Engine**: Built-in Python `re` module support
- **Thread Safety**: Main thread keeps responsive during file operations

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](https://cloud.siliconflow.cn/playground/LICENSE) file for details.
