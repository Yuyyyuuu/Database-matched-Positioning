import math
import matplotlib.pyplot as plt
import tkinter as tk
from ttkthemes import ThemedTk
from tkinter import filedialog
from tkinter import messagebox


sigma=0.5 # 用高斯分布来描述可能性
k=1 # 用 Sigmoid 函数来描述可能性

# 平面坐标类
class EN:
    def __init__(self):
        self.E = 0
        self.N = 0

# 数据库类
class Database:
    def __init__(self, num, rss_list):
        self.num = num
        self.EN = EN()
        self.RSS = rss_list

# 测试数据类
class Testdata:
    def __init__(self, t, rss_list):
        self.t = t
        self.EN = EN()
        self.RSS = rss_list

# 解算结果类
class Result:
    def __init__(self):
        self.t = 0
        self.EN = EN()

database_list=[]
testdata_list=[]
result_data=[]
refer_E=[]
refer_N=[]
real_E=[]
real_N=[]

# 生成数据库
# filepath1:  database.data的绝对路径
# filepath2:  rp_loc.txt的绝对路径
#database_list:  存储着数据库类Database数据类型的列表
def create_database(filepath1,filepath2,database_list):
    # 创建中间列表
    database_helper_list=[]
    # 打开文件并逐行读取数据
    with open(filepath1, 'r') as file:
        lines = file.readlines()
        # 遍历每行数据
        for line in lines:
            # 按空格分隔字符串，得到数字列表
            data = line.strip().split(' ')
            # 将第一个数字设为 num，剩余数字作为 RSS 列表
            num = int(data[0])
            rss_values = [int(x) for x in data[1:]]
            # 创建并添加数据库实例到数据库列表
            database = Database(num, rss_values)
            database_helper_list.append(database)
    # 创建一个字典用于存储num对应的RSS列表
    rss_dict = {}
    # 遍历数据库助手列表
    for helper in database_helper_list:
        num = helper.num
        rss_list = helper.RSS
        if num not in rss_dict:
            # 第一次出现num值，将RSS列表添加
            rss_dict[num] = []
        # 添加RSS列表到对应的num键下
        rss_dict[num].append(rss_list)
    # 遍历rss_dict字典中的每个num键值对
    for num, rss_lists in rss_dict.items():
        # 获取每列RSS列表的长度
        columns = len(rss_lists[0]) # 即每个点位对应的特征向量的维数
        # 创建列表，用于存储平均值
        average_rss = []
        # 迭代每列RSS列表的索引
        for i in range(columns):
            total = 0
            count = 0
            # 求每列RSS列表的总和
            for rss_list in rss_lists:
                rss = rss_list[i]
                if rss != -110:
                    total += rss
                    count += 1
            # 计算平均值，注意处理全部元素为-110的情况
            if count == 0:
                average_rss.append(0)
            else:
                average_rss.append(total / count)
        # 创建Database对象，并添加到结果列表
        database_obj = Database(num, average_rss)
        database_list.append(database_obj)

    # 打开文件并逐行读取数据
    with open(filepath2, 'r') as file:
        lines = file.readlines()
        # 遍历每行数据
        for line in lines:
            # 按空格分隔字符串，得到数字列表
            data = line.strip().split(' ')
            i = int(data[0])
            database_list[i - 1].EN.E = float(data[1])
            database_list[i - 1].EN.N = float(data[2])

# 读入测试数据文件
# filepath:  test1_with_ref.data的绝对路径
# testdata_list:  存储着测试数据类Testdata数据类型的列表
def read_testdata(filepath,testdata_list):
    # 打开文件并逐行读取数据
    with open(filepath, 'r') as file:
        lines = file.readlines()
        # 遍历每行数据
        for line in lines:
            # 按空格分隔字符串，得到数字列表
            data = line.strip().split(' ')
            # 将第一个数字设为 num，剩余数字作为 RSS 列表
            t = float(data[0])
            rss_values = [float(x) for x in data[1:31]]
            E=float(data[31])
            N=float(data[32])
            # 创建并添加数据库实例到数据库列表
            testdata = Testdata(t, rss_values)
            testdata.EN.E = E
            testdata.EN.N = N
            testdata_list.append(testdata)
    # 循环遍历testdata_list中的每个元素
    for i in range(len(testdata_list)):
        rss_list = testdata_list[i].RSS
        # 将-110替换为0
        for j in range(len(rss_list)):
            if rss_list[j] == -110:
                testdata_list[i].RSS[j] = 0

