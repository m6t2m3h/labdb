import cv2
import numpy as np
from TableProcessorBase import TableProcessorBase

# 参考
# How To: Extract Table From Image In Python (OpenCV & OCR)
# https://livefiredev.com/how-to-extract-table-from-image-in-python-opencv-ocr/

# 画像の中から血液検査表と基礎情報の画像を抽出するクラス
class TableExtractor(TableProcessorBase):

    IMAGE_SCALE_FACTOR = 0.5    # 画像縮小サイズ
    LINE_DILATE_ITERATIONS = 5  # 線検出のための膨張の処理回数
    LINE_DETECT_PADDING = 10    # 表線検出処理のために追加するパディング

    def execute(self):

        # 画像ファイルの読み込み
        self.image = self.file_open()
        self.store_process_image("original.jpg", self.image)
        # 時間計測開始
        self.start_timer()

        # 【ステップ１】前処理
        # 画像サイズの縮小
        self.image = cv2.resize(self.image,
                                None,
                                fx=self.IMAGE_SCALE_FACTOR,
                                fy=self.IMAGE_SCALE_FACTOR,
                                interpolation=cv2.INTER_AREA
                            )
        # 赤と青の鉛筆でのマーキングを消去
        process_image = self.remove_red_blue(self.image)
        # グレースケール変換
        self.gray_image = self.convert_grayscale(process_image)
        # 適用的ヒストグラム平坦化
        process_image = self.equalize_histgram(self.gray_image)
        # 2値化と反転
        self.inverted_image = self.convrt_binary(process_image)

        # 【ステップ２】輪郭を見付けて最大級の長方形の輪郭を見つける
        # 線の膨張
        process_image = self.dilate_all_lines(self.inverted_image)
        # 画像内全ての輪郭を描く
        contours = self.find_contours(process_image)
        # 四角形の輪郭だけを抽出
        rectangular_contours = self.leave_only_rectangles(contours)
        # 最大級の四角形だけを抽出
        largest_contours = self.find_largest_contours(rectangular_contours)
        # 表を元の画像から除去して基礎情報のみにする
        patient_image = self.crop_header(self.gray_image, largest_contours)

        # 【ステップ３】遠近感補正
        # 四角形の頂点を求める
        lab_image = []
        points = self.rectangle_points(largest_contours)
        for point in points:
            # 生成する新しい画像サイズを求める
            new_height, new_width = self.get_new_image_size(point)
            # 透視変換
            new_image = self.perspective_transform(point, new_height, new_width)
            # 表線削除時のためパティングの追加
            new_image = self.add_padding(new_image)
            lab_image.append(new_image)

        # 時間計測終了
        self.end_timer()
        return patient_image, lab_image

    def remove_red_blue(self, image):

        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # 赤のマスク
        lower_red1 = np.array([0, 100, 100])
        upper_red1 = np.array([10, 255, 255])

        lower_red2 = np.array([170, 100, 100])
        upper_red2 = np.array([180, 255, 255])

        mask_r1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask_r2 = cv2.inRange(hsv, lower_red2, upper_red2)
        mask_red = mask_r1 + mask_r2

        kernel = np.ones((3,3), np.uint8)
        mask_red = cv2.dilate(mask_red, kernel, iterations=1)
        self.store_process_image("mask_red.jpg", mask_red)

        # 青のマスク
        lower_blue = np.array([100, 80, 80])
        upper_blue = np.array([140, 255, 255])

        mask_hsv = cv2.inRange(hsv, lower_blue, upper_blue)
        mask_blue = cv2.dilate(mask_hsv, kernel, iterations=1)
        self.store_process_image("mask_blue.jpg", mask_blue)

        mask = cv2.bitwise_or(mask_red, mask_blue)
   
        # マスク部分を白で上書き
        noRBimage = image.copy()
        noRBimage[mask > 0] = [255, 255, 255]

        self.store_process_image("remove_red_blue.jpg", noRBimage)

        return noRBimage

    def convert_grayscale(self, image):
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        self.store_process_image("grayscale.jpg", gray_image)
        return gray_image

    def equalize_histgram(self, image):
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        image = clahe.apply(image)
        mean_val = image.mean()    
        threshold = int(mean_val * 0.5)
        _, clahe_image= cv2.threshold(image, threshold, 255, cv2.THRESH_BINARY)
        self.store_process_image("clahe.jpg", clahe_image)
        return clahe_image

    def convrt_binary(self, image):
        _, binary_image = cv2.threshold(image, 90, 255, cv2.THRESH_BINARY_INV)
        self.store_process_image("binary.jpg", binary_image)
        return binary_image
    
    def dilate_all_lines(self, image):
        dilated_image = cv2.dilate(image, None, iterations=self.LINE_DILATE_ITERATIONS)
        self.store_process_image("dilate.jpg", dilated_image)
        return dilated_image
    
    def find_extarnal_contours(self, image):
        contours, _ = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contour_image = self.image.copy()
        cv2.drawContours(contour_image, contours, -1, self.COLOR_GREEN_BGR, 3)
        self.store_process_image("ex_contour.jpg", contour_image)
        return contours    
    
    def find_contours(self, image):
        contours, _ = cv2.findContours(image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        all_contour_image = self.image.copy()
        cv2.drawContours(all_contour_image, contours, -1, self.COLOR_GREEN_BGR, 3)
        self.store_process_image("all_contour.jpg", all_contour_image)
        return contours        

    def leave_only_rectangles(self, contours):
        rectangular_contours = []
        for contour in contours:
            peri = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
            if len(approx) == 4:
                rectangular_contours.append(approx)
        
        rectangle_contour_image = self.image.copy()
        cv2.drawContours(rectangle_contour_image, rectangular_contours, -1, self.COLOR_GREEN_BGR, 3)
        self.store_process_image("rectangle_contour.jpg", rectangle_contour_image)
        return rectangular_contours

    def find_largest_contours(self, contours, tolerance=0.95):
        max_area = 0
        areas = []

        for contour in contours:
            area = cv2.contourArea(contour)
            areas.append((contour, area))

            if area > max_area:
                max_area = area

        largest_contours = [
            contour
            for contour, area in areas
            if area >= max_area * tolerance
        ]

        largest_contours_image = self.image.copy()
        cv2.drawContours(largest_contours_image, largest_contours, -1, self.COLOR_GREEN_BGR, 3)
        self.store_process_image("largest_contours.jpg", largest_contours_image)
        return largest_contours

    def crop_header(self, image, contours):
        if not contours:
            return image
        # 表輪郭の上辺のうち最小値で画像を切り取る
        top = min(
            cv2.boundingRect(contour)[1]
            for contour in contours
        )
        height, width = image.shape[:2]
        crop = image[:top, :width]
        self.store_process_image("header.jpg", crop)
        return crop
    
    def rectangle_points(self, contours):

        coordinate_set = []
        plotted_image = self.image.copy()
        
        for contour in contours:
            coordinate_set.append(self.order_points(contour))

        for coordinate in coordinate_set:
            for point in coordinate:
                point_coordinate = (int(point[0]), int(point[1]))
                plotted_image = cv2.circle(plotted_image, point_coordinate, 10, self.COLOR_RED_BGR, -1)
        
        self.store_process_image("corner_points_plotted.jpg", plotted_image)
        return coordinate_set

    def order_points(self, pts):

        # OpenCVの座標を扱いやすい形にしていく
        # 謎次元を削除
        # (4, 1, 2) -> (4,2)
        pts = pts.reshape(4, 2)

        rect = np.zeros((4, 2), dtype="float32")

        # 座標の和が最小なら左上の点
        # 最大なら右下の点
        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)]
        rect[2] = pts[np.argmax(s)]

        # 座標の差が最小なら右上
        # 最大なら左下
        d = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(d)]
        rect[3] = pts[np.argmax(d)]

        # ４点の座標を返す(左上、右上、右下、左下)
        return rect

    def get_new_image_size(self, contour):
        existing_image_width = self.image.shape[1]
        existing_image_width_reduced_by_10_percent = int(existing_image_width * 0.9)
        
        top_left_and_top_right = self.calculate_distance(contour[0], contour[1])
        top_left_and_bottom_left = self.calculate_distance(contour[0], contour[3])

        aspect_ratio = top_left_and_bottom_left / top_left_and_top_right

        new_image_width = existing_image_width_reduced_by_10_percent
        new_image_height = int(new_image_width * aspect_ratio)

        return new_image_height, new_image_width

    def calculate_distance(self, p1, p2):
        dis = ((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2) ** 0.5
        return dis

    def perspective_transform(self, contour, height, width):
        pts1 = np.float32(contour)
        pts2 = np.float32([[0, 0], [width, 0], [width, height], [0, height]])
        matrix = cv2.getPerspectiveTransform(pts1, pts2)
        transformed_image = cv2.warpPerspective(self.inverted_image, matrix, (width, height))
        self.store_process_image("perspective_corrected.jpg", transformed_image)
        return transformed_image

    def add_padding(self, image):
        padding = self.LINE_DETECT_PADDING
        new_image = cv2.copyMakeBorder(image,
                                    padding,
                                    padding,
                                    padding,
                                    padding,
                                    cv2.BORDER_CONSTANT,
                                    value=[0, 0, 0]
                                )
        self.store_process_image("added_padding.jpg", new_image)
        return new_image
        