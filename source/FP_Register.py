class FPRegisters:
    def __init__(self):
        # 浮点寄存器组的属性
        # 假设有10个寄存器（F0,F1,F2,F3,F4,F5,F6,F7,F8,F10)
        # 每个寄存器包含value（当前值）、reorder（对应的重排序缓冲区条目编号）、busy（是否在等待指令结果）
        self.registers = {f"F{i}": {"value": 0, "reorder": None, "busy": False} for i in range(11)}

    def set_value(self, head, register, value):
        """
        设置寄存器的值。
        :param register: 寄存器名称。
        :param value: 设置的值。
        """
        if register in self.registers and head == self.registers[register]["reorder"]:
            self.registers[register]["value"] = value
            self.registers[register]["busy"] = False

    def set_busy(self, register, reorder):
        """
        设置寄存器为忙碌状态，并记录对应的重排序缓冲区条目。
        :param register: 寄存器名称。
        :param reorder: 对应的重排序缓冲区条目编号。
        """
        if register in self.registers:
            self.registers[register]["reorder"] = reorder
            self.registers[register]["busy"] = True

    def get_value(self, register):
        """
        获取寄存器的值。
        :param register: 寄存器名称。
        :return: 寄存器的值。
        """
        return self.registers[register]["value"] if register in self.registers else None

    def is_busy(self, register):
        """
        检查寄存器是否忙碌。
        :param register: 寄存器名称。
        :return: 寄存器是否忙碌。
        """
        return self.registers[register]["busy"] if register in self.registers else False

    def show(self):
        # 获取所有寄存器名称
        register_names = list(self.registers.keys())

        # 计算每列的最大宽度
        column_width = 3

        # 准备显示数据
        reorder_values = []
        busy_values = []

        for reg in register_names:
            reorder = self.registers[reg]["reorder"]
            busy = self.registers[reg]["busy"]

            # 替换None为一个空格，True为'Yes'，False为'No'
            reorder_str = str(reorder) if reorder is not None else ' '
            busy_str = "Yes" if busy else "No"

            # 格式化为统一的列宽
            reorder_values.append(reorder_str.center(column_width))
            busy_values.append(busy_str.center(column_width))

        # 打印第一行：寄存器名称
        print("Field   | ", " | ".join(name.center(column_width) for name in register_names))

        # 打印第二行：重排序缓冲区条目编号
        print("Reorder | ", " | ".join(reorder_values))

        # 打印第三行：是否在等待指令结果
        print("Busy    | ", " | ".join(busy_values))
