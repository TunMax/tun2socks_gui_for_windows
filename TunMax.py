# -*- coding: utf-8 -*-
import sys
import wx
import wx.adv
import multiprocessing, os, time, yaml, socket
import win32gui, win32con, ctypes
import Logo
import subprocess
import re
import requests


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


def set_tun_route(mode, iplist):
    while True:
        try:
            tmp = cmd_run('ipconfig')
            time.sleep(0.1)
            if 'TunMax' in tmp:
                break
        except:
            print('finding tun device...')
    if mode == 'full':
        cmd_run_lite('netsh interface ip set address TunMax static 10.0.68.10 255.255.255.0 10.0.68.1 3')  # 3是metric
        while True:
            try:
                tmp = cmd_run('ipconfig')
                time.sleep(0.1)
                if '10.0.68.10' in tmp:
                    break
            except:
                print('waiting for TunMax to start completely')
    else:
        cmd_run_lite('netsh interface ip set address TunMax static 10.0.68.10 255.255.255.0 10.0.68.1 9999')
        while True:
            try:
                tmp = cmd_run('ipconfig')
                time.sleep(0.1)
                if '10.0.68.10' in tmp:
                    break
            except:
                print('waiting for TunMax to start completely')
        tmp = []
        for x in iplist:
            tmp.append("route add {} mask 255.255.255.255 10.0.68.1 metric 3".format(x))
        cmd_run_lite(' & '.join(tmp))
    if config['ProxyLanIP']['enable'] == True:
        tmp = []
        for x in config['ProxyLanIP']['IP']:
            tmp.append("route add {} mask 255.255.255.255 10.0.68.1 metric 3".format(x))
        cmd_run_lite(' & '.join(tmp))


def del_route():
    cmd_list = ['route delete 0.0.0.0 10.0.68.1']
    if config['Mode'] == 'expert':
        for ip in ExpertIP:
            cmd_list.append('route delete {} 10.0.68.1'.format(ip))
    else:
        for ip in server_name:
            cmd_list.append('route delete {} {}'.format(ip, config['Gateway']))
    cmd_run_lite(' & '.join(cmd_list))
    if config['ProxyLanIP']['enable'] == True:
        tmp = []
        for x in config['ProxyLanIP']['IP']:
            tmp.append("route delete {} {}".format(x, config['Gateway']))
        cmd_run_lite(' & '.join(tmp))


def dnsQuery(url):
    # res = socket.getaddrinfo(url, None) # 通过本机设置的DNS服务器获取域名IP
    # return [x[4][0] for x in res]
    res = requests.get(f'https://dns.alidns.com/resolve?name={url}')  # 阿里DNS的DoH接口
    # 其他DoH查询API记录：http://119.29.29.29/d?dn=www.baidu.com
    return [i['data'] for i in res.json()['Answer']]


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
        menu.Append(self.MENU_ID1, 'TunMax v0.1.5')
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
        try:
            win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
        except:
            pass
        try:
            del_route()
        except:
            pass
        wx.Exit()


class MyFrame(wx.Frame):
    def __init__(self):
        super().__init__()
        FolderBookmarkTaskBarIcon()


if __name__ == "__main__":
    multiprocessing.freeze_support()  # 解决pyinstaller打包后多进程模块无法工作
    app = wx.App()
    if ctypes.windll.shell32.IsUserAnAdmin() != 1:
        wx.MessageBox('未以管理员身份运行，程序无法正常工作！', '注意', wx.OK | wx.ICON_WARNING)
        sys.exit()
    # 读取yaml配置
    with open('config.yaml', 'r', encoding='utf8') as f:
        config = yaml.load(f.read(), Loader=yaml.FullLoader)
    # 自动获取当前默认网关
    routeInfo = cmd_run('route print')
    Gateway = re.findall('0\.0\.0\.0.*?0\.0\.0\.0.*?(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', routeInfo)[0]
    config['Gateway'] = Gateway
    # 解释直连域名ip
    if config['Mode'] == 'full':
        server_name = []
        cmd_set_route = []
        for x in config['Server']:
            if x.replace('.', '').isdigit():
                server_name += [x]
                server_name = list(set(server_name))
                cmd_set_route.append('route add {} {} metric 5'.format(x, config['Gateway']))
            else:
                ips = dnsQuery(x)
                server_name += ips
                server_name = list(set(server_name))
                for ip in ips:
                    cmd_set_route.append('route add {} {} metric 5'.format(ip, config['Gateway']))
        cmd_run_lite(' & '.join(cmd_set_route))
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
    # expert模式设置
    ExpertIP = []
    if config['Mode'] == 'expert':
        for x in config['ExpertIP']:
            if x.replace('.', '').isdigit():
                ExpertIP.append(x)
                ExpertIP = list(set(ExpertIP))
            else:
                ips = dnsQuery(x)
                for ip in ips:
                    ExpertIP.append(ip)
                    ExpertIP = list(set(ExpertIP))
    set_tun_route(config['Mode'], ExpertIP)
    # Then a frame.
    frm = MyFrame()
    # Show it.
    frm.Show()
    app.MainLoop()
