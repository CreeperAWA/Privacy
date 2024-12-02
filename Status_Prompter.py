# 导入必要的库
from tkinter import Tk  # 导入Tkinter库用于创建图形界面
from psutil import net_io_counters  # 导入psutil库用于获取网络I/O统计信息
from time import sleep  # 导入sleep函数用于延迟执行
from playsound import playsound  # 自定义模块，用于播放声音
from volume import volume  # 自定义模块，用于控制音量
from check_process import check_process  # 自定义模块，用于检查进程是否存在
from subprocess import check_output  # 导入check_output函数用于执行外部命令

# 定义一个Light类，用于表示一个灯光（图形界面元素）
class Light():
    def __init__(self, color: str, location: str, size: str = '40x40'):
        # 初始化Tkinter窗口，并设置窗口的各种属性（颜色、位置、大小、透明度等）
        self.root = Tk()
        self.root.withdraw()  # 隐藏窗口
        self.root.overrideredirect(True)  # 去除窗口边框
        self.root.wm_attributes("-toolwindow", True)  # 设置窗口为工具窗口
        self.root.wm_attributes("-topmost", True)  # 窗口始终置顶
        self.root.resizable(False, False)  # 禁止调整窗口大小
        self.root.configure(bg=color)  # 设置窗口背景颜色
        self.root.geometry(size + '+' + location)  # 设置窗口大小和位置
        self.root.attributes("-alpha", 0.8)  # 设置窗口透明度为80%

    def on(self):
        self.root.deiconify()  # 显示窗口
        self.root.update()  # 更新窗口

    def off(self):
        self.root.withdraw()  # 隐藏窗口
        self.root.update()  # 更新窗口

# 根据进程名和状态控制灯光开关的函数
def check_process_and_light(process_name: str, state: list, light: Light):
    try:
        process_exists = check_process(process_name)  # 检查进程是否存在
    except:
        return  # 出现异常时返回
    # 根据进程是否存在和当前状态控制灯光开关
    if process_exists:
        if not state[0]:
            light.on()
            state[0] = True
    else:
        if state[0]:
            light.off()
            state[0] = False

# 判断网络上行流量是否低于阈值的函数
def low_Ethernet_traffic():
    sent_before = net_io_counters().bytes_sent  # 已发送的流量
    sleep(1)  # 暂停1秒
    sent_now = net_io_counters().bytes_sent
    return True if (sent_now - sent_before)<= 102400 else False  # 算出1秒后的差值并判断(单位:Byte) 当前阈值：100KB

# 调整音量并播放声音的函数
def adjust_volume_and_play_sound(file_path: str):
    vol_control = volume()  # 实例化音量控制对象
    try:
        # 取消静音并将音量设置为12%（如果低于此值）
        vol_control.set_mute(False)
        current_vol = vol_control.get_level()  # 获取当前音量
        if current_vol < 0.12:  # 假设get_level()返回的值在0和1之间
            vol_control.set_level(0.12)
            playsound(file_path)  # 播放声音
        # 如果改变了音量，则恢复原音量
        if current_vol < 0.12:
            vol_control.set_level(current_vol)
    except Exception as e:
        print(f"Error playing sound or adjusting volume: {e}")  # 打印错误信息

# 设置灯光的位置和颜色
temp = Tk()
screen_width = temp.winfo_screenwidth()  # 获取屏幕宽度
temp.withdraw()  # 隐藏临时窗口
# 创建四个灯光，分别对应不同的颜色和位置
L1 = Light(color='#00FF00', location=str(int(screen_width / 2 - 15)) + '+0')  # 低网络流量
L2 = Light(color='#0000FF', location=str(int(screen_width / 2 - 7)) + '+0')   # 远程桌面
L3 = Light(color='#FF0000', location=str(int(screen_width / 2 + 1)) + '+0')   # 摄像头捕获
L4 = Light(color='#FF9300', location=str(int(screen_width / 2 + 9)) + '+0')   # 屏幕捕获

# 初始化灯光和媒体状态
state_lights = [False, False, False, False]  # 灯光状态
state_media = False  # 媒体状态

# 主循环，持续监控并更新灯光状态、网络流量和媒体状态
while True:
    # 检查进程并更新灯光状态
    check_process_and_light('screenCapture.exe', [state_lights[3]], L4)
    check_process_and_light('media_capture.exe', [state_lights[2]], L3)
    check_process_and_light('rtcRemoteDesktop.exe', [state_lights[1]], L2)

    # 检查网络流量
    if low_Ethernet_traffic():  # 如果网络流量低
        if any(state_lights[1:]):  # 如果任何监控进程正在运行
            if not state_lights[0]:  # 如果无灯亮起
                L1.on()  # 亮起灯1
                state_lights[0] = True  # 更新状态：网络流量低状态灯亮起
        else:
            if state_lights[0]:  # 如果网络流量低状态登亮起
                L1.off()  # 熄灭灯1
                state_lights[0] = False  # 更新状态：网络流量低状态灯关闭
    else:
        if state_lights[0]:  # 如果网络流量低状态登亮起
            L1.off()  # 熄灭灯1
            state_lights[0] = False  # 更新状态：网络流量低状态灯关闭

    # 检查media_capture.exe并调整音量/播放声音
    try:
        media_capture_running = check_process('media_capture.exe')  # 检查媒体捕获进程是否存在
    except:
        sleep(0.5)
        continue

    if media_capture_running:
        if not low_Ethernet_traffic():  # 仅在网络流量不低时调整
            if not state_media:
                adjust_volume_and_play_sound("C:\\Windows\\Media\\Speech On.wav")
                state_media = True
    else:
        if state_media:
            adjust_volume_and_play_sound("C:\\Windows\\Media\\Speech Sleep.wav")
            state_media = False

    # 如果网络流量持续低，则尝试终止相关进程
    if low_Ethernet_traffic():
        count = 0
        while True:
            try:
                process_state = check_process(['media_capture.exe', 'screenCapture.exe', 'rtcRemoteDesktop.exe'])  # 检查进程状态
            except:
                sleep(0.5)
                continue
            if process_state:
                sent_before = net_io_counters().bytes_sent  # 记录发送前的字节数
                sleep(1)  # 延迟1秒
                sent_now = net_io_counters().bytes_sent  # 记录发送后的字节数
                if sent_now - sent_before < 102400:  # 上传速度低于100KB/S
                    count += 1
                else:
                    count = 0
                if count >= 60:  # 如果低流量状态持续60秒
                    try:
                        # 使用Nsudo以管理员权限终止进程
                        check_output('Nsudo -U:S -ShowWindowMode:Hide taskkill /f /im media_capture.exe', shell=True)
                        check_output('Nsudo -U:S -ShowWindowMode:Hide taskkill /f /im screenCapture.exe', shell=True)
                        check_output('Nsudo -U:S -ShowWindowMode:Hide taskkill /f /im rtcRemoteDesktop.exe', shell=True)
                    except:
                        pass
                    break  # 终止内层循环
            else:
                count = 0
                break  # 如果没有找到相关进程，终止内层循环

    sleep(1)  # 延迟1秒，减少CPU占用