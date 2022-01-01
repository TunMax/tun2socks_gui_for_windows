# TunMax
A simple gui for tun on Windows.

配合v2ray、ss等客户端(eg. v2rayN)，可使其实现tun模式。

[![GitHub License][1]](https://github.com/TunMax/tun_gui_for_windows/blob/master/LICENSE)
[![Releases][2]](https://github.com/TunMax/tun_gui_for_windows/releases)

[1]: https://img.shields.io/badge/license-GPL%203.0-blue
[2]: https://img.shields.io/badge/releases-v0.1.2-green

## 使用介绍

通过配置 **config.yaml**，运行 TunMax，可以轻松地开启tun设备接管本机所有的`TCP/UDP`流量，使游戏、UWP等不能被系统代理的应用也能被代理到，实现真正的“**全局代理**”模式。

```yaml
# 与Tun设备出口对接的代理地址，支持：socks5、shadowsocks
# 示例：socks5://127.0.0.1:10808、ss://chacha20:password@104.67.88.90:1080
Proxy: socks5://127.0.0.1:10808

# 实际代理服务器的域名或IP，可以填写多个，如为域名程序会自动解析其IP地址。
# 该项用于添加路由表直连规则。
Server: 
  - yourserver.com
  - 104.67.88.90

# 本地路由器的网关，即登陆路由器管理页面的IP地址。
Gateway: 192.168.1.1
```
## 注意事项
开启tun后，除在`config.yaml`中`Server`项设置的ip和本地局域网的ip段，其他所有ip的`TCP/UDP`连接都会被tun设备接管。

使用时，应注意以下设置，否则会造成连接死循环和无法打开网页。

### 1. 与Tun设备出口对接的代理地址为本机代理软件监听地址时，代理软件不要设置任何直连规则，否则会造成连接死循环。

原因：以使用TunMax配合v2rayN使其实现tun模式为例，开启tun后，tun接管了本机 <u>所有</u><font color=#FF0000>*</font> 的`TCP/UDP`连接。如果在v2rayN设置了 baidu.com 直连规则，浏览器访问baidu.com，发起对baidu.com的连接，该连接被tun截获接管，tun将其发给v2rayN处理，v2rayN根据规则对baidu.com发起直连，这个直连连接又会被tun截获接管，tun又将该连接发给v2rayN，v2rayN又发起直连，造成死循环。

<u>所有</u><font color=#FF0000>*</font>：不包括在`config.yaml`中`Server`项设置的ip和本地局域网的ip段。

### 2. 本地代理软件和远程代理服务器开启UDP支持，否则会出现打不开网页的情况。

原因：tun接管了本机 <u>所有</u><font color=#FF0000>*</font> 的`TCP/UDP`连接，包括DNS查询的UDP流量，如果本地代理软件和远程服务器没有开启UDP支持，就无法进行UDP流量转发完成DNS查询，域名无法解析为ip，造成打不开网页的情况。

<u>所有</u><font color=#FF0000>*</font>：不包括在`config.yaml`中`Server`项设置的ip和本地局域网的ip段。

Tips：v2rayN客户端默认开启了UDP支持，不需要特殊设置。vmess、vless协议的代理默认开启了UDP支持，不需要特殊设置。

## 软件截图

![a1.png](https://s2.loli.net/2021/12/31/4AOcwn3NGUe1Rkb.png)

## 运行环境

程序在Windows 10上开发且正常运行。理论上Windows7、8、11也可以运行，但未测试过。

## 特别感谢

[xjasonlyu/tun2socks](https://github.com/xjasonlyu/tun2socks) tun2socks - powered by gVisor TCP/IP stack
