import cv2
import ddddocr
import matplotlib.pyplot as plt

# 准确率很低
det = ddddocr.DdddOcr(det=True)
image_path = 'test2.png'

# 识别
with open(image_path, 'rb') as f:
    image = f.read()
bboxes = det.detection(image)

# 画图，显示识别结果
im = cv2.imread(image_path)
for bbox in bboxes:
    x1, y1, x2, y2 = bbox
    cv2.rectangle(im, (x1, y1), (x2, y2), color=(0, 0, 255), thickness=2)
# 显示图片
plt.imshow(cv2.cvtColor(im, cv2.COLOR_BGR2RGB))
plt.axis('off')
plt.show()