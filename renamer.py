import os
import re
import shutil
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime
from pathlib import Path

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
        self.rule_type = ttk.Combobox(self.rule_frame, values=[
            "添加前缀", 
            "添加后缀",
            "替换文本",
            "正则替换",
            "序号生成",
            "日期前缀"
        ])
        self.rule_type.bind("<<ComboboxSelected>>", self.update_rule_ui)
        self.rule_params_frame = ttk.Frame(self.rule_frame)
        
        # 操作按钮
        self.btn_preview = ttk.Button(self.root, text="预览", command=self.preview)
        self.btn_rename = ttk.Button(self.root, text="执行重命名", command=self.execute_rename)
        self.btn_undo = ttk.Button(self.root, text="撤销", command=self.undo)
        
        # 状态栏
        self.status = ttk.Label(self.root, text="就绪", anchor=tk.W)

    def setup_layout(self):
        # 布局管理
        self.toolbar.pack(fill=tk.X, padx=5, pady=5)
        self.btn_add.pack(side=tk.LEFT, padx=2)
        self.btn_add_dir.pack(side=tk.LEFT, padx=2)
        self.btn_clear.pack(side=tk.LEFT, padx=2)
        
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.rule_frame.pack(fill=tk.X, padx=5, pady=5)
        self.rule_type.pack(fill=tk.X, padx=5, pady=2)
        self.rule_params_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Separator(self.root).pack(fill=tk.X, padx=5, pady=5)
        
        self.btn_preview.pack(side=tk.LEFT, padx=5, pady=5)
        self.btn_rename.pack(side=tk.LEFT, padx=5, pady=5)
        self.btn_undo.pack(side=tk.RIGHT, padx=5, pady=5)
        
        self.status.pack(side=tk.BOTTOM, fill=tk.X)

    def update_rule_ui(self, event=None):
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

    def add_files(self):
        files = filedialog.askopenfilenames()
        if files:
            self.files.extend(files)
            self.update_file_list()
            
    def add_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    self.files.append(os.path.join(root, file))
            self.update_file_list()

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
            return f"{format_str.format(n=1)}{ext}"  # 实际序号在批量处理时生成
            
        elif rule == "日期前缀":
            date_format = self.rule_params["date_format"].get()
            date_str = datetime.now().strftime(date_format)
            return f"{date_str}_{original}"
            
        return original

    def preview(self):
        if not self.files:
            messagebox.showwarning("警告", "请先添加文件")
            return
            
        try:
            for item in self.tree.get_children():
                self.tree.delete(item)
                
            counter = 1
            for idx, file in enumerate(self.files):
                original = os.path.basename(file)
                new_name = self.generate_new_name(original)
                
                # 处理序号生成
                if self.rule_type.get() == "序号生成":
                    format_str = self.rule_params["format"].get()
                    base, ext = os.path.splitext(new_name)
                    new_name = f"{format_str.format(n=counter)}{ext}"
                    counter += 1
                
                self.tree.insert("", "end", values=(original, new_name))
                
            self.status.config(text="预览生成完成")
        except Exception as e:
            messagebox.showerror("错误", f"生成预览失败: {str(e)}")

    def execute_rename(self):
        if not messagebox.askyesno("确认", "确定要执行重命名操作吗？"):
            return
            
        try:
            # 创建备份
            backup_dir = f"rename_backup_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            os.makedirs(backup_dir, exist_ok=True)
            
            operations = []
            counter = 1
            
            for idx, file in enumerate(self.files):
                original_path = Path(file)
                new_name = self.tree.item(self.tree.get_children()[idx])["values"][1]
                new_path = original_path.parent / new_name
                
                # 备份原始文件
                shutil.copy2(file, os.path.join(backup_dir, original_path.name))
                
                # 执行重命名
                original_path.rename(new_path)
                operations.append((str(original_path), str(new_path)))
                
            # 记录操作日志
            self.undo_stack.append({
                "backup_dir": backup_dir,
                "operations": operations
            })
            
            # 更新文件列表
            self.files = [str(new) for _, new in operations]
            self.update_file_list()
            
            messagebox.showinfo("成功", f"已完成{len(operations)}个文件的重命名")
            self.status.config(text="操作完成")
            
        except Exception as e:
            messagebox.showerror("错误", f"重命名失败: {str(e)}")
            self.status.config(text="操作失败")

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