import cv2
import easyocr
import logging

class OcrManager:

    _reader = None

    params = {
            "text_threshold":0.6,   # 文字だと確定する信頼度(デフォルト0.7)
            "low_text":0.3,         # 文字候補とする最低ラインの信頼度(デフォルト0.4)
            "link_threshold":0.2,   # 文字候補同士をつなぐ閾値(デフォルト0.4）
            "ycenter_ths":0.3,      # 縦位置がずれても同じ行とする閾値(デフォルト0.5)
            "width_ths":0.3         # 文字領域をまとめる距離(デフォルト0.5)
        }

    @classmethod
    def get_reader(cls):    
        if cls._reader is None:
            # GPUを使っていないと警告が出るので抑制
            logging.getLogger("easyocr").setLevel(logging.ERROR)
            cls._reader = easyocr.Reader(['ja', 'en'], gpu=False)
        return cls._reader
    
    def preprocess_for_ocr(self, image):
        # 縮小
        image = self.downscale(image)
        # アンシャープマスク
        sharp_image = self.unsharp_mask(image)
        # 大津の二値化
        # _, binary_image = cv2.threshold(sharp_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        # return binary_image
        return sharp_image
    
    def unsharp_mask(self, image):
         # 第２引数ksize：カーネルサイズ自動、第３引数sigmaX：ぼかしの強さ
        blur_image = cv2.GaussianBlur(image, (0,0), 3)
        # 1.5 × gray - 0.5 × blur + 0
        sharp_image = cv2.addWeighted(image, 1.5, blur_image, -0.5, 0)
        return sharp_image

    def downscale(self, image):
        # 画像サイズの縮小
        resize_image = cv2.resize(image, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
        return resize_image
    
