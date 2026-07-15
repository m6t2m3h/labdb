from TableExtractor import TableExtractor
from TableLineRemover import TableLineRemover
from PatientDataAnalyzer import PatientDataAnalyzer
from ResultDataAnalyzer import ResultDataAnalyzer

class ImageAnalyzer:

    def __init__(self, image_path):
        self.image_path = image_path

    def execute(self):

        # 検査基礎情報と検査表の画像抽出
        table_extractor = TableExtractor(self.image_path)
        base_image, result_image = table_extractor.execute()

        # 検査基礎情報の解析
        patient_analyzer = PatientDataAnalyzer(self.image_path)
        patient_data, result_info_data = patient_analyzer.execute(base_image)

        line_remover = TableLineRemover(self.image_path)
        result_analyzer = ResultDataAnalyzer(self.image_path)

        result_item_data = result_info_data

        for table_image in result_image:
            # 検査表の線を削除
            line_removed_image = line_remover.execute(table_image)
            # OCRで文字解析
            table_data = result_analyzer.execute(line_removed_image)
            result_item_data = result_item_data | table_data
            
        return patient_data, result_item_data