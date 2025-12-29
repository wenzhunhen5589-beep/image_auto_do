import time

import cv2
from PIL import Image
from paddleocr import PaddleOCR
from paddleocr.tools.infer.utility import draw_ocr
import numpy as np  # 导入 numpy 库

def image_to_paddleocr_det(image, _ocr=None, isdbug=False):
    if _ocr == None:
        # 模型
        ocr = PaddleOCR(lang='ch')
    else:
        ocr = _ocr

    start_time = time.time()
    res = ocr.ocr(img=image, cls=False, rec=False)
    result = res[0]

    if (isdbug & (result != None)):
        end_time = time.time()
        # 计算执行时间
        execution_time = end_time - start_time
        print(f"[image_to_paddleocr_det] Function execution time: {execution_time} seconds")
        print(result)

        # 绘制带有文本框的图像
        boxes = [item for item in result]

        if isinstance(image, np.ndarray):
            # 确保图像为 RGB 格式，OpenCV 默认是 BGR，需要转换
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        else:
            # 如果传入的是文件路径，使用 PIL 打开图像
            image = Image.open(image).convert('RGB')
            image = np.array(image)  # 转换为 NumPy 数组

        # image = Image.open(image).convert('RGB')
        im_show = draw_ocr(image, boxes, None, font_path='simfang.ttf')
        im_show = Image.fromarray(im_show)
        im_show.show(title="image_to_paddleocr_det")
    return result


def image_to_paddleocr_rec(image, isdbug=False):
    # 创建 PaddleOCR 实例
    ocr = PaddleOCR(lang='ch')
    # 使用 PaddleOCR 提取文本及其坐标
    result = ocr.ocr(image, cls=False)
    result = result[0]

    if isdbug:
        # 输出提取的文本及其坐标
        for line in result:
            word = line[1][0]
            coordinate = line[0]
            print(word)
            print(coordinate)
        # 绘制带有文本框的图像
        boxes = [item[0] for item in result]
        txts = [item[1][0] for item in result]
        image = Image.open(image).convert('RGB')
        im_show = draw_ocr(image, boxes, txts, font_path='simfang.ttf')
        im_show = Image.fromarray(im_show)
        im_show.show()

    return result