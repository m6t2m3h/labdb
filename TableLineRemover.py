import cv2
import numpy as np
from TableProcessorBase import TableProcessorBase

# 2値化されている画像の中から表の線を取り除くクラス
class TableLineRemover(TableProcessorBase):

    def execute(self, image):
        self.image = image
        # 時間計測開始
        self.start_timer()
        # a.縦線のみ抽出
        vertical_image = self.extract_vertical_lines(self.image)
        # b.横線のみ抽出
        horizonal_image = self.extract_horizontal_lines(self.image)
        # aとbを合成して表の線のみにする
        table_line_image = self.combine_line_images(vertical_image, horizonal_image)
        # 表の線を膨張
        table_line_image = self.make_lines_thicker(table_line_image)
        # 元画像から表の線を引く
        text_image = self.remove_table_lines(self.image, table_line_image)
        # ノイズの除去
        text_image = self.remove_noise(text_image)
        # 時間計測終了
        self.end_timer()
        # 文字のみになった画像を返す
        return text_image

    def extract_vertical_lines(self, image):
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(1, image.shape[0]//50))
        vertical_image = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel, iterations=3)
        self.store_process_image("vertical_lines.jpg", vertical_image)
        return vertical_image

    def extract_horizontal_lines(self, image):
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(self.image.shape[1]//50, 1))
        horizonal_image = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel, iterations=3)
        self.store_process_image("horizontal_lines.jpg", horizonal_image)
        return horizonal_image

    def combine_line_images(self, vertical, horizonal):
        combined_image = cv2.add(vertical, horizonal)
        self.store_process_image("combined_lines.jpg", combined_image)
        return combined_image

    def make_lines_thicker(self, line_image):
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        dilated_image = cv2.dilate(line_image, kernel, iterations=5)
        self.store_process_image("dilated.jpg", dilated_image)
        return dilated_image

    def remove_table_lines(self, image, table):
        subtracted_image = cv2.subtract(image, table)
        self.store_process_image("without_lines.jpg", subtracted_image)
        return subtracted_image

    def remove_noise(self, image):
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        denoised_image = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel, iterations=1)
        self.store_process_image("noise_removed.jpg", denoised_image)
        # モルフォロジー変換で出てきた微妙な値を再度２値化で整理する
        _, denoised_image = cv2.threshold(denoised_image, 127, 255, cv2.THRESH_BINARY_INV)
        self.store_process_image("inverted.jpg", denoised_image)
        return denoised_image
        