import os
import random
import subprocess
import time
from PIL import Image


class AndroidComfuc:
    # adb命令输入封装
    def __init__(self, sn, image=(os.path.join(os.path.dirname(__file__), "screenshot.png"))):
        self.sn = sn
        self.image = image

    def shell(self, command, type=0, _timeout=600):
        try:
            res = subprocess.Popen("adb -s %s %s" % (self.sn, command), shell=True,
                                   stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            result = res.communicate(timeout=_timeout)
        except:
            return _timeout
        if type == 0:
            return result[0].decode('UTF-8', 'ignore').strip()
        return result

    def input_keyevent(self, keyworkds):
        self.shell("shell input keyevent %s" % keyworkds)

    def click(self, point):
        x = int(point[0])
        y = int(point[1])
        self.shell("shell input tap %s %s" % (x, y))

    def swipe(self, start, end):
        swipe_time = random.randint(200, 500)
        self.shell(
            "shell input swipe %s %s %s %s %s" % (int(start[0]), int(start[1]), int(end[0]), int(end[1]), swipe_time))

    # 手机截图导出
    def screenshot(self):
        self.shell("exec-out screencap -p > %s" % self.image)

    def get_center_pos(self):
        self.screenshot()
        image = Image.open(self.image)
        width, height = image.size
        # result = self.shell("shell wm size")
        # width, height = result.
        center_coordinate = [width / 2, height / 2]
        return center_coordinate

    # 校准模式
    def alignment_mode(self):
        self.ratio = 1
        center_pos = self.get_center_pos()

        step_size = 100
        while True:  # 判断鼠标是否在边缘，或找不到鼠标位置
            self.swipe(center_pos, [center_pos[0], center_pos[1] + step_size])


if __name__ == '__main__':
    test = AndroidComfuc("emulator-5554")
    test.input_keyevent(21)

