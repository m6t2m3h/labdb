import tkinter as tk
from tkinter import ttk

class ResultTable:
    def __init__(self, parent, column_dic):
        self.root = parent
        self.column_dic = column_dic

        db_columns = [db_name for _, db_name in self.column_dic.items()]
        self.tree = ttk.Treeview(parent, columns=db_columns, show="headings", selectmode="browse")

        self.x_scrollbar = ttk.Scrollbar(parent, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.y_scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.tree.yview)

        self.tree.configure(xscrollcommand=self.x_scrollbar.set) 
        self.tree.configure(yscrollcommand=self.y_scrollbar.set) 

    def set_headings(self):
        self.tree.heading('#0',text='')
        self.tree.column('#0',width=0, stretch='no')
        for jp_name, db_name in self.column_dic.items():
            self.tree.heading(f"{db_name}", text=f"{jp_name}", anchor='w')
            self.tree.column(f"{db_name}", anchor='e', width=150, minwidth=80)

    def set_rows(self, rows, id=None):

        for row in rows:
            # 値がNoneの場合はハイフンに置換
            result = tuple(
                "-" if row.get(db_name) is None else row.get(db_name)
                for db_name in self.column_dic.values()
            )
            if id is not None:
                self.tree.insert(parent="", index="end", iid=row[id], values=result)
            else:
                self.tree.insert(parent="", index="end", values=result)

    def pack(self):
        self.x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH)

    def bind_double_click(self, callback):
        self.tree.bind("<Double-1>", callback)

class DetailTable:
    def __init__(self, parent, column_dic):
        
        self.column_dic = column_dic
        # Treeviewの生成
        column = ["name_1", "value_1", "name_2", "value_2"]
        self.tree = ttk.Treeview(parent, columns=column, selectmode="none", show="headings")
        # スクロールバーの追加
        self.x_scrollbar = ttk.Scrollbar(parent, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.y_scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(xscrollcommand=self.x_scrollbar.set) 
        self.tree.configure(yscrollcommand=self.y_scrollbar.set)
    
    def set_headings(self):
        # 列の設定
        self.tree.heading('#0',text='')
        self.tree.column('#0',width=0, stretch='no')
        self.tree.heading("name_1", text="項目名", anchor='center')
        self.tree.column("name_1", anchor='w',  width=120, minwidth=100)
        self.tree.heading("value_1", text="値", anchor='center')
        self.tree.column("value_1", anchor='e',  width=80, minwidth=50)
        self.tree.heading("name_2", text="項目名", anchor='center')
        self.tree.column("name_2", anchor='w',  width=120, minwidth=100)
        self.tree.heading("value_2", text="値", anchor='center')
        self.tree.column("value_2", anchor='e',  width=80, minwidth=50)

    def set_rows(self, values):
        # 表を切り替える位置
        table_num = 2
        row_num = len(self.column_dic) // table_num
        row_num += len(self.column_dic) % table_num

        n = 0
        jp_name_list = list(self.column_dic.keys())
        db_name_list = list(self.column_dic.values())

        # 値がNoneの場合はハイフンに置換
        while n < row_num:
            left_name = jp_name_list[n]
            left_value = "-" if values.get(db_name_list[n]) is None else values.get(db_name_list[n])
            right_index = row_num + n
            if right_index < len(jp_name_list):
                right_name = jp_name_list[right_index]
                right_value = "-" if values.get(db_name_list[right_index]) is None else values.get(db_name_list[right_index])
            else:
                right_name = ""
                right_value = ""

            val = (left_name, left_value, right_name, right_value)                            
            self.tree.insert(parent='', index='end', values=val)
            n += 1
    
    def pack(self):
        self.x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def bind_click(self, callback):
        self.tree.bind("<Button-1>", callback)

    def cell_entry(self, parent, callback):
        self.entry = tk.Entry(parent, command=callback)


class FileListbox:
    def __init__(self, parent):
        self.files = ()
        self.root = parent
        self.listbox = tk.Listbox(parent, height=40, width=40)
        self.listbox.configure(state="normal")
    
    def set_buttons(self, reference_callback, exe_callback):
        self.reference_button=tk.Button(self.root, text="参照", command=reference_callback, width=4)
        self.execute_button=tk.Button(self.root, text="実行", command=exe_callback, width=4, bg="salmon")

    def pack(self):
        self.listbox.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        self.reference_button.pack(side=tk.LEFT, expand=False)
        self.execute_button.pack(side=tk.LEFT, expand=False)

    def set_files(self, files):
        self.files = files
        self.listbox.delete(0, tk.END)
        for filename in files:
            self.listbox.insert(tk.END, filename)

    def disable_buttons(self):
        self.reference_button.config(state=tk.DISABLED)
        self.execute_button.config(state=tk.DISABLED)
    
    def enable_buttons(self):
        self.reference_button.config(state=tk.NORMAL)
        self.execute_button.config(state=tk.NORMAL)

    def get_files(self):
        return self.files
    
class AnalysisProgressbar:
    
    def __init__(self, parent, max):
        self.progress = ttk.Progressbar(
            parent,
            maximum=max,
            orient="horizontal",
            length=200,
            mode="determinate",
            value=0
        )
        
    def pack(self):
        self.progress.pack(fill=tk.X)

    def set_value(self, value):
        self.progress["value"] = value
    
    def destroy(self):
        self.progress.destroy()

class WindowUtils:

    @staticmethod
    def center_geometry(parent, width, height):
        screen_width = parent.winfo_screenwidth()
        screen_height = parent.winfo_screenheight()

        x = (screen_width - width) // 2
        y = (screen_height - height) // 2

        return f"{width}x{height}+{x}+{y}"
