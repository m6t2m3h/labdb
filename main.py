import os
import logging

import FileViewer as fv
import TableExtractor as te
import TableLineRemover as tlr
import OcrToDataConverter as odc
import TableDataRepository as tdr
import TableViewer as tv

log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=getattr(logging, log_level, logging.INFO)) 

try:
    # 解析する画像指定のウィンドウ表示
    file_dialog = fv.FileViewer()
    file_pathes = file_dialog.window_open()

    for path_to_image in file_pathes:

        # 表の抽出
        table_extractor = te.TableExtractor(path_to_image)
        table_image = table_extractor.execute()

        # 表の線を削除
        line_remover = tlr.TableLinesRemover(path_to_image, table_image)
        line_removed_image = line_remover.execute()
    
        # OCRで文字解析
        ocr_tool = odc.OcrToDataConverter(path_to_image, table_image, line_removed_image)
        table_data = ocr_tool.execute()

        # データベース登録
        data_base = tdr.TableDataRepository()
        data_base.create_table()

        insert_name = []
        insert_value = []
        for row in table_data:
            if data_base.ITEM_NAME.get(row[0]) is not None:
                if len(row) > 2:
                    insert_name.append(data_base.ITEM_NAME[row[0]])
                    insert_value.append(row[1])
            else:
                data_base.logger.debug(f"項目名\"{row[0]}\" はありません。")

        if len(insert_name) > 0:
            data_base.insert_table_data(insert_name, insert_value)
        else:
            data_base.logger.info(f"\"{path_to_image}\" に登録できるデータはありません。")

    # テーブルのGUI表示
    data_base = tdr.TableDataRepository()
    all_data = data_base.select_table_data()
    table_window = tv.TableViewer(all_data)
    table_window.open_window()

except (FileExistsError, ValueError) as e:
    print(f"エラー: {e}")
except Exception as e:
    raise
else:
    print("正常終了")