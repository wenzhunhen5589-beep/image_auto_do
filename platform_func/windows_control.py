import math
import os.path
import time
import cv2
import numpy as np
import win32api
import win32con
import win32gui
import win32ui
from PIL import Image
from PyQt5.QtWidgets import QApplication
from numpy import array, uint8, ndarray
from time import sleep
import matplotlib.pyplot as plt


def get_handle(cl_name, wd_name):
    hd_sub_wd_target = win32gui.FindWindow(cl_name, wd_name)
    # print(hd_sub_wd_target)
    hd_sub_wd_target = win32gui.FindWindowEx(hd_sub_wd_target, None, None, None)
    return hd_sub_wd_target


# 窗口截图
class WindowCapture:
    w = 0
    h = 0
    hwnd = None

    def __init__(self, window_name):
        self.hwnd = win32gui.FindWindow(None, window_name)
        if not self.hwnd:
            raise Exception('Window not found: {}'.format(window_name))

        window_rect = win32gui.GetWindowRect(self.hwnd)
        self.w = window_rect[2] - window_rect[0]
        self.h = window_rect[3] - window_rect[1]

        border_pixels = 8
        titlebar_pixels = 30
        self.w = self.w - (border_pixels * 2)
        self.h = self.h - titlebar_pixels - border_pixels
        self.cropped_x = border_pixels
        self.cropped_y = titlebar_pixels

    # 注意后台窗口不能最小化,返回句柄窗口的设备环境，覆盖整个窗口，包括非客户区，标题栏，菜单，边框
    def screenshot_DC(self):
        hwndDC = win32gui.GetWindowDC(self.hwnd)
        mfcDC = win32ui.CreateDCFromHandle(hwndDC)
        saveDC = mfcDC.CreateCompatibleDC()
        saveBitMap = win32ui.CreateBitmap()
        rctA = win32gui.GetWindowRect(self.hwnd)
        w = rctA[2] - rctA[0]
        h = rctA[3] - rctA[1]
        saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)
        saveDC.SelectObject(saveBitMap)
        saveDC.BitBlt((0, 0), (w, h), mfcDC, (0, 0), win32con.SRCCOPY)
        signedIntsArray = saveBitMap.GetBitmapBits(True)
        img = np.frombuffer(signedIntsArray, dtype="uint8")
        img.shape = (h, w, 4)
        win32gui.DeleteObject(saveBitMap.GetHandle())
        mfcDC.DeleteDC()
        saveDC.DeleteDC()
        # 显示图像
        img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)
        # 保存图片
        cv2.imwrite(os.path.join(os.path.dirname(__file__), "screenshot_dc.jpg"), cv2.cvtColor(img, cv2.COLOR_RGBA2BGR))
        # plt.imshow(img)
        # plt.axis('off')  # 关闭坐标轴
        # plt.show()  # 显示图像

        return img

    # 只截屏游戏内容，不包括边框和状态栏，使用PIL的ImageGrab模块,输出结果为4.015秒，也就是说截取一次屏幕需要半秒钟
    def screenshot_IG(self, savename='') -> ndarray:
        '截图方法，在窗口为 1920 x 1080 大小下，最快速度25ms (grabWindow: 17ms, to_cvimg: 8ms)'

        def to_cvimg(pix):
            '将self.screen.grabWindow 返回的 Pixmap 转换为 ndarray，方便opencv使用'
            qimg = pix.toImage()
            temp_shape = (qimg.height(), qimg.bytesPerLine() * 8 // qimg.depth())
            temp_shape += (4,)
            ptr = qimg.bits()
            ptr.setsize(qimg.byteCount())
            result = array(ptr, dtype=uint8).reshape(temp_shape)
            return result[..., :3]

        pix = QApplication.primaryScreen().grabWindow(self.hwnd)
        img = to_cvimg(pix)
        # 保存图片
        # if savename: self.pix.save(savename)
        return img

    def get_screenshot(self):
        wDC = win32gui.GetWindowDC(self.hwnd)
        dcObj = win32ui.CreateDCFromHandle(wDC)
        cDC = dcObj.CreateCompatibleDC()
        dataBitMap = win32ui.CreateBitmap()
        dataBitMap.CreateCompatibleBitmap(dcObj, self.w, self.h)
        cDC.SelectObject(dataBitMap)
        cDC.BitBlt((0, 0), (self.w, self.h), dcObj, (self.cropped_x, self.cropped_y), win32con.SRCCOPY)

        signedIntsArray = dataBitMap.GetBitmapBits(True)
        img = np.fromstring(signedIntsArray, dtype='uint8')
        img.shape = (self.h, self.w, 4)

        dcObj.DeleteDC()
        cDC.DeleteDC()
        win32gui.ReleaseDC(self.hwnd, wDC)
        win32gui.DeleteObject(dataBitMap.GetHandle())

        img = img[..., :3]
        img = np.ascontiguousarray(img)

        # 显示图像
        # plt.imshow(img)
        # plt.axis('off')  # 关闭坐标轴
        # plt.show()  # 显示图像

        return img

    def generate_image_dataset(self):
        if not os.path.exists("images"):
            os.mkdir("images")
        while (True):
            img = self.get_screenshot()
            im = Image.fromarray(img[..., [2, 1, 0]])
            im.save(f"./images/img_{len(os.listdir('images'))}.jpeg")
            sleep(1)

    def get_window_size(self):
        return (self.w, self.h)


class WindowsComfunc:
    # adb命令输入封装
    def __init__(self, window_name):
        self.hwnd = win32gui.FindWindow(None, window_name)
        if not self.hwnd:
            raise Exception('Window not found: {}'.format(window_name))

    # 设置窗口大小及位置
    def set_size_location(self, x=0, y=0, w=800, h=600):
        win32gui.SetWindowPos(self.hwnd, win32con.HWND_TOP, x, y, w, h, win32con.SWP_NOSIZE)

    # 获取窗口大小及位置 758,1014
    def get_size_location(self):
        return win32gui.GetWindowRect(self.hwnd)

    # 前台，鼠标右键双击
    def right_double_click(self, x, y):
        win32gui.SetForegroundWindow(self.hwnd)  # 激活窗口至前端(这行语句不能少)
        time.sleep(1)

        window_rect = win32gui.GetWindowRect(self.hwnd)
        window_x = window_rect[0]
        window_y = window_rect[1]

        win32api.SetCursorPos(window_x + x, window_y + y)

        time.sleep(1)
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, 0, 0)
        time.sleep(0.01)
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0)
        time.sleep(0.01)
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, 0, 0)
        time.sleep(0.01)
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0)

    # 前台，鼠标左键双击
    def left_double_click(self, x, y):
        # win32gui.SetForegroundWindow(hwnd)  # 激活窗口至前端(这行语句不能少)
        # time.sleep(1)

        window_rect = win32gui.GetWindowRect(self.hwnd)
        window_x = window_rect[0]
        window_y = window_rect[1]

        win32api.SetCursorPos([int(window_x + x), int(window_y + y)])
        time.sleep(0.5)

        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
        time.sleep(0.01)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
        time.sleep(0.1)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
        time.sleep(0.01)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
        time.sleep(1)

    # 前台，鼠标左键单击
    def left_click(self, x, y, click_times=1):
        # win32gui.SetForegroundWindow(hwnd)  # 激活窗口至前端(这行语句不能少)
        # time.sleep(1)
        window_rect = win32gui.GetWindowRect(self.hwnd)
        window_x = window_rect[0]
        window_y = window_rect[1]

        win32api.SetCursorPos([int(window_x + x), int(window_y + y)])
        for i in range(click_times):
            # 模拟鼠标左键按下
            time.sleep(0.5)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
            time.sleep(0.1)
            # 模拟鼠标左键放开
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
        time.sleep(1)

    # 前台，鼠标右键单击
    def right_click(self, x, y):
        # win32gui.SetForegroundWindow(hwnd)  # 激活窗口至前端(这行语句不能少)
        # time.sleep(1)
        window_rect = win32gui.GetWindowRect(self.hwnd)
        window_x = window_rect[0]
        window_y = window_rect[1]

        win32api.SetCursorPos([int(window_x + x), int(window_y + y)])
        time.sleep(0.5)
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, 0, 0)
        time.sleep(0.1)
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0)

    # 前台，数字数值输入
    def enter_code(self, numbers):
        for number in numbers:
            virtual_key_code = ord(number.upper())  # 使用 ord() 获取字符的 ASCII 值
            # 发送按键消息
            win32api.keybd_event(virtual_key_code, 0, 0, 0)  # 模拟按下按键
            time.sleep(0.2)  # 可以根据需要调整输入字符之间的时间间隔
            win32api.keybd_event(virtual_key_code, 0, win32con.KEYEVENTF_KEYUP, 0)  # 模拟释放按键
        time.sleep(0.5)

    # 后台，按键  0 - 0x30
    def send_key(self, key):
        win32gui.SendMessage(self.hwnd, win32con.WM_KEYDOWN, key, 0)
        time.sleep(0.5)
        win32gui.SendMessage(self.hwnd, win32con.WM_KEYUP, key, 1)

    def click(self, x, y, button='left'):
        """
        模拟鼠标点击操作。

        :param x: 点击的x坐标
        :param y: 点击的y坐标
        :param button: 'left' 或 'right' 表示左键或右键
        """
        if button == 'left':
            down_msg = win32con.WM_LBUTTONDOWN
            up_msg = win32con.WM_LBUTTONUP
        elif button == 'right':
            down_msg = win32con.WM_RBUTTONDOWN
            up_msg = win32con.WM_RBUTTONUP
        else:
            raise ValueError("Invalid button specified. Use 'left' or 'right'.")

        win32gui.SendMessage(self.hwnd, down_msg, win32con.MK_LBUTTON, win32api.MAKELONG(x, y))
        time.sleep(0.1)  # 短暂延时
        win32gui.SendMessage(self.hwnd, up_msg, win32con.MK_LBUTTON, win32api.MAKELONG(x, y))

    def mouse_wheel_scroll(self, delta):
        """
        模拟鼠标滚轮操作。

        :param delta: 正值表示向上滚动，负值表示向下滚动。
        """
        win32gui.SendMessage(self.hwnd, win32con.WM_MOUSEWHEEL, delta, 0)

    def send_key(self, key):
        """
        模拟键盘按键操作。

        :param key: 要发送的虚拟键码
        """
        win32gui.SendMessage(self.hwnd, win32con.WM_KEYDOWN, key, 0)
        time.sleep(0.1)  # 短暂延时
        win32gui.SendMessage(self.hwnd, win32con.WM_KEYUP, key, 1)

    def send_combination(self, keys):
        """
        模拟组合键操作。

        :param keys: 一个包含虚拟键码的列表
        """
        # 按下所有组合键
        for key in keys:
            win32gui.SendMessage(self.hwnd, win32con.WM_KEYDOWN, key, 0)

        time.sleep(0.1)  # 短暂延时

        # 释放所有组合键
        for key in keys:
            win32gui.SendMessage(self.hwnd, win32con.WM_KEYUP, key, 0)


if __name__ == '__main__':
    window_name = "雷电模拟器"

    # wincap = WindowCapture(window_name)
    # wincap.screenshot_DC()
    time.sleep(3)
    winfunc = WindowsComfunc(window_name)
    winfunc.mouse_wheel_scroll(100)
    # winfunc.click(10,10)
