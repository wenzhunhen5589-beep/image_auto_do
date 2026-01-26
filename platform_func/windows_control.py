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

    # 获取后台窗口的句柄，注意后台窗口不能最小化
    # 返回句柄窗口的设备环境，覆盖整个窗口，包括非客户区，标题栏，菜单，边框
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
        # 保存图片
        # cv2.imwrite(os.path.join(os.path.dirname(__file__), "screenshot.jpg"), cv2.cvtColor(img, cv2.COLOR_RGBA2RGB))
        return cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)

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


# 只截屏游戏内容，不包括边框和状态栏
# 使用PIL的ImageGrab模块,输出结果为4.015秒，也就是说截取一次屏幕需要半秒钟
class Screen:
    def __init__(self, win_title=None, win_class=None, hwnd=None) -> None:
        self.app = QApplication(['WindowCapture'])
        self.screen = QApplication.primaryScreen()
        self.bind(win_title, win_class, hwnd)

    def bind(self, win_title=None, win_class=None, hwnd=None):
        '可以直接传入句柄，否则就根据class和title来查找，并把句柄做为实例属性 self._hwnd'
        if not hwnd:
            self._hwnd = win32gui.FindWindow(win_class, win_title)
        else:
            self._hwnd = hwnd

    def capture(self, savename='') -> ndarray:
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

        self.pix = self.screen.grabWindow(self._hwnd)
        self.img = to_cvimg(self.pix)
        if savename: self.pix.save(savename)
        return self.img


class WindowsComfuc:
    # adb命令输入封装
    def __init__(self, handle):
        self.hwnd = handle
        self.image = (os.path.join(os.path.dirname(__file__), "screenshot.jpg"))

    def left_click(self, x, y):
        win32gui.SendMessage(self.hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, win32api.MAKELONG(x, y))
        time.sleep(0.3)
        win32gui.SendMessage(self.hwnd, win32con.WM_LBUTTONUP, win32con.MK_LBUTTON, win32api.MAKELONG(x, y))
        # 后台，按键  0 - 0x30

    def send_key(self, key):
        win32gui.SendMessage(self.hwnd, win32con.WM_KEYDOWN, key, 0)
        time.sleep(0.5)
        win32gui.SendMessage(self.hwnd, win32con.WM_KEYUP, key, 1)
        # Python调用windows API实现屏幕截图,输出结果为0.375秒，也就是说通过windows API每次截图只需要0.0375s

    def screenshot(self):
        screen = Screen(hwnd=self.hwnd)
        screen.capture(self.image)


def get_handle(cl_name, wd_name):
    hd_sub_wd_target = win32gui.FindWindow(cl_name, wd_name)
    # print(hd_sub_wd_target)
    hd_sub_wd_target = win32gui.FindWindowEx(hd_sub_wd_target, None, None, None)
    return hd_sub_wd_target


if __name__ == '__main__':
    window_name = "雷电模拟器"
    handle = get_handle(None, window_name)
    test = WindowsComfuc(handle)
    wincap = WindowCapture(window_name)

    alltime = 0
    for i in range(1000):
        time1 = time.time()
        # test.screenshot()  #exe time: 14.462355613708496
        wincap.screenshot1()  #exe time: 4.57158350944519
        # wincap.get_screenshot()   #exe time: 7.412857294082642
        time2 = time.time()
        exe_time = time2 - time1
        alltime = alltime + exe_time
    print(f"exe time: {alltime}")

    # test.screenshot1()

    # window_name = "雷电模拟器"
    # wincap = WindowCapture(window_name)
    # while (True):
    #     time1 = time.time()
    #     ss = wincap.get_screenshot()
    #     time2 = time.time()
    #     exe_time = time2 - time1
    #     print(f"exe time: {exe_time}")
