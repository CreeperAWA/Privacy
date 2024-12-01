# 导入必要的库
from tkinter import Tk  # 导入Tkinter库用于创建GUI界面
from check_process import check_process  # 导入自定义函数用于检查进程是否存在
from psutil import net_io_counters  # 导入psutil库用于获取网络I/O统计信息
from time import sleep  # 导入sleep函数用于暂停程序执行
from playsound import playsound  # 导入playsound库用于播放声音
from volume import volume  # 导入自定义音量控制类

class Light():
    """定义一个Light类，用于创建和控制桌面上的小灯（GUI窗口）"""
    def __init__(self, color: str, location: str, size: str = '4x4'):
        """初始化Light对象，设置颜色、位置和大小"""
        self.root = Tk()  # 创建Tk窗口
        self.root.withdraw()  # 隐藏窗口
        self.root.overrideredirect(True)  # 移除窗口装饰（标题栏、边框等）
        self.root.wm_attributes("-toolwindow", True)  # 设置窗口为工具窗口样式
        self.root.wm_attributes("-topmost", True)  # 设置窗口始终在最前面
        self.root.resizable(False, False)  # 禁止调整窗口大小
        self.root.configure(bg=color)  # 设置窗口背景颜色
        self.root.geometry(size + '+' + location)  # 设置窗口位置和大小
        self.root.attributes("-alpha", 1)  # 设置窗口透明度为不透明

    def on(self):
        """显示窗口"""
        self.root.deiconify()
        self.root.update()

    def off(self):
        """隐藏窗口"""
        self.root.withdraw()
        self.root.update()

def check_process_and_light(process_name: str, state: list, light: Light):
    """检查进程是否存在，并根据状态控制灯的开关"""
    try:
        process_exists = check_process(process_name)  # 检查进程是否存在
    except:
        return  # 出现异常时返回
    if process_exists:
        if not state[0]:  # 如果进程存在且灯当前是关闭的
            light.on()  # 打开灯
            state[0] = True  # 更新状态为开
    else:
        if state[0]:  # 如果进程不存在且灯当前是打开的
            light.off()  # 关闭灯
            state[0] = False  # 更新状态为关

def low_ethernet_traffic():
    """检查以太网流量是否低于100KB/s的阈值"""
    sent_before = net_io_counters().bytes_sent  # 获取之前的发送字节数
    sleep(1)  # 暂停1秒
    sent_now = net_io_counters().bytes_sent  # 获取现在的发送字节数
    return (sent_now - sent_before) <= 102400  # 返回是否低于阈值

def adjust_volume_and_play_sound(file_path: str):
    """调整音量并播放声音"""
    vol_control = volume()  # 创建音量控制对象
    try:
        vol_control.set_mute(False)  # 取消静音
        current_vol = vol_control.get_level()  # 获取当前音量
        if current_vol < 0.12:  # 如果当前音量低于12%
            vol_control.set_level(0.12)  # 设置音量为12%
            playsound(file_path)  # 播放声音
        # 如果我们改变了音量，则恢复之前的音量
        if current_vol < 0.12:
            vol_control.set_level(current_vol)
    except Exception as e:
        print(f"Error playing sound or adjusting volume: {e}")  # 打印错误信息

# 设置灯光
temp = Tk()  # 临时Tk对象用于获取屏幕分辨率
screen_width = temp.winfo_screenwidth()  # 获取屏幕宽度
temp.withdraw()  # 隐藏临时Tk对象
# 创建四个灯光对象，分别代表不同的监控状态
L1 = Light(color='#00FF00', location=str(int(screen_width / 2 - 15)) + '+0')  # 低网络流量
L2 = Light(color='#0000FF', location=str(int(screen_width / 2 - 7)) + '+0')   # 远程桌面
L3 = Light(color='#FF0000', location=str(int(screen_width / 2 + 1)) + '+0')   # 摄像头捕获
L4 = Light(color='#FF9300', location=str(int(screen_width / 2 + 9)) + '+0')   # 屏幕捕获

state_lights = [False, False, False, False]  # 灯光状态列表
state_media = False  # 媒体状态

while True:
    # 检查进程并更新灯光状态
    check_process_and_light('screenCapture.exe', state_lights, L4)
    check_process_and_light('media_capture.exe', state_lights, L3)
    check_process_and_light('rtcRemoteDesktop.exe', state_lights, L2)

    # 检查网络流量
    if low_ethernet_traffic():
        if any(state_lights[1:]):  # 如果其他监控进程中有任何一个是运行的
            if not state_lights[0]:  # 如果低流量灯当前是关闭的
                L1.on()  # 打开低流量灯
                state_lights[0] = True  # 更新状态为开
        else:
            if state_lights[0]:  # 如果没有其他监控进程运行且低流量灯是打开的
                L1.off()  # 关闭低流量灯
                state_lights[0] = False  # 更新状态为关
    else:
        if state_lights[0]:  # 如果低流量灯是打开的
            L1.off()  # 关闭低流量灯
            state_lights[0] = False  # 更新状态为关

    # 检查media_capture.exe进程并调整音量/播放声音
    try:
        media_capture_running = check_process('media_capture.exe')  # 检查media_capture.exe进程是否存在
    except:
        sleep(0.5)  # 出现异常时暂停0.5秒并继续循环
        continue

    if media_capture_running:
        if not low_ethernet_traffic():  # 只有当网络流量不低时才调整音量和播放声音
            if not state_media:  # 如果媒体状态当前是关闭的
                adjust_volume_and_play_sound("C:\\Windows\\Media\\Speech On.wav")  # 调整音量并播放“开始语音”声音
                state_media = True  # 更新媒体状态为开
    else:
        if state_media:  # 如果媒体状态当前是打开的
            adjust_volume_and_play_sound("C:\\Windows\\Media\\Speech Sleep.wav")  # 调整音量并播放“结束语音”声音
            state_media = False  # 更新媒体状态为关

    sleep(2)  # 暂停2秒然后继续循环