import math
import os.path
import time
import cv2
import numpy as np  # 导入 numpy 库
from PIL import Image
from paddleocr import PaddleOCR
from platform_func.android_comfunc import AndroidComfuc
# from ocr_image2txt.image_easyocr import image_easyocr
from ocr_image2txt.image_EAST import image_EAST
from ocr_image2txt.image_paddleocr import image_to_paddleocr_det, image_to_paddleocr_rec


# 处理 bounding box 和缩放坐标的逻辑
def process_boxes(boxes, rW, rH, tmp_list):
    for (startX, startY, endX, endY) in boxes:
        # scale the bounding box coordinates based on the respective ratios
        startX = int(startX * rW)
        startY = int(startY * rH)
        endX = int(endX * rW)
        endY = int(endY * rH)
        data_tuple = (startX, startY, endX, endY)
        tmp_list.append(data_tuple)


# 计算两个坐标点间的距离
def calculate_distance(point1, point2):
    x1, y1 = point1
    x2, y2 = point2
    distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    return distance


# 计算
def calculate_center(coordinate):
    center = [(int(coordinate[0]) + int(coordinate[2])) // 2,
              int(coordinate[3]) + int(coordinate[3] - coordinate[1])]
    return center


class AndroidControl():
    # adb命令输入封装
    def __init__(self, sn):
        self.image = (os.path.join(os.path.dirname(__file__), "screenshot.png"))
        self.comfunc = AndroidComfuc(sn, self.image)

        # Ocr检测模型加载
        self.net = None
        self.ocr = None
        self.init_model()

        # main主界面裁剪区域
        self.center = None
        self.search_coordinates_value1 = 200
        self.search_coordinates_value2 = 370
        self.search_coordinates_value3 = 25

        # 选择目标裁剪区域
        self.trooplist_value1 = 875
        self.trooplist_value2 = 100
        self.trooplist_value3 = 955
        self.trooplist_value4 = 320

    # 初始化ocr算法检测模型
    def init_model(self):
        print("loading text detector...")
        # 模型路径
        model_path = (os.path.join(os.path.dirname(__file__), "ocr_image2txt\\frozen_east_text_detection.pb"))
        # 加载预训练的 EAST 文本检测器
        self.net = cv2.dnn.readNet(model_path)
        self.ocr = PaddleOCR(lang='ch')

    # 自定义裁剪范围区域，每个区域检测的含义不同
    def init_range(self):
        self.comfunc.screenshot()
        image = Image.open(self.image)
        width, height = image.size
        self.center = [width // 2, height // 2]

        search_box = (
        self.search_coordinates_value1, 0, self.search_coordinates_value2, self.search_coordinates_value3)  # 搜索栏
        search_image = image.crop(search_box)

        troop_list_box = (
        self.trooplist_value1, self.trooplist_value2, self.trooplist_value3, self.trooplist_value4)  # 队列信息
        troop_list_image = image.crop(troop_list_box)

        return image, search_image, troop_list_image

    # 判断队列是否已满
    def troop_list(self, troop_list_image=None):
        if troop_list_image == None:
            main_image, troop_list_image = self.init_range()
        result = self.image2ocr(troop_list_image, "PaddleOCR")
        if result == None:
            return False
        elif int(result[0][1][0].split("/")[0]) < int(result[0][1][0].split("/")[1]):
            return False
        else:
            return True

    # ocr图片文字检测
    def image2ocr(self, image, type_ocr="EAST"):
        width, height = image.size
        # 转换为 NumPy 数组
        image_np = np.array(image)
        # 确保图像为 3 通道（BGR）
        if image_np.shape[2] == 4:  # 如果是 RGBA 则转换为 BGR
            image = cv2.cvtColor(image_np, cv2.COLOR_RGBA2BGR)

        if type_ocr == "EAST":
            # EAST模型
            # 0.601391 seconds，识别整张图片，速度很快，准确率较高，需要调整输入参数，参数影响很大，不识别文字
            boxes, rW, rH = image_EAST(image, _net=self.net, _width=width // 32 * 32, _height=height // 32 * 32,
                                       _confidence=0.9, isdbug=False)
            return boxes, rW, rH
        # elif type_ocr == "Easyocr":
        #     # Easyocr模型
        #     # 0.9544482231140137 seconds 切割后4分之一图片速度，但准确率很高，并且识别出文字
        #     image1, image2, image3, image4 = preprocess_image(image_path)
        #     result = image_easyocr(image1)
        #     # 绘制图像并标出文本位置
        #     for (bbox, text, prob) in result:
        #         # bbox 是一个四点坐标，标出文本位置
        #         top_left, top_right, bottom_right, bottom_left = bbox
        #         top_left = tuple(map(int, top_left))
        #         bottom_right = tuple(map(int, bottom_right))
        #         print(top_left)
        #         print(bottom_right)
        #         print(text)
        # image_easyocr(image2)
        # image_easyocr(image3)
        # image_easyocr(image4)
        else:
            # PaddleOCR
            # 0.5096032619476318 seconds，可以选择检测和识别，对于标准文本具有很高的识别准确率，但对于复杂环境识别效果一般
            result = image_to_paddleocr_rec(image, _ocr=self.ocr, isdbug=False)
            return result

    def detect(self, i):
        end_up = [self.center[0], self.center[1]*2]
        end_down = [self.center[0], 102]
        end_left = [self.center[0]*2, self.center[1]]
        end_right = [0, self.center[1]]
        step_length = math.ceil(i / 2)
        direction = i % 4
        # for i in range(1,20):
        #     self.comfunc.swipe(self.center, end_left)
        #     time.sleep(3)
        # for i in range(1,20):
        #     self.comfunc.swipe(self.center, end_right)
        #     time.sleep(3)
        if direction == 1:
            print("up: %s"%step_length)
            for i in range(0, step_length):
                self.comfunc.swipe(self.center, end_up)
                time.sleep(3)
        elif direction == 2:
            print("right: %s" % step_length)
            for i in range(0, step_length):
                self.comfunc.swipe(self.center, end_right)
                time.sleep(3)
        elif direction == 3:
            print("end: %s" % step_length)
            for i in range(0, step_length):
                self.comfunc.swipe(self.center, end_down)
                time.sleep(3)
        elif direction == 0:
            print("left: %s" % step_length)
            for i in range(0, step_length):
                self.comfunc.swipe(self.center, end_left)
                time.sleep(3)

    # http://kvkbvrcwzyunwffannbe.supabase.co/storage/v1/object/public/chrome
    def Gem_digging(self):
        # 坐标回源点

        # -----------------循环动作------------------
        image, search_image, troop_list_image = self.init_range()
        if self.troop_list(troop_list_image):
            return
        # 缩放图像
        self.comfunc.resized()
        # 截图检测，滑动屏幕，再截图检测，返回检测到的坐标
        time.sleep(1)
        # self.detect()
        # 拿到坐标,点击坐标,识别坐标,点击运作

        # -------------------------------------


if __name__ == '__main__':
    test = AndroidControl("emulator-5554")
    # test.Gem_digging()
    test.init_range()
    # print(test.center)
    # test.detect(10)

    for i in range(1, 1000):
        test.detect(i)
# ^.*?->
# ^
# $