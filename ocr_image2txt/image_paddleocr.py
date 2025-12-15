import time
from PIL import Image
from paddleocr import PaddleOCR
from paddleocr.tools.infer.utility import draw_ocr


def image_to_paddleocr_det(image, isdbug=False):
    ocr = PaddleOCR(lang='ch')
    start_time = time.time()

    res = ocr.ocr(img=image, cls=False, rec=False)
    result = res[0]

    end_time = time.time()
    # 计算执行时间
    execution_time = end_time - start_time
    print(f"Function execution time: {execution_time} seconds")

    if isdbug:
        print(result)
        # 绘制带有文本框的图像
        boxes = [item for item in result]
        image = Image.open(image).convert('RGB')
        im_show = draw_ocr(image, boxes, None, font_path='simfang.ttf')
        im_show = Image.fromarray(im_show)
        im_show.show()
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