# 位置估计函数
def match(database_list,testdata_list,result_data):

    # 遍历测试数据列表
    for testdata in testdata_list:
        t = testdata.t
        rss_list_test = testdata.RSS

        # 禁用索引列表，用于记录不可用的索引
        disabled_indexes = []
        # 检查并禁用为测试数据中信号强度列表中元素为0的索引
        for i in range(len(rss_list_test)):
            if rss_list_test[i] == 0:
                disabled_indexes.append(i)
        # 遍历数据库列表,完善禁用列表
        for database in database_list:
            rss_list_database = database.RSS
            # 检查并禁用为0的索引
            for i in range(len(rss_list_database)):
                if rss_list_database[i] == 0:
                    disabled_indexes.append(i)

        #按照[num,distance]形式存储向量距离的列表
        dis_result=[]
        # 遍历数据库列表
        for database in database_list:
            num = database.num
            rss_list_database = database.RSS
            # 计算差值并求和
            difference_squared_sum = 0
            for i in range(len(rss_list_test)):
                if i not in disabled_indexes:
                    difference = rss_list_test[i] - rss_list_database[i]
                    difference_squared_sum += difference ** 2
            # 计算平方和的开平方即距离并存入结果列表
            result_value = math.sqrt(difference_squared_sum)
            dis_result.append([num,result_value])
        # 对 dis_result 列表按 value 进行排序
        sorted_dis_result = sorted(dis_result, key=lambda x: x[1])
        # 提取 value 最小的三个元素对应的 num
        min_three_nums = [result[0] for result in sorted_dis_result[:3]]
        num1 = min_three_nums[0]
        num2 = min_three_nums[1]
        num3 = min_three_nums[2]
        min_three_values = [result[1] for result in sorted_dis_result[:3]]

        #距离反比---可能性函数
        #p1=  1 / min_three_values[0]
        #p2 = 1 / min_three_values[1]
        #p3 = 1 / min_three_values[2]
        #高斯分布---可能性函数
        #p1=math.exp(-0.5 * (min_three_values[0] / sigma) ** 2)
        #p2 = math.exp(-0.5 * (min_three_values[1] / sigma) ** 2)
        #p3 = math.exp(-0.5 * (min_three_values[2] / sigma) ** 2)
        #Sigmoid函数---可能性函数
        p1 = 1 / (1 + math.exp(-k * min_three_values[0]))
        p2 = 1 / (1 + math.exp(-k * min_three_values[1]))
        p3 = 1 / (1 + math.exp(-k * min_three_values[2]))

        result_obj=Result()
        result_obj.t=t
        result_obj.EN.E = (p1 * database_list[num1 - 1].EN.E + p2 * database_list[num2 - 1].EN.E + p3 * database_list[num3 - 1].EN.E) / (p1 + p2 + p3)
        result_obj.EN.N = (p1 * database_list[num1 - 1].EN.N + p2 * database_list[num2 - 1].EN.N + p3 * database_list[num3 - 1].EN.N) / (p1 + p2 + p3)
        result_data.append(result_obj)

#读入数据库文件
def on_button1_click():
    global filepath1
    filepath1 = filedialog.askopenfilename()
    messagebox.showinfo("提示", "读取成功！")

#读入测试数据文件
def on_button2_click():
    filepath = filedialog.askopenfilename()
    read_testdata(filepath, testdata_list)
    messagebox.showinfo("提示", "读取成功！")

#读入参考点的坐标文件
def on_button3_click():
    global filepath2
    filepath2 = filedialog.askopenfilename()
    messagebox.showinfo("提示", "读取成功！")


#生成数据库
def on_button4_click():
    create_database(filepath1, filepath2, database_list)
    messagebox.showinfo("提示", "生成数据库成功！")

