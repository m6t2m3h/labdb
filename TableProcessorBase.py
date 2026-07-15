import os
import time
import logging
import cv2
from functools import wraps

class TableProcessorBase:

    COLOR_BLUE_BGR = (255, 0, 0)
    COLOR_GREEN_BGR = (0, 255, 0)
    COLOR_RED_BGR = (0, 0, 255)

    BASE_DIR = "./process_images/"
    
    def __init__(self, image_path):
        self.logger = logging.getLogger(__name__)
        self.image_path = image_path
        self.debug_image_no = 0
        basename = os.path.splitext(os.path.basename(self.image_path))[0]

        # デバッグ用画像出力ディレクトリの作成
        if self.logger.isEnabledFor(logging.DEBUG):
            self.directory = f"{self.BASE_DIR}{basename}/{self.__class__.__name__}/"
            os.makedirs(self.directory, exist_ok=True)
        
    def start_timer(self):
        self.start_time = time.perf_counter()

    def end_timer(self):
        end_time = time.perf_counter()
        self.logger.debug(f"[{self.__class__.__name__}]{end_time - self.start_time:.6f} sec")
    
    def file_open(self):
        if not os.path.exists(self.image_path):
            raise FileExistsError(f"ファイルが存在しません: {self.image_path}")
        
        image = cv2.imread(self.image_path)

        if image is None:
            raise ValueError(f"画像を読み込めません: {self.image_path}")
        return image

    def store_process_image(self, file_name, image):
        if self.logger.isEnabledFor(logging.DEBUG):
            cv2.imwrite(self.directory + f"{self.debug_image_no:02}_" + file_name, image)
            self.debug_image_no += 1

    # 文字列ブロブを描画する
    def write_debug_image(self, image, ocr_result):
        plot_image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        for box, _, _ in ocr_result:
            p1, _, p3, _ = box
            cv2.rectangle(plot_image, p1, p3, self.COLOR_GREEN_BGR, 2)
        self.store_process_image("boxes.jpg", plot_image) 

# 任意のメソッドの速度を計測する
def measure_time(func):

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not self.logger.isEnabledFor(logging.DEBUG):
            return func(self, *args, **kwargs)

        start = time.perf_counter()

        try:
            return func(self, *args, **kwargs)
        finally:
            elapsed = time.perf_counter() - start
            self.logger.debug(f"<{func.__name__}>: {elapsed:.6f} sec")

    return wrapper