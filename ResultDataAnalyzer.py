import cv2
from difflib import *
from OcrManager import OcrManager
from TableProcessorBase import TableProcessorBase
from DatabaseDefinition import DatabaseDefinition

class ResultDataAnalyzer(TableProcessorBase):

    def __init__(self, path):
        super().__init__(path)
        self.ocr_manager = OcrManager()
        self.reader = OcrManager.get_reader()

    def execute(self, image):
        
        # OCR実行前の画像調整
        image = self.ocr_manager.preprocess_for_ocr(image)
        # OCRの実行
        self.start_timer()           
        result = self.reader.readtext(image,  **self.ocr_manager.params)
        self.end_timer()
        # 検出したテキストのブロブボックスを描画
        self.write_debug_image(image, result)
        # 項目名と値の検索
        result_pare = self.search_pare_item(result, DatabaseDefinition.RESULT_ITEM)

        result_item = {
            key: result_pare[val]
            for key, val in DatabaseDefinition.RESULT_DATA_REVERSE.items()
            if val in result_pare
        }

        return result_item

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

            value = self.find_scope_value(item_data, raw_list)

            # 保存前に不要なスペースを除去
            if value is not None:
                value = value.strip()
                item_list[best_name] = value
            i += 2

        return item_list

    def find_scope_value(self, item_data, raw_list):

        # 項目名の座標
        item_bbox = item_data[0]
        top_left, top_right, bottom_right, bottom_left = item_bbox

        item_right_x = top_right[0]
        item_y = top_right[1]

        # 判定範囲
        Y_MARGIN = 20
        MIN_X_DISTANCE = 5
        MAX_X_DISTANCE = 300

        # OCR結果から値を探す
        for ocr_data in raw_list:
            value_bbox = ocr_data[0]
            top_left, _, _, _ = value_bbox

            value_left_x = top_left[0]
            value_y = top_left[1]

            x_distance = value_left_x - item_right_x
            y_distance = abs(value_y - item_y)

            if (MIN_X_DISTANCE <= x_distance <= MAX_X_DISTANCE and
                    y_distance <= Y_MARGIN):
                return ocr_data[1]

        return None
