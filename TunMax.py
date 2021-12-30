# -*- coding: utf-8 -*-
import sys
import wx
import wx.adv
import multiprocessing, os, time, yaml, socket
import win32gui, win32con, ctypes
import Logo, BypassIP
import subprocess


def cmd_run(cmd):
    cmd_output = subprocess.run(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, encoding='ansi')
    return cmd_output.stdout


def cmd_run_lite(cmd):
    subprocess.run(cmd, shell=True)


def file_path(name):
    return os.path.join(os.getcwd(), name)


def start_tun(Proxy):
    cmd_run_lite('start tun2socks -device tun://TunMax -proxy {}'.format(Proxy.strip()))


def set_tun_route():
    while True:
        try:
            tmp = cmd_run('ipconfig')
            time.sleep(0.1)
            if 'TunMax' in tmp:
                break
        except:
            print('finding tun device...')
    cmd_run_lite(
        'netsh interface ip set address TunMax static 10.0.68.10 255.255.255.0 10.0.68.1 && route add 0.0.0.0 mask 0.0.0.0 10.0.68.1 metric 3')


def del_route():
    cmd_list = ['route delete 0.0.0.0 mask 0.0.0.0 10.0.68.1']
    for ip in server_name:
        cmd_list.append('route delete {} {}'.format(ip, config['Gateway']))
    cmd_run_lite(' & '.join(cmd_list))
    # if config['BypassIP']['enable'] == True:
    #     for x, y in bypass_ip_list:
    #         cmd_run_lite('route delete {} mask {} {}'.format(x, y, config['Gateway']))


def dnsQuery(url):
    res = socket.getaddrinfo(url, None)
    return [x[4][0] for x in res]


class FolderBookmarkTaskBarIcon(wx.adv.TaskBarIcon):
    ICON = 'icon.png'
    TITLE = 'TunMax'

    MENU_ID1, MENU_ID2, MENU_ID3 = wx.NewIdRef(count=3)

    def __init__(self):
        super().__init__()
        # 设置图标和提示
        with open('icon.png', 'wb') as f:
            f.write(Logo.raw)
        self.SetIcon(wx.Icon(self.ICON), self.TITLE)
        os.remove('icon.png')
        # 绑定菜单项事件
        self.Bind(wx.EVT_MENU, self.onOne, id=self.MENU_ID1)
        self.Bind(wx.EVT_MENU, self.onTwo, id=self.MENU_ID2)
        self.Bind(wx.EVT_MENU, self.onExit, id=self.MENU_ID3)

    def CreatePopupMenu(self):
        '''生成菜单'''

        menu = wx.Menu()
        menu.Append(self.MENU_ID1, 'TunMax v0.1.2')
        menu.Append(self.MENU_ID2, '显示/隐藏控制台')
        menu.Append(self.MENU_ID3, '退出')
        return menu

    def onOne(self, event):
        pass

    def onTwo(self, event):
        if win32gui.IsWindowVisible(hwnd):
            win32gui.ShowWindow(hwnd, win32con.SW_HIDE)
        else:
            win32gui.ShowWindow(hwnd, win32con.SW_SHOWNORMAL)

    def onExit(self, event):
        win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
        del_route()
        wx.Exit()


class MyFrame(wx.Frame):
    def __init__(self):
        super().__init__()
        FolderBookmarkTaskBarIcon()


def add_bypassip_route(ip_list, gateway):
    for x, y in ip_list:
        cmd_run_lite('route add {} mask {} {}'.format(x, y, gateway))


def delete_bypassip_route(ip_list, gateway):
    for x, y in ip_list:
        cmd_run_lite('route delete {} mask {} {}'.format(x, y, gateway))


if __name__ == "__main__":
    multiprocessing.freeze_support()  # 解决pyinstaller打包后多进程模块无法工作
    app = wx.App()
    if ctypes.windll.shell32.IsUserAnAdmin() != 1:
        wx.MessageBox('未以管理员身份运行，程序无法正常工作！', '注意', wx.OK | wx.ICON_WARNING)
        sys.exit()
    # 读取yaml配置
    server_name = []
    with open('config.yaml', 'r', encoding='utf8') as f:
        config = yaml.load(f.read(), Loader=yaml.FullLoader)
    cmd_set_route = []
    # 解释直连域名ip
    for x in config['Server']:
        print('进入')
        if x.replace('.', '').isdigit():
            server_name += [x]
            cmd_set_route.append('route add {} {} metric 5'.format(x, config['Gateway']))
        else:
            ips = dnsQuery(x)
            server_name += ips
            for ip in ips:
                cmd_set_route.append('route add {} {} metric 5'.format(ip, config['Gateway']))
    cmd_run_lite(' & '.join(cmd_set_route))
    # 绕开Tun接管的IP地址的路由设置
    config['BypassIP']['enable'] = False  # ！！！因未解决添加路由表性能问题，该项暂不生效
    if config['BypassIP']['enable'] == True:
        if config['BypassIP']['mode'] == 'url':
            bypass_ip_list = BypassIP.getIP(config['BypassIP']['mode'], config['BypassIP']['target'])
        else:
            bypass_ip_list = BypassIP.getIP(config['BypassIP']['mode'], file_path(config['BypassIP']['target']))
        pool = multiprocessing.Pool(6)
        n, t1 = 0, time.time()
        for i in range(0, 120, 20):
            # pool.apply_async(add_bypassip_route, args=(bypass_ip_list[i:i + 20], config['Gateway']))
            pool.apply_async(delete_bypassip_route, args=(bypass_ip_list[i:i + 20], config['Gateway']))
        pool.close()
        pool.join()
        print(time.time() - t1)
        sys.exit()
        input('调试')
    # 启动Tun设备
    multiprocessing.Process(target=start_tun, args=(config['Proxy'],)).start()
    while True:
        hwnd = win32gui.FindWindow(None, os.getcwd().replace('/', '\\') + '\\tun2socks.exe')
        # time.sleep(0.1)
        print('finding tun output window...')
        if hwnd != 0:
            win32gui.ShowWindow(hwnd, win32con.SW_SHOWNORMAL)
            win32gui.ShowWindow(hwnd, win32con.SW_HIDE)
            break
    set_tun_route()
    # Then a frame.
    frm = MyFrame()
    # Show it.
    frm.Show()
    app.MainLoop()
