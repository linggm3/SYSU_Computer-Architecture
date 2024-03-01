from Simulator import Simulator
import sys


simulator = Simulator("input1.txt")

# 打开文件output1.txt并将其设置为标准输出
with open("output1.txt", "w") as file:
    # 保存当前的标准输出
    original_stdout = sys.stdout
    # 将标准输出重定向到文件
    sys.stdout = file

    # 运行模拟器，其输出会被重定向到output1.txt
    simulator.run()

    # 恢复标准输出到原来的状态
    sys.stdout = original_stdout

# 现在所有的print输出将正常显示在控制台
print("结果已输出在 output.txt 中")
