import aircv, cv2


# 对比图片定位坐标，返回值为定位框中心坐标（x，y）
def matchImg(imsrc: object, imgobj: object, confidence: object = 0.6, type: object = 0) -> object:
    """
    图片对比识别imgobj在imgsrc上的相对位置（批量识别统一图片中需要的部分）
    :param imgsrc: 原始图片路径(str)
    :param imgobj: 待查找图片路径（模板）(str)
    :param confidence: 识别度（0<confidence<1.0）
    :return: None or dict({'confidence': 相似度(float), 'rectangle': 原始图片上的矩形坐标(tuple), 'result': 中心坐标(tuple)})
    """
    imsrc = aircv.imread(imsrc)
    imobj = aircv.imread(imgobj)
    match_result = aircv.find_template(imsrc, imobj, confidence)
    # print(match_result)
    if match_result is not None:
        if type == 0:
            return match_result['result']
        else:
            return match_result
    return None


def matchImgAll(imsrc: object, imgobj: object, confidence: object = 0.6) -> object:
    """
    图片对比识别imgobj在imgsrc上的相对位置（批量识别统一图片中需要的部分）
    :param imgsrc: 原始图片路径(str)
    :param imgobj: 待查找图片路径（模板）(str)
    :param confidence: 识别度（0<confidence<1.0）
    :return: None or dict({'confidence': 相似度(float), 'rectangle': 原始图片上的矩形坐标(tuple), 'result': 中心坐标(tuple)})
    """
    imsrc = aircv.imread(imsrc)
    imobj = aircv.imread(imgobj)
    match_result = aircv.find_all_template(imsrc, imobj, confidence)
    return match_result
    # print(len(match_result))
    # if match_result is not None:
    #     if type == 0:
    #         return match_result['result']
    #     else:
    #         return match_result
    # return None


# 对比图片定位坐标，可以显示定位图片
def matchImg2(imsrc, imgobj):
    # 加载目标图片和待匹配图片
    target_img = cv2.imread(imgobj, 0)
    matching_img = cv2.imread(imsrc, 0)

    # 使用模板匹配方法（TM_CCOEFF_NORMED）
    result = cv2.matchTemplate(matching_img, target_img, cv2.TM_CCOEFF_NORMED)

    # 获取匹配结果的坐标
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    top_left = max_loc
    bottom_right = (top_left[0] + target_img.shape[1], top_left[1] + target_img.shape[0])

    # 在原始图片上绘制矩形框标记目标位置
    matched_img = cv2.cvtColor(matching_img, cv2.COLOR_GRAY2BGR)
    cv2.rectangle(matched_img, top_left, bottom_right, (0, 255, 0), 2)
    print(top_left)
    print(bottom_right)
    # 显示结果图片
    cv2.imshow('Matched Image', matched_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
