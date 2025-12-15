from preprocess_image import preprocess_image
from image_easyocr import image_easyocr
from image_EAST import image_EAST
from image_paddleocr import image_to_paddleocr_det

if __name__ == '__main__':
    image_path = 'test.png'

    # PaddleOCR
    # 0.5096032619476318 seconds，可以选择检测和识别，对于标准文本具有很高的识别准确率，但对于复杂环境识别效果一般
    result = image_to_paddleocr_det(image_path)
    for (startX, startY, endX, endY) in result:
        print(startX)
        print(startY)
        print(endX)
        print(endY)

    # EAST模型
    # 0.601391 seconds，识别整张图片，速度很快，准确率较高，需要调整输入参数，参数影响很大，不识别文字
    boxes, rW, rH = image_EAST(image_path, _width=1280, _height=640, _confidence=0.8)
    # loop over the bounding boxes
    for (startX, startY, endX, endY) in boxes:
        # scale the bounding box coordinates based on the respective ratios
        startX = int(startX * rW)
        startY = int(startY * rH)
        endX = int(endX * rW)
        endY = int(endY * rH)
        print(startX)
        print(startY)
        print(endX)
        print(endY)

    # Easyocr模型
    # 0.9544482231140137 seconds 切割后4分之一图片速度，但准确率很高，并且识别出文字
    image1 ,image2,image3,image4 =preprocess_image(image_path)
    result = image_easyocr(image1)
    # 绘制图像并标出文本位置
    for (bbox, text, prob) in result:
        # bbox 是一个四点坐标，标出文本位置
        top_left, top_right, bottom_right, bottom_left = bbox
        top_left = tuple(map(int, top_left))
        bottom_right = tuple(map(int, bottom_right))
        print(top_left)
        print(bottom_right)
        print(text)
    # image_easyocr(image2)
    # image_easyocr(image3)
    # image_easyocr(image4)
