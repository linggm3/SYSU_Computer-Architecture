from Exec_Unit import AddressUnit, MemoryUnit, FPMultiplier, FPAdder
from FP_Register import FPRegisters
from Instruction_Queue import InstructionQueue
from Reservation_Station import ReservationStation
from ReOrder_Buffer import ReorderBuffer
from CDB import CDB


class Simulator:
    def __init__(self, instruction_file_path):
        # 初始化组件
        self.fp_registers = FPRegisters()
        self.cdb = CDB()
        self.fp_adder = FPAdder(self.cdb)
        self.fp_multiplier = FPMultiplier(self.cdb)
        self.memory_unit = MemoryUnit(self.cdb)
        self.address_unit = AddressUnit(self.cdb)
        self.reorder_buffer = ReorderBuffer(9, self.fp_registers, self.cdb)
        self.reservation_station = ReservationStation(self.cdb, self.fp_registers, self.fp_adder, self.fp_multiplier, self.memory_unit, self.address_unit, self.reorder_buffer)
        self.instruction_queue = InstructionQueue(instruction_file_path, self.reservation_station, self.reorder_buffer)
        self.clock = 0

    def run(self):
        # 运行模拟器
        while self.instruction_queue.has_instructions() or not self.reorder_buffer.is_empty():
            print(f"---------------------------Clock Cycle: {self.clock+1}---------------------------\n")

            self.cdb.clear()
            self.reorder_buffer.commit_instructions()
            self.reservation_station.execute_instructions()
            self.reorder_buffer.check_cdb()
            self.reservation_station.update_from_rob()
            self.instruction_queue.issue_instruction()

            self.clock += 1

            self.reorder_buffer.show()
            print()
            self.reservation_station.show()
            print()
            self.fp_registers.show()
            print("\n\n")

            # 防止无限循环
            if self.clock > 100:
                break
