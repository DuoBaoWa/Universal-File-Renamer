import os
import re
import shutil
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from functools import partial

@dataclass
class RenameOperation:
    original_path: str
    new_path: str
    backup_path: str

class FileRenamer:
    """文件重命名核心逻辑类"""
    
    def __init__(self):
        self.operations: List[RenameOperation] = []
        
    def generate_new_name(self, original: str, rule: dict) -> str:
        rule_type = rule.get('type')
        params = rule.get('params', {})
        
        if not rule_type:
            return original
            
        base, ext = os.path.splitext(original)
        
        rule_handlers = {
            "添加前缀": lambda: f"{params['prefix']}{original}",
            "添加后缀": lambda: f"{base}{params['suffix']}{ext}",
            "替换文本": lambda: original.replace(params['search'], params['replace']),
            "正则替换": lambda: re.sub(params['pattern'], params['repl'], original),
            "序号生成": lambda: f"{params['format'].format(n=params.get('counter', 1))}{ext}",
            "日期前缀": lambda: f"{datetime.now().strftime(params['date_format'])}_{original}"
        }
        
        return rule_handlers.get(rule_type, lambda: original)()

    def execute_rename(self, operations: List[RenameOperation]) -> bool:
        try:
            for op in operations:
                shutil.copy2(op.original_path, op.backup_path)
                Path(op.original_path).rename(op.new_path)
            return True
        except Exception as e:
            raise RuntimeError(f"重命名操作失败: {str(e)}")

    def undo_rename(self, operations: List[RenameOperation]) -> bool:
        try:
            for op in reversed(operations):
                Path(op.new_path).rename(op.original_path)
            return True
        except Exception as e:
            raise RuntimeError(f"撤销操作失败: {str(e)}")

class FileRenamerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("通用文件重命名工具 v2.0")
        self.root.geometry("800x600")
        
        # 核心组件初始化
        self.renamer = FileRenamer()
        self.files: List[str] = []
        self.undo_stack: List[List[RenameOperation]] = []
        
        # GUI组件初始化
        self._init_gui()
        self._setup_layout()
        
    def _init_gui(self):
        # 使用ttk风格
        style = ttk.Style()
        style.theme_use('clam')
        
        self._create_toolbar()
        self._create_file_list()
        self._create_rule_frame()
        self._create_action_buttons()
        self._create_status_bar()
        
    def _create_toolbar(self):
        self.toolbar = ttk.Frame(self.root)
        buttons = [
            ("添加文件", self.add_files),
            ("添加目录", self.add_directory),
            ("清空列表", self.clear_list)
        ]
        
        for text, command in buttons:
            ttk.Button(self.toolbar, text=text, command=command).pack(side=tk.LEFT, padx=2)
            
        # 文件过滤
        ttk.Label(self.toolbar, text="文件过滤:").pack(side=tk.LEFT, padx=5)
        self.filter_var = tk.StringVar()
        self.filter_var.trace_add("write", lambda *args: self._update_file_list())
        ttk.Entry(self.toolbar, textvariable=self.filter_var).pack(side=tk.LEFT, padx=2)
        
    def _create_file_list(self):
        columns = ("original", "new")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings")
        
        for col, text in zip(columns, ["原始文件名", "新文件名"]):
            self.tree.heading(col, text=text)
            self.tree.column(col, width=300)
            
        # 添加滚动条
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
    def _create_rule_frame(self):
        self.rule_frame = ttk.LabelFrame(self.root, text="重命名规则")
        rules = ["添加前缀", "添加后缀", "替换文本", "正则替换", "序号生成", "日期前缀"]
        
        self.rule_type = ttk.Combobox(self.rule_frame, values=rules)
        self.rule_type.bind("<<ComboboxSelected>>", self._update_rule_ui)
        
        self.rule_params_frame = ttk.Frame(self.rule_frame)
        self.rule_params: Dict[str, tk.Widget] = {}
        
    def _create_action_buttons(self):
        buttons_frame = ttk.Frame(self.root)
        buttons = [
            ("预览", self.preview),
            ("执行重命名", self.execute_rename),
            ("撤销", self.undo)
        ]
        
        for text, command in buttons:
            ttk.Button(buttons_frame, text=text, command=command).pack(side=tk.LEFT, padx=5)
            
    def _create_status_bar(self):
        self.status = ttk.Label(self.root, text="就绪", anchor=tk.W)
        
    def _setup_layout(self):
        # 使用grid布局管理器
        self.toolbar.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        self.tree.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        self.rule_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        self.status.grid(row=3, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        
        # 配置grid权重
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
    def _get_rule_params(self) -> dict:
        rule_type = self.rule_type.get()
        params = {}
        
        for key, widget in self.rule_params.items():
            if isinstance(widget, ttk.Entry):
                params[key] = widget.get()
                
        return {"type": rule_type, "params": params}
        
    def _update_file_list(self):
        self.tree.delete(*self.tree.get_children())
        filter_text = self.filter_var.get().strip().lower()
        
        for file in self.files:
            basename = os.path.basename(file)
            if filter_text and filter_text not in basename.lower():
                continue
            self.tree.insert("", "end", values=(basename, ""))
            
    @staticmethod
    def _create_backup_dir() -> str:
        backup_dir = f"rename_backup_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        os.makedirs(backup_dir, exist_ok=True)
        return backup_dir
        
    def add_files(self):
        files = filedialog.askopenfilenames()
        if files:
            self.files.extend(files)
            self._update_file_list()
            
    def add_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            for root_dir, _, files in os.walk(directory):
                self.files.extend(os.path.join(root_dir, f) for f in files)
            self._update_file_list()
            
    def clear_list(self):
        self.files.clear()
        self.tree.delete(*self.tree.get_children())
        
    def preview(self):
        if not self.files:
            messagebox.showwarning("警告", "请先添加文件")
            return
            
        try:
            rule = self._get_rule_params()
            counter = 1
            
            for item in self.tree.get_children():
                original = self.tree.item(item)["values"][0]
                
                if rule["type"] == "序号生成":
                    rule["params"]["counter"] = counter
                    counter += 1
                    
                new_name = self.renamer.generate_new_name(original, rule)
                self.tree.item(item, values=(original, new_name))
                
            self.status.config(text="预览生成完成")
            
        except Exception as e:
            messagebox.showerror("错误", f"生成预览失败: {str(e)}")
            
    def execute_rename(self):
        if not messagebox.askyesno("确认", "确定要执行重命名操作吗？"):
            return
            
        try:
            backup_dir = self._create_backup_dir()
            operations = []
            
            for item in self.tree.get_children():
                values = self.tree.item(item)["values"]
                original_name, new_name = values
                
                original_path = next(f for f in self.files if os.path.basename(f) == original_name)
                new_path = str(Path(original_path).parent / new_name)
                backup_path = os.path.join(backup_dir, original_name)
                
                operations.append(RenameOperation(original_path, new_path, backup_path))
                
            if self.renamer.execute_rename(operations):
                self.undo_stack.append(operations)
                self._update_file_list()
                messagebox.showinfo("成功", f"已完成{len(operations)}个文件的重命名")
                
        except Exception as e:
            messagebox.showerror("错误", str(e))
            
    def undo(self):
        if not self.undo_stack:
            messagebox.showinfo("信息", "没有可撤销的操作")
            return
            
        try:
            operations = self.undo_stack.pop()
            if self.renamer.undo_rename(operations):
                self._update_file_list()
                messagebox.showinfo("成功", "已撤销最后一次操作")
                
        except Exception as e:
            messagebox.showerror("错误", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = FileRenamerGUI(root)
    root.mainloop()
