from paddleocr import PaddleOCR
import pandas as pd

ocr = PaddleOCR(use_angle_cls=True, lang='en')

def parse_scanned_pdf(file_path):

    result = ocr.ocr(file_path, cls=True)

    rows = []
    for line in result[0]:
        rows.append([line[1][0]])

    df = pd.DataFrame(rows, columns=["extracted_text"])

    return df
