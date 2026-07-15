import threading
import os
import tkinter as tk
import logging

from tkinter import filedialog
from GuiComponents import WindowUtils
from GuiComponents import FileListbox
from GuiComponents import ResultTable
from GuiComponents import DetailTable
from GuiComponents import AnalysisProgressbar
from ImageAnalyzer import ImageAnalyzer
from DatabaseDefinition import DatabaseDefinition

class FileViewer:

    MAIN_WINDOW_TITLE = "血液検査管理システム"
    PROGRESS_WINDOW_TITLE = "血液検査管理システム【解析】"
    ANALYZED_WINDOW_TITLE = "解析データ確認"
    TABLE_WINDOW_TITLE = " 【検査データ一覧】"
    DETAIL_WINDOW_TITLE = "検査表ID："

    MAIN_WITH = 600
    MAIN_HEIGHT = 350
    DETAIL_WITH = 410
    DETAIL_HEIGHT = 950
    PROGRESS_WITH = 300
    PROGRESS_HEIGHT = 150
    RESULT_WITH = 1400
    RESULT_HEIGHT = 300

    def __init__(self, data_base):
        self.patient_values = data_base.select_patient()
        self.data_base = data_base
        self.logger = logging.getLogger(__name__) 

    def open_main_window(self):

        self.analyzed_data = []

        self.root = tk.Tk()
        self.root.title(self.MAIN_WINDOW_TITLE)
        self.root.geometry(WindowUtils.center_geometry(self.root, self.MAIN_WITH, self.MAIN_HEIGHT))
        self.root.protocol("WM_DELETE_WINDOW", self.close_main_window)
    
        top_frame = tk.Frame(self.root, height=150)
        bottom_frame = tk.Frame(self.root)
        top_frame.pack_propagate(False) 
        top_frame.pack(fill=tk.BOTH, expand=True)
        bottom_frame.pack(fill=tk.X)

        # 患者一覧
        patient_table = ResultTable(top_frame, DatabaseDefinition.DB_PATIENT_ITEM)
        patient_table.set_headings()    
        patient_table.set_rows(self.patient_values, "patient_id")
        patient_table.bind_double_click(self.on_patient_click)
        patient_table.pack()

        # ファイル名表示リストボックス
        self.listbox = FileListbox(bottom_frame)
        self.listbox.set_buttons(self.on_reference_button_click, self.on_execute_button_click)
        self.listbox.pack()

        self.root.mainloop()

        return self.analyzed_data

    def close_main_window(self):
        self.root.destroy()
        
    def on_patient_click(self, event):
        tree = event.widget
        selected_items = tree.selection()
        if not selected_items:
            return
        patient_id = selected_items[0]
        self.open_result_window(patient_id)

    def open_result_window(self, selected_id):
        # 選択した患者の全検査表データを取得
        self.result_values = self.data_base.select_result(patient_id=selected_id)

        # 患者名の取得
        name = next((p['patient_name'] for p in self.patient_values if p['patient_id'] == int(selected_id)), "")

        table_window = tk.Toplevel()
        table_window.title(name + self.TABLE_WINDOW_TITLE)
        table_window.geometry(WindowUtils.center_geometry(self.root, self.RESULT_WITH, self.RESULT_HEIGHT))

        result_table = ResultTable(table_window, DatabaseDefinition.DB_RESULT_ITEM)
        result_table.set_headings()    
        result_table.set_rows(self.result_values, "result_id")
        result_table.bind_double_click(self.on_result_click)
        result_table.pack()

    def on_result_click(self, event):
        tree = event.widget
        selected_items = tree.selection()
        if not selected_items:
            return
        result_id = selected_items[0]
        values = next(
            (val for val in self.result_values if val["result_id"] == int(result_id)),
            None
        )
        self.open_detail_table(result_id, values)

    def open_detail_table(self, result_id, values):

        detail_window = tk.Toplevel()
        detail_window.title(self.DETAIL_WINDOW_TITLE + result_id)
        detail_window.geometry(WindowUtils.center_geometry(detail_window, self.DETAIL_WITH, self.DETAIL_HEIGHT))
    
        detail_table = DetailTable(detail_window, DatabaseDefinition.DB_RESULT_ITEM)
        detail_table.set_headings()
        detail_table.set_rows(values)
        detail_table.pack()

    def on_reference_button_click(self):
        self.listbox.disable_buttons()
        filetype=[("Image file",".png .jpg"),("PNG",".png"),("JPEG",".jpeg")]
        files = filedialog.askopenfilenames(filetypes=filetype, initialdir="~/")
        self.listbox.set_files(files)
        self.listbox.enable_buttons()

    def on_execute_button_click(self):

        file_paths = self.listbox.get_files()
        if not file_paths:
            return
        
        self.listbox.disable_buttons()
        
        self.progress_window = tk.Toplevel()
        self.progress_window.title(self.PROGRESS_WINDOW_TITLE)
        self.progress_window.resizable(False, False)
        self.progress_window.protocol("WM_DELETE_WINDOW", lambda: None)
        self.progress_window.geometry(WindowUtils.center_geometry(self.root, self.PROGRESS_WITH, self.PROGRESS_HEIGHT))

        label = tk.Label(self.progress_window, text="画像解析中…")
        label.pack()

        self.progressbar = AnalysisProgressbar(self.progress_window, len(file_paths))
        self.progressbar.pack()

        thread = threading.Thread(target=self.analyze_worker, args=(file_paths,))
        thread.start()

    def analyze_worker(self, file_paths):

        self.analyzed_data = []
  
        for i, path_to_image in enumerate(file_paths, start=1):
            try: 
                # 画像解析
                analyzer = ImageAnalyzer(path_to_image)
                patient_data, result_data = analyzer.execute()
                self.analyzed_data.append((patient_data, result_data))
            except Exception as e:
                self.logger.exception(f"画像解析失敗：{path_to_image}:{e}")
            finally:
                self.progress_window.after(0, lambda v=i: self.progressbar.set_value(v))
        
        self.progress_window.after(300, self.analyze_finish)

    def analyze_finish(self):
        self.progressbar.destroy()
        self.progress_window.destroy()
        self.listbox.enable_buttons()

        # リストをイテレータに変換
        self.itr_analyzed_data = iter(self.analyzed_data)
        self.open_analyzed_window(next(self.itr_analyzed_data))

    def open_analyzed_window(self, analyzed_data):
        if analyzed_data is None:
            return
        patient_data, result_data = analyzed_data
        self.temp_data  = result_data
        analyzed_window = tk.Toplevel()
        analyzed_window.title(self.ANALYZED_WINDOW_TITLE)
        analyzed_window.geometry(WindowUtils.center_geometry(analyzed_window, self.DETAIL_WITH, self.DETAIL_HEIGHT))

        button_frame = tk.Frame(analyzed_window)
        button_frame.pack(fill=tk.X)
        table_frame = tk.Frame(analyzed_window)
        table_frame.pack(fill=tk.BOTH, expand=True)

        register_button = tk.Button(button_frame, text="登録", command=lambda: self.on_register_button_click(analyzed_window, patient_data))
        cancel_button=tk.Button(button_frame, text="キャンセル", command=lambda: self.close_analyzed_window(analyzed_window))

        register_button.pack(side=tk.LEFT, padx=10, pady=5)
        cancel_button.pack(side=tk.LEFT, padx=10, pady=5)

        analyzed_table = DetailTable(table_frame, DatabaseDefinition.RESULT_DATA)
        analyzed_table.set_headings()
        analyzed_table.set_rows(self.temp_data)
        analyzed_table.bind_click(lambda e, table=analyzed_table:self.on_analyzed_data_click(e, table))
        analyzed_table.pack()
    
    def close_analyzed_window(self, parent):
        parent.destroy()
        self.open_analyzed_window(next(self.itr_analyzed_data, None))

    def on_analyzed_data_click(self, event, table):

        tree = table.tree
        row = tree.identify_row(event.y)
        column = tree.identify_column(event.x)

        if not row or not column:
            return

        values = tree.item(row, "values")
        col_index = int(column[1:]) - 1
        cell_value = values[col_index]

        if col_index == 1 or col_index == 3:
            db_name = DatabaseDefinition.RESULT_DATA[values[col_index-1]]
            x, y, w, h = tree.bbox(row, column)

            entry = tk.Entry(tree)
            entry.place(x=x, y=y, width=w, height=h)
            entry.insert(0, cell_value)
            entry.focus()
            entry.bind("<Return>", lambda e, entry=entry, table=table: self.finish_edit(entry, table, row, column, db_name))
            entry.bind("<FocusOut>", lambda e, entry=entry, table=table: self.finish_edit(entry, table, row, column, db_name))

    def finish_edit(self, entry, table, row, column, db_name):

        new_value = entry.get().replace("\u3000", " ").strip()
        # 空文字（半角・全角スペースのみ）はNoneとして扱う
        if new_value == "":
            new_value = None
        # 編集されたカラムに対応するデータを更新
        self.temp_data[db_name] = new_value

        # Treeviewの表示を更新
        values = list(table.tree.item(row, "values"))
        col_index = int(column[1:]) - 1
        if new_value is None:
            values[col_index] = "-"
        else:
            values[col_index] = new_value
        table.tree.item(row, values=values)

        entry.destroy()
    
    def on_register_button_click(self, parent, patient_data):
        # 患者データの登録、存在チェック
        patient_id = self.data_base.check_patient(patient_data)
        
        if patient_id is not None:
            # 検査表データの登録
            self.data_base.output_result(patient_id, self.temp_data)

        parent.destroy()
        self.open_analyzed_window(next(self.itr_analyzed_data, None))
