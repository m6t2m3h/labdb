import os
import time
import logging
import cv2

class TableProcessorBase:

    BASE_DIR = "./process_images/"

    def __init__(self, image_path):
        self.logger = logging.getLogger(__name__)
        self.image_path = image_path
        basename = os.path.splitext(os.path.basename(self.image_path))[0]
        # デバッグ用画像出力ディレクトリの作成
        if self.logger.isEnabledFor(logging.DEBUG):
            self.directory = f"{self.BASE_DIR}{basename}/{self.__class__.__name__}/"
            os.makedirs(self.directory, exist_ok=True)
            self.file_number = 0
    
    def start_timer(self):
        self.start_time = time.perf_counter()

    def end_timer(self):
        if self.logger.isEnabledFor(logging.DEBUG):
            end_time = time.perf_counter()
            print(f"[{self.__class__.__name__}]{end_time - self.start_time:.6f} 秒")
    
    def file_open(self):
        if not os.path.exists(self.image_path):
            raise FileExistsError(f"ファイルが存在しません: {self.image_path}")
        
        image = cv2.imread(self.image_path)

        if image is None:
            raise ValueError(f"画像を読み込めません: {self.image_path}")
        return image

    def store_process_image(self, file_name, image):
        if self.logger.isEnabledFor(logging.DEBUG):
            cv2.imwrite(self.directory + f"{self.file_number:02}_" + file_name, image)
            self.file_number+=1