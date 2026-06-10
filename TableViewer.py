import tkinter as tk
from tkinter import ttk

from DatabaseDefinition import DatabaseDefinition

# ttkとは
# https://docs.python.org/ja/3.13/library/tkinter.ttk.html

class TableViewer(DatabaseDefinition):

    def __init__(self, data_list):
        self.data_list = data_list
    
    def open_window(self):
        # メインウィンドウ生成
        root = tk.Tk()
        root.title("データ一覧")
        root.geometry("1000x400")
        frame = tk.Frame(root)

        # Treeviewの生成
        column = [db_name for _, db_name in self.ITEM_NAME.items()]
        tree = ttk.Treeview(frame, columns=column, selectmode="browse", show="headings")
        tree.bind("<Double-1>", self.on_double_click)

        # スクロールバーの追加
        x_scrollbar = ttk.Scrollbar(frame, orient=tk.HORIZONTAL, command=tree.xview)
        y_scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(xscrollcommand=x_scrollbar.set) 
        tree.configure(yscrollcommand=y_scrollbar.set) 

        # 列の設定
        tree.heading('#0',text='')
        tree.column('#0',width=0, stretch='no')

        for jp_name, db_name in self.ITEM_NAME.items():
            tree.heading(f"{db_name}", text=f"{jp_name}", anchor='w')
            tree.column(f"{db_name}", anchor='e', width=80)
  
        # レコードの追加
        for row in self.data_list:
            # データのNoneはハイフンに置換
            result = tuple("-" if x is None else x for x in row)
            tree.insert(parent='', index='end', values=result[1:])
 
        # ウィジェットの配置
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        frame.pack(fill=tk.BOTH, expand=True)

        root.mainloop()

    def on_double_click(self, event):
        tree = event.widget
        selected_items = tree.selection()
        item_id = selected_items[0]
        values = tree.item(item_id, "values")
        self.open_detail(item_id, values)

    def open_detail(self, id, values):
        # サブウィンドウ生成
        sub = tk.Toplevel()
        sub.title(id)
        sub.geometry("400x950")
        # 表を切り替える位置
        table_num = 2
        row_num = len(self.ITEM_NAME) // table_num
        row_num += len(self.ITEM_NAME) % table_num
        # Treeviewの生成
        column = ["name_1", "value_1", "name_2", "value_2"]
        tree = ttk.Treeview(sub, columns=column, selectmode="none", show="headings")
        # 列の設定
        tree.heading('#0',text='')
        tree.column('#0',width=0, stretch='no')
        tree.heading("name_1", text="項目名", anchor='center')
        tree.column("name_1", anchor='w', width=80)
        tree.heading("value_1", text="結果", anchor='center')
        tree.column("value_1", anchor='e', width=80)
        tree.heading("name_2", text="項目名", anchor='center')
        tree.column("name_2", anchor='w', width=80)
        tree.heading("value_2", text="結果", anchor='center')
        tree.column("value_2", anchor='e', width=80)
        # レコードの追加
        n = 0
        key_list = list(self.ITEM_NAME.keys())
        while n < row_num:
            left_name = key_list[n]
            left_value = values[n]
            right_index = row_num + n
            if right_index < len(key_list):
                right_name = key_list[right_index]
                right_value = values[right_index] 
            else:
                right_name = ""
                right_value = ""

            val = (left_name, left_value, right_name, right_value)                            
            tree.insert(parent='', index='end', values=val)
            n += 1

        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
