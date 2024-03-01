class ReservationStation:
    def __init__(self, cdb, fp_registers, fp_adder, fp_multiplier, memory_unit, address_unit, reorder_buffer):
        # 初始化保留站的条目
        self.entries = {
            "Add": [{"name": f"Add{i}", "busy": False, "Op": None, "Vj": None, "Vk": None, "Qj": None, "Qk": None, "Dest": None, "A": None} for i in range(3)],
            "Mult": [{"name": f"Mult{i}", "busy": False, "Op": None, "Vj": None, "Vk": None, "Qj": None, "Qk": None, "Dest": None, "A": None} for i in range(3)],
            "Load": [{"name": f"Load{i}", "busy": False, "Op": None, "Vj": None, "Vk": None, "Qj": None, "Qk": None, "Dest": None, "A": None} for i in range(3)]
        }
        self.cdb = cdb
        self.fp_registers = fp_registers
        self.fp_adder = fp_adder
        self.fp_multiplier = fp_multiplier
        self.memory_unit = memory_unit
        self.address_unit = address_unit
        self.reorder_buffer = reorder_buffer
        self.clock = 0

    def issue_instruction(self, instruction):
        """
        向保留站发射指令。
        :param instruction: 要发射的指令。
        """
        op, *operands = instruction.split()
        entry_type = "Add" if op in ["ADDD", "SUBD"] else "Mult" if op in ["MULTD", "DIVD"] else "Load"

        for entry in self.entries[entry_type]:
            if not entry["busy"]:
                entry["busy"] = True
                entry["Op"] = op
                # 检查源操作数对应的寄存器是否busy
                if op == "LD":
                    entry["Vj"] = operands[2]  # 地址
                    entry["Vk"] = None
                    entry["Qj"] = None
                    entry["Qk"] = None
                    entry["A"] = operands[1]
                elif op == "SD":
                    # 检查操作数对应的寄存器是否busy
                    if self.fp_registers.is_busy(operands[0]):
                        entry["Qj"] = operands[0]
                    else:
                        entry["Vj"] = operands[0]
                    entry["Vk"] = operands[2]
                    entry["Qk"] = None
                    entry["A"] = operands[1]
                else:
                    # 检查操作数对应的寄存器是否busy
                    if self.fp_registers.is_busy(operands[1]):
                        entry["Qj"] = operands[1]
                    else:
                        entry["Vj"] = operands[1]
                    if self.fp_registers.is_busy(operands[2]):
                        entry["Qk"] = operands[2]
                    else:
                        entry["Vk"] = operands[2]
                entry["Dest"] = str(self.reorder_buffer.tail)  # 目的地址
                break

    def execute_instructions(self):
        """
        执行保留站中的指令。
        """
        for _, entries in self.entries.items():
            for entry in entries:
                if entry["busy"] and self.reorder_buffer.entries[int(entry["Dest"])]["State"] in ["WriteBack", "Commit"]:
                    entry["busy"] = False
                # 仅当所有操作数准备就绪时，执行指令
                if entry["busy"] and all(entry[q] is None for q in ["Qj", "Qk"]):
                    unit = None
                    if entry["Op"] in ["ADDD", "SUBD"]:
                        unit = self.fp_adder
                    elif entry["Op"] in ["MULTD", "DIVD"]:
                        unit = self.fp_multiplier
                    elif entry["Op"] in ["LD", "SD"]:
                        unit1 = self.address_unit
                        unit = self.memory_unit
                        # 查看是否完成访存地址的计算，没有则计算地址（需要消耗一周期）
                        if entry["busy"] and not entry["Vj"] is None and self.reorder_buffer.entries[int(entry["Dest"])]["State"] == "Issued":
                            if not unit1.busy:
                                unit1.issue_instruction(self.reorder_buffer.entries[int(entry["Dest"])], 0)
                                entry["Vj"] = None
                                entry["A"] = unit1.execute()
                                self.reorder_buffer.entries[int(entry["Dest"])]["State"] = "Executing"
                        # 当执行单元不忙时，向单元输入指令
                        elif not unit.busy and self.reorder_buffer.entries[int(entry["Dest"])]["State"] == "Executing":
                            unit.issue_instruction(self.reorder_buffer.entries[int(entry["Dest"])], 0)
                            self.reorder_buffer.entries[int(entry["Dest"])]["State"] = "Executing"
                        continue

                    # 当执行单元不忙时，向单元输入指令
                    if not unit.busy and self.reorder_buffer.entries[int(entry["Dest"])]["State"] == "Issued":
                        unit.issue_instruction(self.reorder_buffer.entries[int(entry["Dest"])], 0)
                        self.reorder_buffer.entries[int(entry["Dest"])]["State"] = "Executing"

        # 调用各执行单元的execute方法
        for unit in [self.fp_adder, self.fp_multiplier, self.memory_unit, self.address_unit]:
            result = unit.execute()

    def update_from_rob(self):
        """
        更新可用数据源(从rob中）
        """
        for _, entries in self.entries.items():
            for entry in entries:
                if entry["busy"]:
                    if not entry["Qj"] is None:
                        # 已经执行完成保存在buffer中，可将Q转为V
                        if self.reorder_buffer.entries[self.fp_registers.registers[entry["Qj"]]["reorder"]]["Value"] is not None:
                            # print(self.reorder_buffer.entries[self.fp_registers.registers[entry["Qj"]]["reorder"]]["Value"])
                            entry["Vj"] = entry["Qj"]
                            entry["Qj"] = None

                    if not entry["Qk"] is None:
                        if self.reorder_buffer.entries[self.fp_registers.registers[entry["Qk"]]["reorder"]][
                                "Value"] is not None:
                            entry["Vk"] = entry["Qk"]
                            entry["Qk"] = None
                    # # 检查Qj和Qk是否可以通过CDB更新
                    # for q in ["Qj", "Qk"]:
                    #     print(entry[q])
                    #     if entry[q]:
                    #         data = self.cdb.get_data(entry[q])
                    #         if data is not None:
                    #             entry[f"V{q[1]}"] = data
                    #             entry[q] = None

    def show(self):
        # 定义列标题
        headers = ["name", "busy", "Op", "Vj", "Vk", "Qj", "Qk", "Dest", "A"]

        # 计算每列最大宽度
        column_widths = {header: len(header) for header in headers}
        for type_ in self.entries:
            for item in self.entries[type_]:
                for key, value in item.items():
                    if key == "busy":  # 特殊处理busy字段
                        value = "Yes" if value else "No"
                    elif value is None:
                        value = ' '  # 将None替换为空格
                    column_widths[key] = max(column_widths[key], len(str(value)))

        # 增加额外空间为每列左右预留空格
        extra_space = 2
        for key in column_widths.keys():
            column_widths[key] += 2 * extra_space

        # 打印列标题
        header_row = "|".join(header.center(column_widths[header]) for header in headers)
        print(header_row)
        print('-' * len(header_row))

        # 为每种类型的保留站打印条目
        for type_ in self.entries:
            for item in self.entries[type_]:
                row = []
                for header in headers:
                    value = item[header]
                    if header == "busy":  # 特殊处理busy字段
                        value = "Yes" if value else "No"
                    elif value is None:
                        value = ' '  # 将None替换为空格
                    row.append(str(value).center(column_widths[header]))
                print("|".join(row))
