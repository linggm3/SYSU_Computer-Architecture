class InstructionQueue:
    def __init__(self, file_path, reservation_station, reorder_buffer):
        self.instructions = self.read_instructions(file_path)
        self.reservation_station = reservation_station
        self.reorder_buffer = reorder_buffer
        self.current_index = 0  # 当前处理的指令索引

    def read_instructions(self, file_path):
        """
        从文件读取指令。
        :param file_path: 指令文件的路径。
        :return: 指令列表。
        """
        instructions = []
        with open(file_path, 'r') as file:
            for line in file:
                instructions.append(line.strip())
        return instructions

    def issue_instruction(self):
        """
        向保留站和重排序缓冲区发射指令。
        """
        if self.current_index < len(self.instructions) and not self.reorder_buffer.is_full():
            instruction = self.instructions[self.current_index]
            parts = instruction.split()
            op = parts[0]
            dest = parts[1]

            # 发送指令到保留站
            self.reservation_station.issue_instruction(instruction)

            # 更新重排序缓冲区
            self.reorder_buffer.add_instruction(instruction, dest)
            self.current_index += 1

    def has_instructions(self):
        """
        检查是否还有未处理的指令。
        :return: 布尔值，表示是否还有指令待处理。
        """
        return self.current_index < len(self.instructions)
