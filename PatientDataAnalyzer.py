import cv2
from difflib import *
from OcrManager import OcrManager
from TableProcessorBase import TableProcessorBase
from DatabaseDefinition import DatabaseDefinition

class PatientDataAnalyzer(TableProcessorBase):

    def __init__(self, path):
        super().__init__(path)
        self.ocr_manager = OcrManager()
        self.reader = OcrManager.get_reader()
  
    def execute(self, image):
        
        # OCR実行前の画像調整
        image = self.ocr_manager.preprocess_for_ocr(image)

        # OCRの実行
        self.start_timer()        
        result = self.reader.readtext(image, **self.ocr_manager.params)
        self.end_timer()
        # 項目名と値の検索
        header_item = self.search_pare_item(result, DatabaseDefinition.HEADER_ITEM)

        # 時間の正規化
        time = header_item.get("時間")
        if time:
            header_item["時間"] = self.normaize_time(header_item["時間"])

        self.write_debug_image(image, result)
    
        patient_item = {
            key: header_item.get(val, None)
            for key, val in DatabaseDefinition.PATIENT_ITEM_REVERSE.items()
        }

        info_item = {
            key: header_item.get(val, None)
            for key, val in DatabaseDefinition.RESULT_INFO_REVERSE.items()
        }
    
        return patient_item, info_item

    def search_pare_item(self, raw_list, item_dict):
        item_list = {}
        i = 0
        while i < len(raw_list):
            item_data = raw_list[i]
            text = item_data[1]

            # 辞書から一番近い項目名を使う
            best_name = None
            best_score = 0
            for item_name in item_dict:
                score = SequenceMatcher(None, text, item_name).ratio()
                if score > best_score:
                    best_score = score
                    best_name = item_name

            if best_name is None or best_score <= 0.5 or i + 1 >= len(raw_list):
                i += 1
                continue

            value_data = raw_list[i + 1]
            value = value_data[1].replace("【", "").replace("】", "")

            # 文字列が空、またはスペースで分割される可能性がある項目はbboxから取得
            if best_name in ["患者名", "病院名", "担当医"] or value == "":
                near = self.find_nearest_value(value_data, raw_list)
                if near:
                    value = f"{value}　{near}" if value else near

            # 保存前に不要なスペースを除去
            value = value.strip()
            item_list[best_name] = value
            i += 2

        return item_list

    def find_nearest_value(self, item_data, raw_list):
        # 右上の座標位置
        item_bbox = item_data[0]
        item_x = item_bbox[1][0]
        item_y = item_bbox[1][1]

        min_distance = float("inf")
        nearest = None
        for data in raw_list:
            if data == item_data:
                continue
            # 左上の座標位置
            bbox = data[0]
            x = bbox[0][0]
            y = bbox[0][1]
            # 右側にある文字だけ対象
            if x > item_x and abs(x - item_x) < 50 and abs(y - item_y) < 20:
                distance = abs(x - item_x) - abs(y - item_y)
                if distance < min_distance:
                    min_distance = distance
                    nearest = data[1]
        return nearest
    
    def normaize_time(self, value):
        value = value.replace(".", ":").replace(";",":")
        return value
