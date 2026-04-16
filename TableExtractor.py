import os
import logging
import cv2
import numpy as np

# 画像の中から表を抽出するクラス
class TableExtractor:
    
    BASE_DIR = "./process_images/table_extractor/"

    def __init__(self, image_path):
        self.image_path = image_path
        self.logger = logging.getLogger(__name__)

        # デバッグ用画像出力ディレクトリの作成
        if self.logger.isEnabledFor(logging.DEBUG):
            os.makedirs(self.BASE_DIR, exist_ok=True)
    
    def execute(self):

        # 画像ファイルの読み込み
        if not os.path.exists(self.image_path):
            raise FileExistsError(f"ファイルが存在しません: {self.image_path}")
        
        self.image = cv2.imread(self.image_path)

        if self.image is None:
            raise ValueError(f"画像を読み込めません: {self.image_path}")
        
        self.store_process_image("00_original.jpg", self.image)

        # グレースケール変換
        self.gray_image = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        self.store_process_image("01_grayscale.jpg", self.gray_image)

        # 2値化と反転
        ret, self.binary_image = cv2.threshold(self.gray_image, 90, 255, cv2.THRESH_BINARY_INV)
        self.store_process_image("02_threshold.jpg", self.binary_image)

        # 線の拡張
        self.dilated_image = cv2.dilate(self.binary_image, None, iterations=5)
        self.store_process_image("03_dilate.jpg", self.dilated_image)

        # 画像内全ての輪郭を描く
        self.find_contours()
        self.store_process_image("04_all_contours.jpg", self.image_with_all_contours)

        # 四角形の輪郭だけを抽出
        self.leave_only_rectangles()  
        self.store_process_image("05_only_rectangular_contours.jpg", self.image_with_only_rectangular_contours)

        # 最大の四角形だけを抽出
        self.find_largest_contour()
        self.store_process_image("06_contour_with_max_area.jpg", self.image_with_contour_with_max_area)

    def find_contours(self):
        self.contours, self.hierarchy = cv2.findContours(self.dilated_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        self.image_with_all_contours = self.image.copy()
        cv2.drawContours(self.image_with_all_contours, self.contours, -1, (0, 255, 0), 3)

    def leave_only_rectangles(self):
        self.rectangular_contours = []
        for contour in self.contours:
            peri = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
            if len(approx) == 4:
                self.rectangular_contours.append(approx)
        self.image_with_only_rectangular_contours = self.image.copy()
        cv2.drawContours(self.image_with_only_rectangular_contours, self.rectangular_contours, -1, (0, 255, 0), 3)

    def find_largest_contour(self):
        max_area = 0
        self.contour_with_max_area = None
        for contour in self.rectangular_contours:
            area = cv2.contourArea(contour)
            if area > max_area:
                max_area = area
                self.contour_with_max_area = contour
        self.image_with_contour_with_max_area = self.image.copy()
        cv2.drawContours(self.image_with_contour_with_max_area, [self.contour_with_max_area], -1, (0, 255, 0), 3)

    def store_process_image(self, file_name, image):
        if self.logger.isEnabledFor(logging.DEBUG):
            cv2.imwrite(self.BASE_DIR + file_name, image)
        