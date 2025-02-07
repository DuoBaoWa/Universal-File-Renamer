import os
import re
import shutil
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime
from pathlib import Path
import fnmatch  # 导入fnmatch模块，用于文件名匹配

class FileRenamerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("通用文件重命名工具 v1.0")
        self.root.geometry("800x600")
        
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

    def create_widgets(self):
        # 文件列表
        self.tree = ttk.Treeview(self.root, columns=("original", "new"), show="headings")
        self.tree.heading("original", text="原始文件名")
        self.tree.heading("new", text="新文件名")
        self.tree.column("original", width=300)
        self.tree.column("new", width=300)
        
        # 工具栏
        self.toolbar = ttk.Frame(self.root)
        self.btn_add = ttk.Button(self.toolbar, text="添加文件", command=self.add_files)
        self.btn_add_dir = ttk.Button(self.toolbar, text="添加目录", command=self.add_directory)
        self.btn_clear = ttk.Button(self.toolbar, text="清空列表", command=self.clear_list)
        
        # 规则配置
        self.rule_frame = ttk.LabelFrame(self.root, text="重命名规则")
        self.rule_type = ttk.Combobox(self.rule_frame, values=[  # 下拉框
            "添加前缀", 
            "添加后缀",
            "替换文本",
            "正则替换",
            "序号生成",
            "日期前缀"
        ])
        self.rule_type.bind("<<ComboboxSelected>>", self.update_rule_ui)  # 绑定选择事件
        self.rule_params_frame = ttk.Frame(self.rule_frame)
        
        # 操作按钮
        self.btn_preview = ttk.Button(self.root, text="预览", command=self.preview)
        self.btn_rename = ttk.Button(self.root, text="执行重命名", command=self.execute_rename)
        self.btn_undo = ttk.Button(self.root, text="撤销", command=self.undo)
        
        # 状态栏
        self.status = ttk.Label(self.root, text="就绪", anchor=tk.W)

        # 新增过滤组件
        self.filter_frame = ttk.Frame(self.toolbar)
        self.lbl_filter = ttk.Label(self.filter_frame, text="文件过滤:")
        self.ent_filter = ttk.Entry(self.filter_frame, width=25)
        self.ent_filter.insert(0, "*.*")  # 默认不过滤
        self.btn_filter = ttk.Button(self.filter_frame, text="应用", command=self.update_filter)

    def setup_layout(self):
        # 调整工具栏布局
        self.toolbar.pack(fill=tk.X, padx=5, pady=5)
        self.btn_add.pack(side=tk.LEFT, padx=2)
        self.btn_add_dir.pack(side=tk.LEFT, padx=2)
        self.btn_clear.pack(side=tk.LEFT, padx=2)

        # 添加过滤组件到工具栏
        self.filter_frame.pack(side=tk.RIGHT, padx=5)
        self.lbl_filter.pack(side=tk.LEFT)
        self.ent_filter.pack(side=tk.LEFT, padx=2)
        self.btn_filter.pack(side=tk.LEFT)

        # 布局管理
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.rule_frame.pack(fill=tk.X, padx=5, pady=5)
        self.rule_type.pack(fill=tk.X, padx=5, pady=2)
        self.rule_params_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Separator(self.root).pack(fill=tk.X, padx=5, pady=5)
        
        self.btn_preview.pack(side=tk.LEFT, padx=5, pady=5)
        self.btn_rename.pack(side=tk.LEFT, padx=5, pady=5)
        self.btn_undo.pack(side=tk.RIGHT, padx=5, pady=5)
        
        self.status.pack(side=tk.BOTTOM, fill=tk.X)

    def update_filter(self):
        """更新文件过滤模式"""
        patterns = self.ent_filter.get().split(";")
        self.filter_patterns = [p.strip() for p in patterns if p.strip()]
        messagebox.showinfo("过滤更新", f"已设置过滤模式: {self.filter_patterns}")
        self.clear_list()  # 清空当前列表以应用新过滤

    def is_file_match(self, filename):
        """检查文件是否符合过滤条件"""
        if not self.filter_patterns:
            return True
        return any(fnmatch.fnmatch(filename, pattern) for pattern in self.filter_patterns)

    def add_files(self):
        files = filedialog.askopenfilenames()
        if files:
            # 添加过滤逻辑
            filtered = [f for f in files if self.is_file_match(os.path.basename(f))]
            self.files.extend(filtered)
            self.update_file_list()

    def add_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if self.is_file_match(file):
                        self.files.append(os.path.join(root, file))
            self.update_file_list()

    def update_rule_ui(self, event=None):
        """更新规则配置界面"""
        # 清空参数区域
        for widget in self.rule_params_frame.winfo_children():
            widget.destroy()
        
        rule = self.rule_type.get()
        if rule == "添加前缀":
            ttk.Label(self.rule_params_frame, text="前缀:").pack(side=tk.LEFT)
            self.rule_params["prefix"] = ttk.Entry(self.rule_params_frame)
            self.rule_params["prefix"].pack(side=tk.LEFT)
            
        elif rule == "添加后缀":
            ttk.Label(self.rule_params_frame, text="后缀:").pack(side=tk.LEFT)
            self.rule_params["suffix"] = ttk.Entry(self.rule_params_frame)
            self.rule_params["suffix"].pack(side=tk.LEFT)
            
        elif rule == "替换文本":
            ttk.Label(self.rule_params_frame, text="查找:").pack(side=tk.LEFT)
            self.rule_params["search"] = ttk.Entry(self.rule_params_frame)
            self.rule_params["search"].pack(side=tk.LEFT)
            ttk.Label(self.rule_params_frame, text="替换为:").pack(side=tk.LEFT)
            self.rule_params["replace"] = ttk.Entry(self.rule_params_frame)
            self.rule_params["replace"].pack(side=tk.LEFT)
            
        elif rule == "正则替换":
            ttk.Label(self.rule_params_frame, text="正则表达式:").pack(side=tk.LEFT)
            self.rule_params["pattern"] = ttk.Entry(self.rule_params_frame)
            self.rule_params["pattern"].pack(side=tk.LEFT)
            ttk.Label(self.rule_params_frame, text="替换为:").pack(side=tk.LEFT)
            self.rule_params["repl"] = ttk.Entry(self.rule_params_frame)
            self.rule_params["repl"].pack(side=tk.LEFT)
            
        elif rule == "序号生成":
            ttk.Label(self.rule_params_frame, text="格式:").pack(side=tk.LEFT)
            self.rule_params["format"] = ttk.Entry(self.rule_params_frame)
            self.rule_params["format"].insert(0, "{n:03d}")
            self.rule_params["format"].pack(side=tk.LEFT)
            
        elif rule == "日期前缀":
            ttk.Label(self.rule_params_frame, text="日期格式:").pack(side=tk.LEFT)
            self.rule_params["date_format"] = ttk.Entry(self.rule_params_frame)
            self.rule_params["date_format"].insert(0, "%Y-%m-%d")
            self.rule_params["date_format"].pack(side=tk.LEFT)

    def clear_list(self):
        self.files.clear()
        self.tree.delete(*self.tree.get_children())
        
    def update_file_list(self):
        self.tree.delete(*self.tree.get_children())
        for file in self.files:
            self.tree.insert("", "end", values=(os.path.basename(file), ""))

    def generate_new_name(self, original):
        rule = self.rule_type.get()
        base, ext = os.path.splitext(original)
        
        if rule == "添加前缀":
            prefix = self.rule_params["prefix"].get()
            return f"{prefix}{original}"
            
        elif rule == "添加后缀":
            suffix = self.rule_params["suffix"].get()
            return f"{base}{suffix}{ext}"
            
        elif rule == "替换文本":
            search = self.rule_params["search"].get()
            replace = self.rule_params["replace"].get()
            return original.replace(search, replace)
            
        elif rule == "正则替换":
            pattern = self.rule_params["pattern"].get()
            repl = self.rule_params["repl"].get()
            return re.sub(pattern, repl, original)
            
        elif rule == "序号生成":
            format_str = self.rule_params["format"].get()
            return format_str.format(n=self.files.index(original) + 1)
            
        elif rule == "日期前缀":
            date_format = self.rule_params["date_format"].get()
            current_date = datetime.now().strftime(date_format)
            return f"{current_date}_{original}"

        return original

    def preview(self):
        self.tree.delete(*self.tree.get_children())
        for file in self.files:
            new_name = self.generate_new_name(os.path.basename(file))
            self.tree.insert("", "end", values=(os.path.basename(file), new_name))

    def execute_rename(self):
        if not self.files:
            messagebox.showwarning("警告", "没有文件可重命名")
            return

        self.backup_dir = os.path.join(os.getcwd(), "backup", datetime.now().strftime("%Y%m%d%H%M%S"))
        os.makedirs(self.backup_dir, exist_ok=True)

        operations = []
        for file in self.files:
            new_name = self.generate_new_name(os.path.basename(file))
            if new_name != os.path.basename(file):
                backup_file = shutil.copy(file, self.backup_dir)
                os.rename(file, os.path.join(os.path.dirname(file), new_name))
                operations.append((file, new_name))

        # 保存操作记录
        self.undo_stack.append({
            "operations": operations,
            "backup_dir": self.backup_dir
        })
        
        self.status.config(text="重命名完成")
        messagebox.showinfo("成功", "文件重命名完成")

    def undo(self):
        if not self.undo_stack:
            messagebox.showinfo("信息", "没有可撤销的操作")
            return

        last_op = self.undo_stack.pop()
        try:
            # 恢复文件
            for orig, new in reversed(last_op["operations"]):
                Path(new).rename(orig)

            # 删除备份
            shutil.rmtree(last_op["backup_dir"])

            # 更新文件列表
            self.files = [orig for orig, _ in last_op["operations"]]
            self.update_file_list()

            messagebox.showinfo("成功", "已撤销最后一次操作")
            self.status.config(text="撤销完成")

        except Exception as e:
            messagebox.showerror("错误", f"撤销失败: {str(e)}")
            self.status.config(text="撤销失败")

if __name__ == "__main__":
    root = tk.Tk()
    app = FileRenamerApp(root)
    root.mainloop()
