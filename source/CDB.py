class CDB:
    def __init__(self):
        # 数据存储区，用于存储广播的数据
        # 使用字典来存储，键是数据的目标寄存器，值是对应的数据
        self.data = {}
        self.busy = False

    def broadcast(self, target, value):
        """
        广播数据到公共数据总线。
        :param target: 目标寄存器或保留站的名称。
        :param value: 要广播的数据值。
        """
        self.data[target] = value
        self.busy = True
        # print("CDB: ", target, value)

    def get_data(self, target):
        """
        从公共数据总线获取数据。
        :param target: 请求数据的寄存器或保留站的名称。
        :return: 返回请求的数据值，如果没有则返回None。
        """
        return self.data.get(target)

    def clear(self):
        """
        清除公共数据总线上的所有数据。
        """
        self.data.clear()
        self.busy = False
