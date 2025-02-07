import os
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime


class FileRenamerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("通用文件重命名工具 v1.0")
        self.root.geometry("800x600")
        self.root.iconbitmap("icon.ico")  # 可以根据需要设置自己的图标

        # 初始化核心组件
        self.files = []
        self.backup_dir = None
        self.undo_stack = []

        # 创建界面
        self.create_widgets()
        self.setup_layout()

        # 初始化规则
        self.current_rule = None
        self.rule_params = {}

        # 新增过滤模式变量
        self.filter_patterns = []

        # 添加猫猫动画部分
        self.cat_canvas = None

    def create_widgets(self):
        # 工具栏
        self.toolbar = ttk.Frame(self.root, padding=5)
        self.toolbar.grid(row=0, column=0, sticky="ew")

        # 添加文件按钮
        self.btn_add_files = ttk.Button(self.toolbar, text="添加文件", command=self.add_files)
        self.btn_add_files.grid(row=0, column=0, padx=10)

        # 清空文件按钮
        self.btn_clear = ttk.Button(self.toolbar, text="清空列表", command=self.clear_list)
        self.btn_clear.grid(row=0, column=1, padx=10)

        # 重命名规则选择
        self.rule_label = ttk.Label(self.toolbar, text="选择规则:")
        self.rule_label.grid(row=0, column=2, padx=10)

        self.rule_type = ttk.Combobox(self.toolbar,
                                      values=["添加前缀", "添加后缀", "替换文本", "正则替换", "序号生成", "日期前缀"])
        self.rule_type.grid(row=0, column=3, padx=10)
        self.rule_type.bind("<<ComboboxSelected>>", self.update_rule_ui)  # 绑定选择事件

        # 创建预览和执行按钮
        self.btn_preview = ttk.Button(self.root, text="预览", command=self.preview, style="TButton")
        self.btn_preview.grid(row=1, column=0, padx=10, pady=10)

        self.btn_rename = ttk.Button(self.root, text="执行重命名", command=self.execute_rename, style="TButton")
        self.btn_rename.grid(row=1, column=1, padx=10, pady=10)

        self.btn_undo = ttk.Button(self.root, text="撤销", command=self.undo, style="TButton")
        self.btn_undo.grid(row=1, column=2, padx=10, pady=10)

        # 文件列表显示
        self.file_listbox = tk.Listbox(self.root, height=15, width=60)
        self.file_listbox.grid(row=2, column=0, columnspan=4, padx=10, pady=10)

        # 保存规则的参数输入框
        self.param_frame = ttk.Frame(self.root)
        self.param_frame.grid(row=3, column=0, columnspan=4, padx=10, pady=10)

    def setup_layout(self):
        """设置窗口布局"""
        pass  # 可根据需要修改布局

    def add_files(self):
        """添加文件到列表"""
        file_paths = ["file1.txt", "file2.txt", "file3.txt"]  # 假设这里是文件选择的结果
        self.files.extend(file_paths)
        self.update_file_list()

    def update_file_list(self):
        """更新文件列表显示"""
        self.file_listbox.delete(0, tk.END)
        for file in self.files:
            self.file_listbox.insert(tk.END, file)

    def clear_list(self):
        """清空文件列表"""
        self.files = []
        self.update_file_list()

    def update_rule_ui(self, event):
        """更新规则的输入界面"""
        rule = self.rule_type.get()
        for widget in self.param_frame.winfo_children():
            widget.grid_forget()

        if rule == "添加前缀":
            self.current_rule = "添加前缀"
            ttk.Label(self.param_frame, text="前缀:").grid(row=0, column=0, padx=5)
            self.rule_params["prefix"] = ttk.Entry(self.param_frame)
            self.rule_params["prefix"].grid(row=0, column=1, padx=5)
        elif rule == "添加后缀":
            self.current_rule = "添加后缀"
            ttk.Label(self.param_frame, text="后缀:").grid(row=0, column=0, padx=5)
            self.rule_params["suffix"] = ttk.Entry(self.param_frame)
            self.rule_params["suffix"].grid(row=0, column=1, padx=5)
        elif rule == "替换文本":
            self.current_rule = "替换文本"
            ttk.Label(self.param_frame, text="替换:").grid(row=0, column=0, padx=5)
            self.rule_params["search"] = ttk.Entry(self.param_frame)
            self.rule_params["search"].grid(row=0, column=1, padx=5)
            ttk.Label(self.param_frame, text="为:").grid(row=0, column=2, padx=5)
            self.rule_params["replace"] = ttk.Entry(self.param_frame)
            self.rule_params["replace"].grid(row=0, column=3, padx=5)
        elif rule == "正则替换":
            self.current_rule = "正则替换"
            ttk.Label(self.param_frame, text="正则表达式:").grid(row=0, column=0, padx=5)
            self.rule_params["pattern"] = ttk.Entry(self.param_frame)
            self.rule_params["pattern"].grid(row=0, column=1, padx=5)
            ttk.Label(self.param_frame, text="替换:").grid(row=0, column=2, padx=5)
            self.rule_params["repl"] = ttk.Entry(self.param_frame)
            self.rule_params["repl"].grid(row=0, column=3, padx=5)
        elif rule == "序号生成":
            self.current_rule = "序号生成"
            pass  # 序号生成的界面可以稍后添加
        elif rule == "日期前缀":
            self.current_rule = "日期前缀"
            ttk.Label(self.param_frame, text="日期格式:").grid(row=0, column=0, padx=5)
            self.rule_params["date_format"] = ttk.Entry(self.param_frame)
            self.rule_params["date_format"].grid(row=0, column=1, padx=5)

    def preview(self):
        """预览文件的重命名结果"""
        if not self.files:
            messagebox.showwarning("警告", "请先添加文件")
            return

        # 显示重命名预览
        preview_window = tk.Toplevel(self.root)
        preview_window.title("重命名预览")

        preview_listbox = tk.Listbox(preview_window, width=60, height=20)
        preview_listbox.pack(padx=10, pady=10)

        for old_file in self.files:
            old_name = os.path.basename(old_file)
            new_name = self.generate_new_name(old_name)
            preview_listbox.insert(tk.END, f"{old_name} -> {new_name}")

        ttk.Button(preview_window, text="关闭", command=preview_window.destroy).pack(pady=5)

    def generate_new_name(self, old_name):
        """根据规则生成新的文件名"""
        if self.current_rule == "添加前缀":
            prefix = self.rule_params["prefix"].get()
            return prefix + old_name
        elif self.current_rule == "添加后缀":
            suffix = self.rule_params["suffix"].get()
            return old_name + suffix
        elif self.current_rule == "替换文本":
            search = self.rule_params["search"].get()
            replace = self.rule_params["replace"].get()
            return old_name.replace(search, replace)
        elif self.current_rule == "正则替换":
            import re
            pattern = self.rule_params["pattern"].get()
            repl = self.rule_params["repl"].get()
            return re.sub(pattern, repl, old_name)
        elif self.current_rule == "序号生成":
            # Generate sequential number logic
            pass
        elif self.current_rule == "日期前缀":
            date_format = self.rule_params["date_format"].get()
            return datetime.now().strftime(date_format) + old_name
        return old_name

    def execute_rename(self):
        """执行重命名操作"""
        if not self.files:
            messagebox.showwarning("警告", "请先添加文件")
            return

        # 执行重命名逻辑
        for file in self.files:
            old_name = os.path.basename(file)
            new_name = self.generate_new_name(old_name)
            new_path = os.path.join(os.path.dirname(file), new_name)
            os.rename(file, new_path)

        # 更新文件列表
        self.update_file_list()

        # 执行成功时显示猫猫动画
        self.show_cat_animation()

    def show_cat_animation(self):
        """显示猫猫动画"""
        if not self.cat_canvas:
            self.cat_canvas = tk.Canvas(self.root, width=100, height=100)
            self.cat_canvas.grid(row=4, column=0, columnspan=4)

        self.cat_canvas.delete("all")

        # 画一个简笔画猫猫
        self.cat_canvas.create_oval(20, 20, 80, 80, fill="pink")
        self.cat_canvas.create_line(50, 30, 50, 50, width=2)
        self.cat_canvas.create_line(40, 40, 60, 40, width=2)

        # 简单动画
        self.cat_canvas.after(200, lambda: self.cat_canvas.delete("all"))

    def undo(self):
        """撤销操作"""
        pass


# 创建应用程序主窗口
root = tk.Tk()
app = FileRenamerApp(root)
root.mainloop()
