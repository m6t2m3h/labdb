import logging
import cv2
import numpy as np
import subprocess
from TableProcessorBase import TableProcessorBase

class OcrToDataConverter(TableProcessorBase):

    def __init__(self, file_path, table_image, text_image):
        super().__init__(file_path)
        _, self.original_image = cv2.threshold(table_image, 90, 255, cv2.THRESH_BINARY_INV)
        self.original_image = cv2.cvtColor(self.original_image, cv2.COLOR_GRAY2BGR)
        self.text_image = text_image
        # pytesseractはDEBUGがうるさいのでINFO以上にする
        logging.getLogger("pytesseract").setLevel(logging.INFO)

    def execute(self):
        self.start_timer()
        # 単語をブロブ化する
        blob_image = self.create_text_blobs(self.text_image)
        # ブロブの輪郭を取得する
        contours = self.find_contours(blob_image)
        # ブロブを外接矩形に変換する
        bounding_boxes = self.contours_to_bounding_boxes(contours)
        # 外接矩形の高さの平均を求める
        mean_height = self.get_mean_height(bounding_boxes)
        # 外接矩形をy座標で並べ替え
        bounding_boxes = self.sort_boxes(bounding_boxes)
        # 全ての外接矩形を近いy座標ごとに列としてグループ化する
        rows = self.group_boxes_into_rows(mean_height, bounding_boxes)
        # 列をx座標で並べ替え
        rows = self.sort_rows(rows)
        # 矩形単位でOCRを実行
        table = self.crop_each_bounding_box_and_ocr(rows)
        # CSVファイルで結果を出力
        self.generate_csv_file(table)
        self.end_timer()
        return table

    def create_text_blobs(self, image):
        # 横長のカーネルで水平方向に単語をブロブ化する
        horizonal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
        blob_image = cv2.dilate(image, horizonal_kernel, iterations=3)
        # さらに正方形のカーネルで細かな隙間を埋める
        gap_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (4, 4))
        blob_image = cv2.dilate(blob_image, gap_kernel, iterations=3)
        self.store_process_image("text_blobs.jpg", blob_image)
        return blob_image
    
    def find_contours(self, image):
        contours, _ = cv2.findContours(image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        filtered_contours = []             
        # 小さな輪郭は排除する
        for contour in contours:
            area = cv2.contourArea(contour)
            if area >= 100:
                filtered_contours.append(contour)
        contours_image= self.original_image.copy()   
        contours_image = cv2.drawContours(contours_image, filtered_contours, -1, (0, 0, 255), 3)
        self.store_process_image("contours.jpg", contours_image)
        return filtered_contours
    
    def contours_to_bounding_boxes(self, contours):
        bounding_boxes = []
        bounding_boxes_image = self.original_image.copy()
        # 非常に小さな外接矩形は文字の内部なので排除する
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            if w > 30 and h > 30:
                bounding_boxes.append((x, y, w, h))
                bounding_boxes_image = cv2.rectangle(bounding_boxes_image, (x, y), (x + w, y + h), (0, 0, 255), 5)

        self.store_process_image("bounding_boxes.jpg", bounding_boxes_image)
        return bounding_boxes
    
    def get_mean_height(self, bounding_boxes):
        heights = []
        for bounding_box in bounding_boxes:
            x, y, w, h = bounding_box
            heights.append(h)
        return np.mean(heights)

    def sort_boxes(self, bounding_boxes):
        # y軸の座標で昇順で並べ替え
        return sorted(bounding_boxes, key=lambda x: x[1])

    def group_boxes_into_rows(self, mean_height, boxes):
        rows = []
        half_of_mean_height = mean_height / 2
        current_row = [ boxes[0] ]

        for box in boxes[1:]:
            current_box_y = box[1]
            previous_box_y = current_row[-1][1]
            distance_between_boxes = abs(current_box_y - previous_box_y)
            if distance_between_boxes <= half_of_mean_height:
                current_row.append(box)
            else:
                rows.append(current_row)
                current_row = [ box ]
        rows.append(current_row)
        return rows

    def sort_rows(self, rows):
        for row in rows:
            row.sort(key=lambda x: x[0])
        return rows

    def crop_each_bounding_box_and_ocr(self, rows):
        table = []
        current_row = []
        image_number = 0
        for row in rows:
            for bounding_box in row:
                x, y, w, h = bounding_box
                y = y - 5
                cropped_image = self.text_image[y:y+h, x:x+w]
                image_slice_path = "./ocr_slices/img_" + str(image_number) + ".jpg"
                cv2.imwrite(image_slice_path, cropped_image)
                results_from_ocr = self.get_result_from_tersseract(image_slice_path)
                current_row.append(results_from_ocr)
                image_number += 1
            table.append(current_row)
            current_row = []
        return table
    
    def get_result_from_tersseract(self, image_path):
        output = subprocess.getoutput('tesseract ' + image_path + ' - -l jpn+eng --oem 3 --psm 7 --dpi 72') 
        output = output.replace(" ", "")
        return output

    def generate_csv_file(self, table):
        with open("output.csv", "w") as f:
            for row in table:
                f.write(",".join(row) + "\n")