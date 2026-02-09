# Python + pyautogui
# 优点：跨平台、代码简洁。
# 缺点：依赖屏幕坐标和窗口焦点，无法操作后台窗口。
# 原理：
# PyAutoGUI 针对不同操作系统（Windows、macOS、Linux）使用底层系统 API 生成鼠标事件，确保跨平台兼容性：
# 	• Windows: 调用 user32.dll 中的 SendInput 或 mouse_event 函数。
# 	• macOS: 使用 Quartz 框架的 CGEventCreateMouseEvent 和 CGEventPost。
#   • Linux: 通过 Xlib/XTest 扩展（如 XTestFakeMotionEvent 和 XTestFakeButtonEvent）
import random
import time
import pyautogui

# 功能
# 1.鼠标控制
# pyautogui.moveTo(1100, 720, duration=1)移动并点击（带延迟）
# pyautogui.click()  此方法未点击只移动了鼠标
pyautogui.moveTo(1100, 720)
pyautogui.mouseDown()  # 按下鼠标
pyautogui.mouseUp()  # 松开鼠标

pyautogui.dragTo(300, 400, duration=0.5)  # 拖动到目标位置
pyautogui.drag(100, 0, duration=1)  # 相对拖动,向右拖动100px

pyautogui.scroll(10)  # 向上滚动10单位,不好用
pyautogui.scroll(-10)  # 向下滚动


# 添加随机延迟：在点击、移动操作中引入随机间隔
def human_click(x, y):
    pyautogui.moveTo(x, y, duration=random.uniform(0.2, 0.5))
    time.sleep(random.uniform(0.1, 0.3))
    pyautogui.click()


# 模拟自然移动：使用贝塞尔曲线或随机路径代替直线移动。
# 示例：随机偏移路径
def human_move(x, y):
    current_x, current_y = pyautogui.position()
    steps = 10
    for i in range(steps):
        offset_x = random.randint(-5, 5)
        offset_y = random.randint(-5, 5)
        target_x = current_x + (x - current_x) * (i / steps) + offset_x
        target_y = current_y + (y - current_y) * (i / steps) + offset_y
        pyautogui.moveTo(target_x, target_y, duration=0.01)


# 2.键盘控制
pyautogui.hotkey("ctrl", "c")  # 按下 Ctrl+C

pyautogui.press("enter")  # 按下回车

pyautogui.keyDown("shift")  # 按住 Shift
pyautogui.keyUp("shift")  # 松开 Shift

pyautogui.write("Hello World!", interval=0.1)  # 文本输入,间隔0.1秒输入
# 3.屏幕处理
screenshot = pyautogui.screenshot()  # 全屏截图
screenshot.save("screenshot.png")

region = pyautogui.screenshot(region=(0, 0, 300, 400))  # 区域截图 (x,y,width,height)
# 4.获取像素颜色
pixel_color = pyautogui.pixel(100, 200)
print(pixel_color)  # 输出 (R, G, B)
# 5.图像识别（定位元素）
# 在屏幕中查找图片位置
# confidence: 识别置信度（需安装 opencv-python）
# grayscale=True: 灰度匹配加速识别
location = pyautogui.locateOnScreen("button.png", confidence=0.8)
if location:
    x, y = pyautogui.center(location)
    pyautogui.click(x, y)
# 6.实用工具
# 检查分辨率
print("屏幕分辨率:", pyautogui.size())
# 获取鼠标当前位置
x, y = pyautogui.position()
print(f"当前坐标: ({x}, {y})")
# 延迟控制
pyautogui.PAUSE = 0.5  # 每个操作后暂停0.5秒
