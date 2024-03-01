class ReorderBuffer:
    def __init__(self, num_entries, fp_registers, cdb):
        self.entries = [{"Entry": i, "busy": False, "Instruction": None, "State": None, "Dest": None, "Value": None} for i in range(num_entries)]
        self.head = 0  # 最老的指令对应的条目号
        self.tail = 0  # 最新的指令对应的条目号
        self.cdb = cdb
        self.fp_registers = fp_registers
        self.to_write_pos = None
        self.to_write_data = None

    def add_instruction(self, instruction, dest):
        """
        添加一条指令到重排序缓冲区。
        :param instruction: 要添加的指令。
        :param dest: 指令的目的寄存器。
        """
        if not self.entries[self.tail]["busy"]:
            self.entries[self.tail] = {
                "Entry": self.tail,
                "busy": True,
                "Instruction": instruction,
                "State": "Issued",
                "Dest": dest,
                "Value": None
            }
            # store指令不设置寄存器的busy
            if self.entries[self.tail]["Instruction"].split()[0] != "SD":
                self.fp_registers.set_busy(instruction.split()[1], self.tail)
            self.tail = (self.tail + 1) % len(self.entries)

    def check_cdb(self):
        if self.to_write_pos is not None:
            self.entries[self.to_write_pos]["State"] = "WriteBack"
            self.entries[self.to_write_pos]["Value"] = self.to_write_data
            self.to_write_pos = None
            self.to_write_data = None
        if self.cdb.busy:
            for i in self.cdb.data:
                if self.entries[i]["State"] == "Executing":
                    if self.entries[i]["Instruction"].split()[0] == "SD":
                        self.entries[i]["State"] = "Commit"
                        break
                    self.to_write_pos = i
                    self.to_write_data = self.cdb.data[i]
                    self.entries[self.to_write_pos]["State"] = "Executed"
                    break
        self.cdb.clear()

    def update_state(self, entry_number, state):
        """
        更新条目的状态。
        :param entry_number: 条目编号。
        :param state: 新状态。
        """
        if 0 <= entry_number < len(self.entries):
            self.entries[entry_number]["State"] = state

    def set_value(self, entry_number, value):
        """
        设置条目的值。
        :param entry_number: 条目编号。
        :param value: 值。
        """
        if 0 <= entry_number < len(self.entries):
            self.entries[entry_number]["Value"] = value

    def commit_instructions(self):
        """
        提交重排序缓冲区中的指令。
        """
        while self.entries[self.head]["busy"] and self.entries[self.head]["State"] in ["WriteBack", "Commit"]:
            entry = self.entries[self.head]
            self.fp_registers.set_value(self.head, entry["Dest"], entry["Value"])
            entry["State"] = "Commit"
            entry["busy"] = False
            self.head = (self.head + 1) % len(self.entries)

    def get_value(self, entry_number):
        """
        获取条目的值。
        :param entry_number: 条目编号。
        :return: 条目的值。
        """
        if 0 <= entry_number < len(self.entries):
            return self.entries[entry_number]["Value"]
        return None

    def is_full(self):
        """
        检查重排序缓冲区是否已满。
        :return: 布尔值，表示缓冲区是否已满。
        """
        return self.tail == (self.head - 1) % len(self.entries)

    def is_empty(self):
        """
        检查重排序缓冲区是否为空。
        :return: 布尔值，表示缓冲区是否为空。
        """
        return self.head == self.tail

    def show(self):
        # 定义列标题
        headers = ["Entry", "busy", "Instruction", "State", "Dest", "Value"]

        # 计算每列最大宽度
        column_widths = {header: len(header) for header in headers}
        for item in self.entries:
            for key, value in item.items():
                if key == "busy":  # 特殊处理busy字段
                    value = "Yes" if value else "No"
                elif value is None:
                    value = ' '  # 将None替换为空格
                column_widths[key] = max(column_widths[key], len(str(value)))

        # 增加额外空间为每列左右预留空格
        extra_space = 2  # 每边预留空格数
        for key in column_widths.keys():
            column_widths[key] += 2 * extra_space

        # 打印标题行
        header_row = "|".join(header.center(column_widths[header]) for header in headers)
        print(header_row)
        print('-' * len(header_row))

        # 打印每个条目
        for item in self.entries:
            row = []
            for header in headers:
                value = item[header]
                if header == "busy":  # 特殊处理busy字段
                    value = "Yes" if value else "No"
                elif value is None:
                    value = ' '  # 将None替换为空格
                row.append(str(value).center(column_widths[header]))
            print("|".join(row))
