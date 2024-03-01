from CDB import CDB


class AddressUnit:
    def __init__(self, cdb: CDB):
        # 地址计算单元的基本属性
        self.busy = False           # 标志单元是否忙碌
        self.delay_time = 1         # 地址计算需要的周期数
        self.instruction = None     # 当前正在执行的指令
        self.current_clock = 0      # 当前的时钟周期
        self.start_clock = 0        # 指令开始执行的时钟周期
        self.cdb = cdb

    def issue_instruction(self, instruction, current_clock):
        """
        发送指令到地址计算单元执行。
        :param instruction: 要执行的指令。
        :param current_clock: 当前的时钟周期。
        """
        if not self.busy:
            self.instruction = instruction
            self.start_clock = current_clock
            self.current_clock = current_clock
            self.busy = True

    def execute(self):
        """
        执行地址计算。
        :return: 如果计算完成，返回计算结果；否则返回None。
        """
        if self.busy:
            self.busy = False
            return int(self.instruction["Instruction"].split()[2].strip('+')) + 10
        return None


class MemoryUnit:
    def __init__(self, cdb: CDB):
        # 内存单元的基本属性
        self.busy = False           # 标志单元是否忙碌
        self.delay_time = 1         # 访存需要的周期数
        self.instruction = None     # 当前正在执行的指令
        self.current_clock = 0      # 当前的时钟周期
        self.start_clock = 0        # 指令开始执行的时钟周期
        self.cdb = cdb

    def issue_instruction(self, instruction, current_clock):
        """
        发送指令到内存单元执行。
        :param instruction: 要执行的指令。
        :param current_clock: 当前的时钟周期。
        """
        if not self.busy:
            self.instruction = instruction
            self.start_clock = current_clock
            self.current_clock = current_clock
            self.busy = True

    def execute(self):
        """
        执行内存访问。
        :return: 如果内存访问完成，返回访问结果；否则返回None。
        """
        if self.busy:
            self.current_clock += 1
            # 判断内存访问是否完成，若完成且cdb空闲，则在cdb上广播
            if self.current_clock - self.start_clock >= self.delay_time and not self.cdb.busy:
                self.busy = False
                self.cdb.broadcast(self.instruction["Entry"], 10)
                # 返回指令执行结果
                return 10  # 这里简化处理，直接返回10作为结果
        return None


class FPAdder:
    def __init__(self, cdb: CDB):
        # 浮点加法运算单元的基本属性
        self.busy = False            # 标志单元是否忙碌
        self.delay_time = 2          # 浮点加法需要的周期数
        self.instruction = None      # 当前正在执行的指令
        self.current_clock = 0       # 当前的时钟周期
        self.start_clock = 0         # 指令开始执行的时钟周期
        self.cdb = cdb

    def issue_instruction(self, instruction, current_clock):
        """
        发送指令到浮点加法运算单元执行。
        :param instruction: 要执行的指令。
        :param current_clock: 当前的时钟周期。
        """
        if not self.busy:
            self.instruction = instruction
            self.start_clock = current_clock
            self.current_clock = current_clock
            self.busy = True

    def execute(self):
        """
        执行浮点加法运算。
        :return: 如果运算完成，返回运算结果；否则返回None。
        """
        if self.busy:
            self.current_clock += 1
            # 判断运算是否完成，若完成且cdb空闲，则在cdb上广播
            if self.current_clock - self.start_clock >= self.delay_time and not self.cdb.busy:
                self.busy = False
                self.cdb.broadcast(self.instruction["Entry"], 10)
                # 返回指令执行结果
                return 10  # 这里简化处理，直接返回10作为结果
        return None


class FPMultiplier:
    def __init__(self, cdb: CDB):
        # 浮点乘法运算单元的基本属性
        self.busy = False                # 标志单元是否忙碌
        self.delay_time = {'MULTD': 10, 'DIVD': 20}  # 乘法和除法的周期数
        self.instruction = None          # 当前正在执行的指令
        self.current_clock = 0           # 当前的时钟周期
        self.start_clock = 0             # 指令开始执行的时钟周期
        self.cdb = cdb

    def issue_instruction(self, instruction, current_clock):
        """
        发送指令到浮点乘法运算单元执行。
        :param instruction: 要执行的指令。
        :param current_clock: 当前的时钟周期。
        """
        if not self.busy:
            self.instruction = instruction
            self.start_clock = current_clock
            self.current_clock = current_clock
            self.busy = True
            return True
        return False

    def execute(self):
        """
        执行浮点乘法运算。
        :return: 如果运算完成，返回运算结果；否则返回None。
        """
        if self.busy:
            self.current_clock += 1
            op = self.instruction["Instruction"].split()[0].upper()  # 获取指令中的操作类型
            delay = self.delay_time.get(op, 10)  # 默认乘法延迟
            # 判断运算是否完成，若完成且cdb空闲，则在cdb上广播
            if self.current_clock - self.start_clock >= delay and not self.cdb.busy:
                self.busy = False
                self.cdb.broadcast(self.instruction["Entry"], 10)
                # 返回指令执行结果
                return 10  # 这里简化处理，直接返回10作为结果
        return None
