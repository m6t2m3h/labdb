import os
import logging
import time
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
            self.file_number = 0
    
    def file_open(self):
        if not os.path.exists(self.image_path):
            raise FileExistsError(f"ファイルが存在しません: {self.image_path}")
        
        self.image = cv2.imread(self.image_path)

        if self.image is None:
            raise ValueError(f"画像を読み込めません: {self.image_path}")
            
        self.store_process_image("original.jpg", self.image)

    def execute(self):

        # 画像ファイルの読み込み
        self.file_open()
        # 時間計測開始
        start = time.perf_counter()

        # 【ステップ１】前処理
        # 赤と青の鉛筆でのマーキングを消去
        no_red_blue_image = self.remove_red_blue(self.image)
        # グレースケール変換とぼかし
        gray_image = cv2.cvtColor(no_red_blue_image, cv2.COLOR_BGR2GRAY)
        gray_image = cv2.GaussianBlur(gray_image, (3,3), 0)
        self.store_process_image("grayscale.jpg", gray_image)
        # 2値化と反転
        _, binary_image = cv2.threshold(gray_image, 90, 255, cv2.THRESH_BINARY_INV)
        self.store_process_image("binary.jpg", binary_image)
        # 線の拡張
        dilated_image = cv2.dilate(binary_image, None, iterations=5)
        self.store_process_image("dilate.jpg", dilated_image)

        # 【ステップ２】輪郭を見付けて最大級の長方形の輪郭を見つける
        # 画像内全ての輪郭を描く
        contours = self.find_contours(dilated_image)
        # 四角形の輪郭だけを抽出
        rectangular_contours = self.leave_only_rectangles(contours)
        # 最大級の四角形だけを抽出
        largest_contours = self.find_largest_contours(rectangular_contours)

        #####一時的にリストの最初の要素(表の左側)のみ解析していく#####
        # 【ステップ３】遠近感補正
        # 四角形の頂点を求める
        points = self.rectangle_points(largest_contours)
        # 生成する新しい画像サイズを求める
        new_height, new_width = self.get_new_image_size(points[0])
        #print(f"new_heigh={new_height},new_width={new_width}")
        # 遠近変換
        tmp_image = self.perspective_transform(points[0], new_height, new_width)
        # パティングの追加
        new_image = self.add_10_percent_padding(tmp_image)
        
        # 時間計測終了
        end = time.perf_counter()
        print(f"処理時間: {end - start:.6f} 秒")

        return new_image

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

        mask = mask_red + mask_blue
   
        # マスク部分を白で上書き
        noRBimage = image.copy()
        noRBimage[mask > 0] = [255, 255, 255]

        self.store_process_image("remove_red_blue.jpg", noRBimage)

        return noRBimage
    
    def find_contours(self, image):
        contours, _ = cv2.findContours(image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        all_contour_image = self.image.copy()
        cv2.drawContours(all_contour_image, contours, -1, (0, 255, 0), 3)
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
        cv2.drawContours(rectangle_contour_image, rectangular_contours, -1, (0, 255, 0), 3)
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
        cv2.drawContours(largest_contours_image, largest_contours, -1, (0, 255, 0), 3)
        self.store_process_image("largest_contours.jpg", largest_contours_image)
        return largest_contours

    def rectangle_points(self, contours):

        coordinate_set = []
        plotted_image = self.image.copy()
        
        for contour in contours:
            coordinate_set.append(self.order_points(contour))

        for coordinate in coordinate_set:
            for point in coordinate:
                point_coordinate = (int(point[0]), int(point[1]))
                plotted_image = cv2.circle(plotted_image, point_coordinate, 10, (0, 0, 255), -1)
        
        self.store_process_image("corner_points_plotted.jpg", plotted_image)
        return coordinate_set

    def order_points(self, pts):

        # OpenCVの座標を扱いやすい形にしていく
        # 謎次元を削除
        # (4, 1, 2) -> (4,1)
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
        transformed_image = cv2.warpPerspective(self.image, matrix, (width, height))
        self.store_process_image("perspective_corrected.jpg", transformed_image)
        return transformed_image

    def add_10_percent_padding(self, image):
        image_height = self.image.shape[0]
        padding = int(image_height * 0.1)
        new_image = cv2.copyMakeBorder(image, padding, padding, padding, padding, cv2.BORDER_CONSTANT, value=[255, 255, 255])
        self.store_process_image("perspective_corrected_with_padding.jpg", new_image)
        return new_image

    def store_process_image(self, file_name, image):
        if self.logger.isEnabledFor(logging.DEBUG):
            cv2.imwrite(self.BASE_DIR + f"{self.file_number:02}_" + file_name, image)
            self.file_number+=1
        