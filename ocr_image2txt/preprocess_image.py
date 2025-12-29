import cv2
import numpy as np  # 导入 numpy 库
from PIL import Image

# 裁剪图片，输入 PIL 图片对象，元组（tuple）
def crop_image(image, box):
    return image.crop(box)

# 图片预处理，输入图片路径，输出
def preprocess_image(img_path):
    # 1.打开图片
    image_path = img_path
    image = Image.open(image_path)
    # 获取图片的尺寸
    width, height = image.size

    # 2.转换为单通道灰度图
    image = image.convert("L")

    # 3.切割图片
    # 计算切割点
    mid_width = width // 2
    mid_height = height // 2
    # 定义四个切割区域（左上，右上，左下，右下）
    box1 = (0, 0, mid_width, mid_height)  # 左上
    box2 = (mid_width, 0, width, mid_height)  # 右上
    box3 = (0, mid_height, mid_width, height)  # 左下
    box4 = (mid_width, mid_height, width, height)  # 右下
    image1 = crop_image(image, box1)
    image2 = crop_image(image, box2)
    image3 = crop_image(image, box3)
    image4 = crop_image(image, box4)

    # 4. 转为 NumPy 数组，方便 OpenCV 处理
    gray_np1 = np.array(image1)
    gray_np2 = np.array(image2)
    gray_np3 = np.array(image3)
    gray_np4 = np.array(image4)

    # 5. 调整图像分辨率 (缩放)
    resize_coefficient = 0.8
    resized1 = cv2.resize(gray_np1, (int(mid_width * resize_coefficient), int(mid_height * resize_coefficient)),
                          interpolation=cv2.INTER_LINEAR)
    resized2 = cv2.resize(gray_np2, (int(mid_width * resize_coefficient), int(mid_height * resize_coefficient)),
                          interpolation=cv2.INTER_LINEAR)
    resized3 = cv2.resize(gray_np3, (int(mid_width * resize_coefficient), int(mid_height * resize_coefficient)),
                          interpolation=cv2.INTER_LINEAR)
    resized4 = cv2.resize(gray_np4, (int(mid_width * resize_coefficient), int(mid_height * resize_coefficient)),
                          interpolation=cv2.INTER_LINEAR)

    # 6. 去噪处理
    # 使用 OpenCV 的高斯模糊或中值滤波
    # 高斯模糊
    # denoised = cv2.GaussianBlur(resized, (5, 5), 0)
    # 或者中值滤波
    # denoised = cv2.medianBlur(gray_np, 5)

    # 7. 转回 Pillow 图像，方便保存或显示
    # image1 = Image.fromarray(resized1)
    # image2 = Image.fromarray(resized2)
    # image3 = Image.fromarray(resized3)
    # image4 = Image.fromarray(resized4)

    # # 保存切割后的图片
    # image.save('image1.jpg')

    # # 如果需要显示这些图片
    # image1.show()
    # image2.show()
    # image3.show()
    # image4.show()

    image1 = resized1
    image2 = resized2
    image3 = resized3
    image4 = resized4
    return image1, image2, image3, image4
