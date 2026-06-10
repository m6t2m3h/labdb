import tkinter as tk
from tkinter import filedialog

class FileViewer:

    def __init__(self):
        self.files = ()

    def window_open(self):
        # メインウィンドウ生成
        self.root=tk.Tk()
        # self.root.geometry("600x100")
        self.root.title("血液検査管理システム -解析ファイル選択-")
        # モニターとウィンドウの中央から座標を取得
        window_width = 600
        window_height = 200
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x_coordinate = (screen_width // 2) - (window_width // 2)   # モニター中央-ウィンドウ半分
        y_coordinate = (screen_height // 2) - (window_height // 2) # モニター中央-ウィンドウ半分
        self.root.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")
        # ファイル名表示リストボックス
        self.list_box = tk.Listbox(height=40, width=40)
        self.list_box.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        # 参照ボタン
        reference_button=tk.Button(text="参照", command=self.open_file, width=4)
        reference_button.pack(after=self.list_box, side=tk.LEFT, expand=False)
        # 実行ボタン
        execute_button=tk.Button(text="実行", command=self.execute, width=4, bg="salmon")
        execute_button.pack(after=reference_button, side=tk.LEFT, expand=False)
        # 閉じるボタン
        self.root.protocol("WM_DELETE_WINDOW", self.close_window)
        self.root.mainloop()
        return self.files

    def open_file(self):
        self.list_box.delete(0, tk.END)
        self.list_box.configure(state="normal")
        filetype=[("Image file",".png .jpg"),("PNG",".png"),("JPEG",".jpeg")]
        # デフォルトでホームディレクトリを開く
        self.files = filedialog.askopenfilenames(filetypes=filetype, initialdir="~/")
        for filename in self.files:
            self.list_box.insert(tk.END, filename)

    def execute(self):
        self.root.quit()
        self.root.destroy()

    def close_window(self):
        self.files = ()
        self.root.quit()
        self.root.destroy()