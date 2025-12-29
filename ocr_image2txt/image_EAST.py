import time
import cv2
import numpy as np
from imutils.object_detection import non_max_suppression


def image_EAST(imagepath,_net=None , _width=1280, _height=640, _confidence=0.8, isdbug=False):
    # 加载输入图像并获取图像尺寸
    # image = cv2.imread(imagepath)

    if _net == None:
        # 模型路径
        modelpath = "frozen_east_text_detection.pb"
        # 加载预训练的 EAST 文本检测器
        print("[image_EAST] loading EAST text detector...")
        net = cv2.dnn.readNet(modelpath)
    else:
        net = _net

    image = imagepath
    orig = image.copy()
    # 输入网络的图片尺寸（必须为32的倍数）
    width = _width
    height = _height
    # 设置新的宽度和高度
    (newW, newH) = (width, height)
    # 记录原图像大小与缩小后的比值，得到预测结果后需要乘上这个缩放因子
    (H, W) = image.shape[:2]
    rW = W / float(newW)
    rH = H / float(newH)
    # 调整图像大小并获取新的图像尺寸
    image = cv2.resize(image, (newW, newH))
    (H, W) = image.shape[:2]
    start = time.time()
    # 从图像中构建一个 blob，然后执行模型的前向传播以获得两个输出层集合
    blob = cv2.dnn.blobFromImage(image, 1.0, (W, H),
                                 (123.68, 116.78, 103.94), swapRB=True, crop=False)
    net.setInput(blob)
    # 定义EAST检测器模型的两个输出层名称
    # 第一个是输出概率,置信度
    # 第二个可用于导出文本的边界框坐标
    layerNames = [
        "feature_fusion/Conv_7/Sigmoid",
        "feature_fusion/concat_3"]
    (scores, geometry) = net.forward(layerNames)
    end = time.time()

    # show timing information on text prediction

    # grab the number of rows and columns from the scores volume, then
    # initialize our set of bounding box rectangles and corresponding
    # confidence scores
    (numRows, numCols) = scores.shape[2:4]
    rects = []
    confidences = []

    # loop over the number of rows
    for y in range(0, numRows):
        # extract the scores (probabilities), followed by the geometrical
        # data used to derive potential bounding box coordinates that
        # surround text
        scoresData = scores[0, 0, y]
        xData0 = geometry[0, 0, y]
        xData1 = geometry[0, 1, y]
        xData2 = geometry[0, 2, y]
        xData3 = geometry[0, 3, y]
        anglesData = geometry[0, 4, y]

        # loop over the number of columns
        for x in range(0, numCols):
            # if our score does not have sufficient probability, ignore it
            if scoresData[x] < _confidence:    # 最小置信度
                continue

            # compute the offset factor as our resulting feature maps will
            # be 4x smaller than the input image
            (offsetX, offsetY) = (x * 4.0, y * 4.0)

            # extract the rotation angle for the prediction and then
            # compute the sin and cosine
            angle = anglesData[x]
            cos = np.cos(angle)
            sin = np.sin(angle)

            # use the geometry volume to derive the width and height of
            # the bounding box
            h = xData0[x] + xData2[x]
            w = xData1[x] + xData3[x]

            # compute both the starting and ending (x, y)-coordinates for
            # the text prediction bounding box
            endX = int(offsetX + (cos * xData1[x]) + (sin * xData2[x]))
            endY = int(offsetY - (sin * xData1[x]) + (cos * xData2[x]))
            startX = int(endX - w)
            startY = int(endY - h)

            # add the bounding box coordinates and probability score to
            # our respective lists
            rects.append((startX, startY, endX, endY))
            confidences.append(scoresData[x])

    # apply non-maxima suppression to suppress weak, overlapping bounding
    # boxes
    boxes = non_max_suppression(np.array(rects), probs=confidences)

    if isdbug:
        print("[image_EAST] text detection took {:.6f} seconds".format(end - start))
        # loop over the bounding boxes
        for (startX, startY, endX, endY) in boxes:
            # scale the bounding box coordinates based on the respective
            # ratios
            startX = int(startX * rW)
            startY = int(startY * rH)
            endX = int(endX * rW)
            endY = int(endY * rH)

            # draw the bounding box on the image
            cv2.rectangle(orig, (startX, startY), (endX, endY), (0, 0, 255), 2)

        # show the output image
        cv2.imshow("Text Detection", orig)
        cv2.waitKey(0)

    return boxes,rW,rH



