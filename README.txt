本次作业的架构如下：

main.py : 主程序
	读取指令并载入仿真器运行Speculative Tomasulo算法

Simulator.py : 仿真器
	将各个功能部件组合起来，并实现Speculative Tomasulo算法的结构

CDB.py : CDB 通用数据总线
	传输数据，进行广播，只需将数据存好，让其他模块访问即可
	
FP_Register.py : FP Registers 浮点寄存器组
	假设有10个寄存器（F0,F1,F2,F3,F4,F5,F6,F7,F8,F10)
	每个寄存器有value，reorder，busy，分别表示当前值，对应的reorder的条目编号，是否在等待指令的结果

Reservation_Station.py  : Reservation Station 保留站
	保留站每个条目有name，busy，Op，Vj，Vk，Qj，Qk，Dest，A这些字段
	每个条目存储指令类型Op，目的地址Dest，操作数（Vj，Vk，Qj，Qk），V表示已准备好的数据，Q表示有依赖的未准备好的数据，A表示Load/Store指令的地址
	FP Adder有三个加载缓冲区插槽，FP Multiplier有三个加载缓冲区插槽，Memory Unit有三个存储缓冲区插槽
	若保留站中的某个指令的操作数都准备完毕了，且对应的功能单元不处于忙碌状态，则执行这条指令，
	执行完成后结果会在CDB中广播，保留站自己侦听，从而为保留站中的其他指令获取操作数

ReOrder_Buffer.py : Reorder Buffer 重排序缓冲区
	Reorder Buffer有head和tail，分别代表最老的指令和最新的指令对应的条目号
	假设Reorder Buffer有9个条目，刚好和保留站总条目数对应
	Reorder Buffer中的每个条目有Entry，busy，Instruction，State，Dest，Value字段
	Busy位指示某一行是否正保存有指令；
	State位用来指示保存的指令当前的运行情况，ROB就是通过State的信息来判断某条指令是否可以提交，当最老的指令还没到提交阶段时，ROB中的所有指令都要等待，不能提交；
	Value还有别的作用：在一条指令执行完毕但还不能提交时，后序指令有可能从ROB中读取Value。
	Destination指示指令的目的寄存器；
	Value保存指令的结果，当指令可以提交，就直接提交Value到逻辑寄存器，这个过程不用通过CDB，而是Reorder Buffer直接与FP Registers模块交流

Instruction_Queue.py : Instruction Queue 指令队列
	属性包括n条指令（读取txt），保留站和Reorder Buffer的引用等等
	存储一系列的浮点指令，等待发射，每个周期向保留站顺序地发送一条指令（如果保留站有位置）这意味着指令发射需要1个周期
	将指令发送到保留站的同时，改写Reorder Buffer：处理器会在Reorder Buffer中按顺序找到一个空行写入指令，置Busy位为Yes，表示当前行含有指令信息；置State为Issue，表示当前指令刚刚完成发射；并在Dest处标记目的寄存器编号。
	保留站中有这些位置：FP Adder有三个加载缓冲区插槽，FP Multiplier有三个加载缓冲区插槽，Memory Unit有三个存储缓冲区插槽


Exec_Unit.py : Address Unit 地址计算单元
	有busy，delay time，instruction，当前clock，指令开始执行时的clock等等属性，这里delay time为1个周期，表示地址计算需要1个周期
	为了执行Load/Store指令，需要计算目的内存地址，计算需要1个周期，也就是说发送Load指令时，需要1个周期准备保留站中对应Load指令的A字段
	地址计算单元执行地址计算时，如果单元状态为空闲，则先将instruction和当前clock存下来，设置单元状态为忙碌。每次调用执行函数时，将clock加1，如果当前clock-指令开始执行时的clock >= delay time，则执行完成，输出结果，置单元状态为空闲；如果当前clock-指令开始执行时的clock < delay time，则执行未完成，输出None

Exec_Unit.py : Memory Unit 内存单元
	有busy，delay time，instruction，当前clock，指令开始执行时的clock等等属性，这里delay time为1个周期，表示访存需要1个周期，无论是写还是读都是1个周期
	不是流水线式的，同时只能执行一条指令，用busy标志单元是否空闲
	如果busy为false则保留站可以将发射的一条指令放入单元中执行，同时置busy为true
	内存单元执行访存时，如果单元状态为空闲，则先将instruction和当前clock存下来，设置单元状态为忙碌。每次调用执行函数时，将clock加1，如果当前clock-指令开始执行时的clock >= delay time，则执行完成，输出结果，置单元状态为空闲；如果当前clock-指令开始执行时的clock < delay time，则执行未完成，输出None
	

Exec_Unit.py : FP Adder 浮点加法运算单元
	有busy，delay time，instruction，当前clock，指令开始执行时的clock等等属性，这里delay time为2个周期（假设浮点加法和减法都要执行2个周期）
	不是流水线式的，同时只能执行一条指令，用busy标志单元是否空闲
	如果busy为false则保留站可以将发射的一条指令放入单元中执行，同时置busy为true
	浮点加法运算单元执行运算时，如果单元状态为空闲，则先将instruction和当前clock存下来，设置单元状态为忙碌。每次调用执行函数时，将clock加1，如果当前clock-指令开始执行时的clock >= delay time，则执行完成，输出结果，置单元状态为空闲；如果当前clock-指令开始执行时的clock < delay time，则执行未完成，输出None

Exec_Unit.py : FP Multiplier 浮点乘法运算单元
	和浮点加法运算单元类似
	有busy，delay time，instruction，当前clock，指令开始执行时的clock等等属性，这里乘法的delay time为10个周期，除法的delay time为20个周期
	不是流水线式的，同时只能执行一条指令，用busy标志单元是否空闲
	如果busy为false则保留站可以将发射的一条指令放入单元中执行，同时置busy为true
	浮点乘法运算单元执行运算时，如果单元状态为空闲，则先将instruction和当前clock存下来，设置单元状态为忙碌。每次调用执行函数时，将clock加1，如果当前clock-指令开始执行时的clock >= delay time，则执行完成，输出结果，置单元状态为空闲；如果当前clock-指令开始执行时的clock < delay time，则执行未完成，输出None
