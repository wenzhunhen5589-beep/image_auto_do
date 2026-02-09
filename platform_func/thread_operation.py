import threading

class SharedVar:
    def __init__(self, shared_var):
        self._shared_var = shared_var  # 共享变量
        self._lock = threading.Lock()  # 创建一个锁

    def append(self, item):
        """向共享列表添加元素，确保线程安全"""
        with self._lock:
            if item not in self._shared_var:
                self._shared_var.append(item)
                print(f"shared_list append: {self._shared_var}")

    def remove(self, item):
        """从共享列表移除元素，确保线程安全"""
        with self._lock:
            if item in self._shared_var:
                self._shared_var.remove(item)
                print(f"shared_list remove: {self._shared_var}")

    def get_list(self):
        """获取共享列表的副本，确保线程安全"""
        with self._lock:
            return self._shared_var.copy()  # 返回列表的副本以避免外部修改