# debug模型调参模式，显示结果框图
def image_EAST_debug(imagepath, _width=1280, _height=640, _confidence=0.8):
    # 加载输入图像并获取图像尺寸
    image = cv2.imread(imagepath)
    # image = imagepath
    orig = image.copy()
    (H, W) = image.shape[:2]

    # 模型路径
    modelpath = "frozen_east_text_detection.pb"
    # 输入网络的图片尺寸（必须为8的倍数）
    # size_list = [160, 320, 640, 960, 1280]
    width = _width
    height = _height

    # 最小置信度
    min_confidence = _confidence

    # 设置新的宽度和高度
    (newW, newH) = (width, height)
    # 记录原图像大小与缩小后的比值，得到预测结果后需要乘上这个缩放因子
    rW = W / float(newW)
    rH = H / float(newH)

    # 调整图像大小并获取新的图像尺寸
    image = cv2.resize(image, (newW, newH))
    (H, W) = image.shape[:2]

    # 定义EAST检测器模型的两个输出层名称
    # 第一个是输出概率,置信度
    # 第二个可用于导出文本的边界框坐标
    layerNames = [
        "feature_fusion/Conv_7/Sigmoid",
        "feature_fusion/concat_3"]

    # 加载预训练的 EAST 文本检测器
    print("[INFO] loading EAST text detector...")
    net = cv2.dnn.readNet(modelpath)

    # 从图像中构建一个 blob，然后执行模型的前向传播以获得两个输出层集合
    blob = cv2.dnn.blobFromImage(image, 1.0, (W, H),
                                 (123.68, 116.78, 103.94), swapRB=True, crop=False)
    start = time.time()
    net.setInput(blob)
    (scores, geometry) = net.forward(layerNames)
    end = time.time()

    # show timing information on text prediction
    print("[INFO] text detection took {:.6f} seconds".format(end - start))

    # grab the number of rows and columns from the scores volume, then
    # initialize our set of bounding box rectangles and corresponding
    # confidence scores
    (numRows, numCols) = scores.shape[2:4]
    rects = []
    confidences = []

    # loop over the number of rows
    for y in range(0, numRows):
        # extract the scores (probabilities), followed by the geometrical
        # data used to derive potential bounding box coordinates that
        # surround text
        scoresData = scores[0, 0, y]
        xData0 = geometry[0, 0, y]
        xData1 = geometry[0, 1, y]
        xData2 = geometry[0, 2, y]
        xData3 = geometry[0, 3, y]
        anglesData = geometry[0, 4, y]

        # loop over the number of columns
        for x in range(0, numCols):
            # if our score does not have sufficient probability, ignore it
            if scoresData[x] < min_confidence:
                continue

            # compute the offset factor as our resulting feature maps will
            # be 4x smaller than the input image
            (offsetX, offsetY) = (x * 4.0, y * 4.0)

            # extract the rotation angle for the prediction and then
            # compute the sin and cosine
            angle = anglesData[x]
            cos = np.cos(angle)
            sin = np.sin(angle)

            # use the geometry volume to derive the width and height of
            # the bounding box
            h = xData0[x] + xData2[x]
            w = xData1[x] + xData3[x]

            # compute both the starting and ending (x, y)-coordinates for
            # the text prediction bounding box
            endX = int(offsetX + (cos * xData1[x]) + (sin * xData2[x]))
            endY = int(offsetY - (sin * xData1[x]) + (cos * xData2[x]))
            startX = int(endX - w)
            startY = int(endY - h)

            # add the bounding box coordinates and probability score to
            # our respective lists
            rects.append((startX, startY, endX, endY))
            confidences.append(scoresData[x])

    # apply non-maxima suppression to suppress weak, overlapping bounding
    # boxes
    boxes = non_max_suppression(np.array(rects), probs=confidences)

    # loop over the bounding boxes
    for (startX, startY, endX, endY) in boxes:
        # scale the bounding box coordinates based on the respective
        # ratios
        startX = int(startX * rW)
        startY = int(startY * rH)
        endX = int(endX * rW)
        endY = int(endY * rH)

        # draw the bounding box on the image
        cv2.rectangle(orig, (startX, startY), (endX, endY), (0, 0, 255), 2)

    # show the output image
    cv2.imshow("Text Detection", orig)
    cv2.waitKey(0)