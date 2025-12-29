import math
import os.path
import subprocess
import time
import cv2
import numpy as np  # 导入 numpy 库
from PIL import Image
from paddleocr import PaddleOCR
from android_comfunc import AndroidComfuc
# from ocr_image2txt.image_easyocr import image_easyocr
from ocr_image2txt.image_EAST import image_EAST
from ocr_image2txt.image_paddleocr import image_to_paddleocr_det

NO_SELECT = 0
ON_SELECT = 1
TO_SELECT = 2
TO_SELECT_TIMES = 0

# 绕过物品

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
        self.pre_state = NO_SELECT

        # Ocr检测模型加载
        self.net = None
        self.ocr = None
        self.init_model()

        # self.init_range()
        self.center = None
        self.h_value1 = 130
        self.h_value2 = 70

        self.select_value1 = 585
        self.select_value2 = 50
        self.select_value3 = 380

        self.w_key = 220
        self.h_key = 520

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
        self.center = (width // 2, height // 2)

        main_box = (0, self.h_value1, width, height - self.h_value2)  # 主画面
        main_image = image.crop(main_box)

        is_select_box = (self.select_value3, 0, self.select_value1, self.select_value2)  # 选中目标区域
        is_select_image = image.crop(is_select_box)

        return main_image, is_select_image

    # 判断是否选中目标
    def is_select(self, is_select_image=None):
        if is_select_image == None:
            main_image, is_select_image = self.init_range()
        # self.image2ocr(is_select_image, "EAST")
        result = self.image2ocr(is_select_image, "PaddleOCR")
        if result == None:
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
            result = image_to_paddleocr_det(image, _ocr=self.ocr, isdbug=False)
            return result

    def extract_boxes(self, main_image):
        width, height = main_image.size
        tmp_list = []

        middle_box = (width // 3 - 40, 0, width // 3 * 2, height)  # 中——主画面
        middle_image = main_image.crop(middle_box)
        boxes, rW, rH = self.image2ocr(middle_image, "EAST")
        offset = (width // 3 - 40, 0)
        # 尝试从左边、右边提取 box
        if len(boxes) == 0:
            left_box = (0, 0, width // 3, height)  # 左边——主画面
            left_image = main_image.crop(left_box)
            boxes, rW, rH = self.image2ocr(left_image, "EAST")
            offset = (0, 0)
            if len(boxes) == 0:
                right_box = (width // 3 * 2 - 40, 0, width, height)  # 右边——主画面
                right_image = main_image.crop(right_box)
                boxes, rW, rH = self.image2ocr(right_image, "EAST")
                offset = (width // 3 * 2 - 40, 0)
                if len(boxes) == 0:
                    return tmp_list, offset
        # 如果 boxes 不为空，则直接使用
        if len(boxes) > 0:
            process_boxes(boxes, rW, rH, tmp_list)
        return tmp_list, offset

    # 按距离排列获取的结果点
    def order_result(self, result, offset=(0, 0)):
        tmp_point = None
        tmp_distance = 999
        offset = (offset[0], offset[1] + self.h_value1)
        for point in result:
            center = calculate_center(point)
            # print("center")
            # print(center)
            center = (center[0] + offset[0], center[1] + offset[1])
            distance = calculate_distance(center, self.center)
            if distance < tmp_distance:
                tmp_point = center
                tmp_distance = distance
        # print("tmp_point")
        # print(tmp_point)
        return tmp_point

    # 截屏 --- 目标已选中 --- 攻击             5s
    #         目标未选中 --- 扫描选目标        5s
    def attack(self):
        start_time = time.time()
        main_image, is_select_image = self.init_range()
        print("已截屏")
        if self.is_select(is_select_image):
            print("当前状态：目标已选中")
            self.pre_state = ON_SELECT
            # self.comfunc.input_keyevent(8)  # 按键1
            target = [self.w_key, self.h_key]
            self.comfunc.click(target) #点击技能图标
            time.sleep(0.5)
            target = [285, self.h_key]
            self.comfunc.click(target)  # 点击空白

        elif self.pre_state == TO_SELECT:
            print("当前状态：目标未选中成功")
            self.pre_state = NO_SELECT
            self.comfunc.input_keyevent(47) #s 键，停止移动

        elif self.pre_state == ON_SELECT:
            # 拾取物品
            print("当前状态：拾取物品")
            self.pre_state = NO_SELECT
            for i in range(3):
                self.comfunc.click([460,520])
                time.sleep(0.5)

        elif self.pre_state == NO_SELECT:
            global TO_SELECT_TIMES  # 声明 counter 为全局变量
            tmp_list, offset = self.extract_boxes(main_image)  # 扫描主界面，是否存在目标
            if len(tmp_list) == 0:
                print("当前状态：未扫描到目标,转移视角")
                self.pre_state = NO_SELECT
                # adb_long_press('21', duration=3)  # 长按3秒返回键
                start = [480,270]
                end = [720,270]
                self.comfunc.swipe(start, end)
            else:
                print("当前状态：点击目标，攻击目标")
                self.pre_state = TO_SELECT
                TO_SELECT_TIMES += 1
                if TO_SELECT_TIMES > 5:
                    get_away = [0,0] #点击边界点，逃离无法选中的目标
                    self.comfunc.click(get_away)
                    self.comfunc.input_keyevent(62) #空格，跳跃
                    TO_SELECT_TIMES = 0
                target = self.order_result(tmp_list, offset)
                self.comfunc.click(target)

                # end_time = time.time()
                # # 计算执行时间
                # execution_time = end_time - start_time
                # print(f"Attack Function execution time: {execution_time} seconds")

if __name__ == '__main__':
    # adb_long_press('21', duration=3)  # 长按3秒返回键
    test = AndroidControl("emulator-5554")

    while True:
        test.attack()
        time.sleep(1)
