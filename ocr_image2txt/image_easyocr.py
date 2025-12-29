import time
import easyocr #version 1.7.2
import cv2
import matplotlib.pyplot as plt
import numpy as np  # 导入 numpy 库1.23.0

# return 扫描结果，为三元组数组(bbox, text, prob) in result
def image_easyocr(image_path, isdbug=False):
    # 创建 easyocr Reader 对象
    reader = easyocr.Reader(['ch_sim'], gpu=True)  # 只识别英文，如果需要识别其他语言，可以传入 ['en', 'ch', 'fr'] 等
    start_time = time.time()
    # 使用 easyocr 进行文字位置检测
    result = reader.readtext(image_path, text_threshold = 0.7, low_text = 0.4, detail=1)  # detail=1 表示返回边界框和文本内容
    end_time = time.time()
    # 计算执行时间
    execution_time = end_time - start_time
    print(f"Function execution time: {execution_time} seconds")

    if isdbug:
        # 绘制图像并标出文本位置
        for (bbox, text, prob) in result:
            # bbox 是一个四点坐标，标出文本位置
            top_left, top_right, bottom_right, bottom_left = bbox
            top_left = tuple(map(int, top_left))
            bottom_right = tuple(map(int, bottom_right))
            # 画出矩形框
            cv2.rectangle(image_path, top_left, bottom_right, (0, 255, 0), 2)

        # 显示图片
        plt.imshow(cv2.cvtColor(image_path, cv2.COLOR_BGR2RGB))
        plt.axis('off')
        plt.show()
    return result


    return result

# debug图片检测，结果显示框图
def easyoc_debug(image_path):
    # 创建 easyocr Reader 对象
    reader = easyocr.Reader(['ch_sim'], gpu=True)  # 只识别英文，如果需要识别其他语言，可以传入 ['en', 'ch', 'fr'] 等
    start_time = time.time()

    # 加载图片
    # 输入image_path为图片路径
    # image = cv2.imread(image_path)

    # 输入image_path为PIL对象，将 PIL 图像转换为 numpy 数组
    # image_path = np.array(image_path)

    # 输入image_path为numpy 数组
    image = image_path

    # 使用 easyocr 进行文字位置检测
    result = reader.readtext(image_path, text_threshold = 0.7, low_text = 0.4, detail=1)  # detail=1 表示返回边界框和文本内容

    # 绘制图像并标出文本位置
    for (bbox, text, prob) in result:
        # bbox 是一个四点坐标，标出文本位置
        top_left, top_right, bottom_right, bottom_left = bbox
        top_left = tuple(map(int, top_left))
        bottom_right = tuple(map(int, bottom_right))
        # 画出矩形框
        cv2.rectangle(image, top_left, bottom_right, (0, 255, 0), 2)

    end_time = time.time()
    # 计算执行时间
    execution_time = end_time - start_time
    print(f"Function execution time: {execution_time} seconds")

    # 显示图片
    plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    plt.axis('off')
    plt.show()