#生成参考点的点位分布图
def on_button5_click():
    for it in database_list:
        refer_E.append(it.EN.E)
        refer_N.append(it.EN.N)
    # 设置图幅名和轴标签
    plt.title("RP location")
    plt.xlabel("E (m)")
    plt.ylabel("N (m)")
    # 绘制散点图
    plt.scatter(refer_E, refer_N, marker="*", c="blue", label="p")
    # 添加网格线
    plt.grid(True, axis="both", linestyle="--", alpha=0.5)
    # 保持横轴和纵轴的长度一致
    plt.axis("equal")
    # 显示图例
    plt.legend()
    # 展示图表
    plt.show()

#进行位置估计
def on_button6_click():
    match(database_list, testdata_list, result_data)
    messagebox.showinfo("提示", "指纹识别成功！")

#生成结果轨迹图
def on_button7_click():
    global result_E
    global result_N
    result_E = [value.EN.E for value in result_data]
    result_N = [value.EN.N for value in result_data]
    # 设置图幅名和轴标签
    plt.title("Fingerprinting solution")
    plt.xlabel("E (m)")
    plt.ylabel("N (m)")
    # 绘制轨迹图
    plt.plot(result_E, result_N, marker="o", linestyle="-", markersize=3.5, color="red", label="p")
    # 添加网格线
    plt.grid(True, linestyle="--", alpha=0.5)
    # 保持横轴和纵轴的长度一致
    plt.axis("equal")
    # 显示图例
    plt.legend()
    # 展示图表
    plt.show()

#生成轨迹对比图
def on_button8_click():
    for it in testdata_list:
        real_E.append(it.EN.E)
        real_N.append(it.EN.N)
    # 设置图幅名和轴标签
    plt.title("Position solution and reference")
    plt.xlabel("E (m)")
    plt.ylabel("N (m)")
    # 绘制轨迹图
    plt.plot(result_E, result_N, marker="o", linestyle="-", markersize=3.5, color="red", label="FP")
    plt.plot(real_E, real_N, marker="*", linestyle="-", markersize=5, color="green", label="Ref")
    # 添加网格线
    plt.grid(True, linestyle="--", alpha=0.5)
    # 保持横轴和纵轴的长度一致
    plt.axis("equal")
    # 显示图例
    plt.legend()
    # 展示图表
    plt.show()

#保存结果文件
def on_button9_click():
    filepath = filedialog.asksaveasfilename(defaultextension=".txt", initialfile="result_data.txt")
    with open(filepath, "w") as file:
        file.write(" t/s        E/m       N/m\n")
        for result in result_data:
            t = result.t
            E = result.EN.E
            N = result.EN.N
            file.write(" {:.3f}    {:.3f}    {:.3f}\n".format(t, E, N))


# 创建主窗口
window = ThemedTk(theme="arc")  # 使用ThemedTk创建带有主题的窗口
window.title("2D Fingerprint matching by Yu")

# 创建界面组件
custom_text = "请先读取必要的数据后再生成结果图或保存结果文件"
label = tk.Label(window, text=custom_text,font=("Arial", 12))
label.place(x=150, y=20)

button1 = tk.Button(window, text="读入数据库文件", command=on_button1_click,font=("Arial", 14))
button1.place(x=40, y=75)

button2 = tk.Button(window, text="读入测试数据文件", command=on_button2_click,font=("Arial", 14))
button2.place(x=235, y=75)

button3 = tk.Button(window, text="读入参考点位坐标文件", command=on_button3_click,font=("Arial", 14))
button3.place(x=450, y=75)

button4 = tk.Button(window, text="生成数据库", command=on_button4_click,font=("Arial", 14))
button4.place(x=50, y=160)

button5 = tk.Button(window, text="生成参考点的点位分布图", command=on_button5_click,font=("Arial", 14))
button5.place(x=225, y=160)

button6 = tk.Button(window, text="进行位置估计", command=on_button6_click,font=("Arial", 14))
button6.place(x=510, y=160)

button7 = tk.Button(window, text="生成结果轨迹图", command=on_button7_click,font=("Arial", 14))
button7.place(x=45, y=245)

button8 = tk.Button(window, text="生成轨迹对比图", command=on_button8_click,font=("Arial", 14))
button8.place(x=265, y=245)

button9 = tk.Button(window, text="保存结果文件", command=on_button9_click,font=("Arial", 14))
button9.place(x=490, y=245)

# 设置窗口属性
window.geometry("700x350")  # 设置窗口大小为宽600像素、高400像素

# 运行窗口循环
window.mainloop()