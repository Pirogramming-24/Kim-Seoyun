import os
os.environ['PADDLE_HOME'] = 'C:/paddle_models'

import re
import numpy as np
import cv2
from paddleocr import PaddleOCR

_ocr_model = None


def get_ocr_model():
    global _ocr_model
    if _ocr_model is None:
        _ocr_model = PaddleOCR(
            use_angle_cls=True, 
            lang='korean',

        )
    return _ocr_model

def run_ocr(image_file):
    model = get_ocr_model()
    image_bytes = image_file.read()
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    img = cv2.resize(img, None, fx=2.5, fy=2.5, interpolation=cv2.INTER_CUBIC)
    
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_norm = cv2.normalize(img_gray, None, 0, 255, cv2.NORM_MINMAX)
    img_result = cv2.cvtColor(img_norm, cv2.COLOR_GRAY2BGR)

    result = model.ocr(img_result)
    
    texts = []
    if result and result[0]:
        for line in result[0]:
            texts.append(line[1][0])
            
    return texts

def clean_ocr_value(val, nutrient_type):
    if val == 0: return 0
    
    val_int = int(val)
    val_str = str(val_int)
    if val > 50 and val_str.endswith('9'):
        val = float(val_str[:-1])

    if nutrient_type in ['protein', 'fat']:
       
        if val > 30: 
            val = val / 10.0
            
        if val == 19:
            val = 1.0

    return val

def parse_nutrition_info(texts):
    full_text = " ".join(texts)
    full_text = full_text.replace("kca!", "kcal").replace("나트름", "나트륨")
    
    print(f"=== 정정된 Raw Text: {full_text} ===")
    
    data = {"kcal": 0, "carbohydrate": 0, "protein": 0, "fat": 0}
    
    # 1. 칼로리 추출 
    kcal_match = re.search(r"(\d+)\s*kca", full_text, re.IGNORECASE)
    if kcal_match:
        data["kcal"] = float(kcal_match.group(1))

    # 2. 탄수화물 추출 
    carbs_match = re.search(r"탄\s*수\s*화\s*물.*?(\d+)\s*g", full_text)
    if not carbs_match: # g가 안붙어있을 경우 숫지만이라도 시도
         carbs_match = re.search(r"탄\s*수\s*화\s*물.*?(\d+)", full_text)
    if carbs_match:
        data["carbohydrate"] = float(carbs_match.group(1))

    # 3. 지방 추출 
    clean_text_for_fat = re.sub(r"(포화|트랜스)\s*지방", "", full_text)
    fat_match = re.search(r"지\s*방.*?(\d+)\s*g", clean_text_for_fat)
    if not fat_match:
        fat_match = re.search(r"지\s*방.*?(\d+)", clean_text_for_fat)
    if fat_match:
        data["fat"] = float(fat_match.group(1))

    # 4. 단백질 추출
    protein_match = re.search(r"단\s*백\s*질.*?(\d+)\s*g", full_text)
    if not protein_match:
        protein_match = re.search(r"단\s*백\s*질.*?(\d+)", full_text)
    if protein_match:
        data["protein"] = float(protein_match.group(1))

    return data