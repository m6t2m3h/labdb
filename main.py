import os
import logging

from FileViewer import FileViewer
from TableDataRepository import TableDataRepository

def main():

    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(level=getattr(logging, log_level, logging.INFO))

    # データベース処理用
    data_base = TableDataRepository()
    data_base.create_table()

    # 解析する画像指定のウィンドウ表示
    file_dialog = FileViewer(data_base)
    file_dialog.open_main_window()

try:
    if __name__ == "__main__":
        main()
except (FileExistsError, ValueError):
    logging.exception(f"入力データエラー")
except Exception:
    logging.exception(f"処理中にエラー発生")
    raise
else:
    logging.info("正常終了")
