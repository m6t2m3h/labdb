import os
import logging
import cv2
import TableExtractor as te
import TableLineRemover as lr

log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=getattr(logging, log_level, logging.INFO))
 
# 解析する画像の指定
path_to_image = "./image/blood_test.jpg"

try:
    # 表の抽出
    table_extractor = te.TableExtractor(path_to_image)
    table_image = table_extractor.execute()

    # 表の線を削除
    line_remover = lr.TableLinesRemover()
    line_removed_image = line_remover.execute()

except (FileExistsError, ValueError) as e:
    print(f"エラー: {e}")
except Exception as e:
    raise
else:
    print("正常終了")