# TunMax
A simple gui for tun2socks on Windows.

配合v2ray、ss等客户端(eg. v2rayN)，可使其实现tun模式。

[![GitHub License][1]](https://github.com/TunMax/tun_gui_for_windows/blob/master/LICENSE)
[![Releases][2]](https://github.com/TunMax/tun_gui_for_windows/releases)

[1]: https://img.shields.io/badge/license-GPL%203.0-blue
[2]: https://img.shields.io/badge/releases-v0.1.5-green

## 使用介绍

通过配置 **config.yaml**，运行 TunMax，可以轻松地开启tun设备接管本机所有的`TCP/UDP`流量，使游戏、UWP等不能被系统代理的应用也能被代理到，实现真正的 **全局代理** 模式。

```yaml
# 与Tun设备出口对接的代理地址，支持：socks5、shadowsocks
# 示例：socks5://127.0.0.1:10808、ss://chacha20:password@104.67.88.90:1080
# 注意：如果以下是本机监听的地址，开启这个监听地址的软件一定要使用全局规则(Global Mode)，否则会引起死循环。关于死循环的解释，参见本项目的README.md
Proxy: socks5://127.0.0.1:10808

# 可选两种模式，full与expert
# full模式：默认模式，除Server项目设置的地址和本地局域网ip直连，其他流量均走tun
# expert模式：除ExpertIP设置的地址走tun，其他流量均直连。
Mode: full

# 实际代理服务器的域名或IP，可以填写多个，如为域名程序会自动解析其IP地址。
# 该项也用于添加路由表直连规则，属于以下域名或IP的流量均直连，不经过tun。
Server: 
  - yourserver.com
  - 104.67.88.90

# 使用expert模式时生效
ExpertIP:
  - ip138.com
  - 192.168.1.26

# [可选功能]
# 因为full模式下，本地局域网ip默认会直连。如需使其强制走tun，将以下enable值改为true，并填写强制走tun的局域网ip。
# 开启以下配置后，无论是full模式还是expert模式，填写的局域网ip都会走tun。注：以下仅可填写ip，不支持填写域名。
ProxyLanIP:
  enable: false
  IP:
    - 192.168.1.10
    - 192.168.1.11
```
## 注意事项
开启tun后，除在`config.yaml`中`Server`项设置的ip和本地局域网的ip段，其他所有ip的`TCP/UDP`连接都会被tun设备接管。

使用时，应注意以下设置，否则会造成连接死循环和无法打开网页。

### 1. 与Tun设备出口对接的代理地址为本机代理软件监听地址时，代理软件不要设置任何直连规则，否则会造成连接死循环。

原因：以使用TunMax配合v2rayN使其实现tun模式为例，开启tun后，tun接管了本机 [所有*](#) 的`TCP/UDP`连接。如果在v2rayN设置了 baidu.com 直连规则，浏览器访问baidu.com，发起对baidu.com的连接，该连接被tun截获接管，tun将其发给v2rayN处理，v2rayN根据规则对baidu.com发起直连，这个直连连接又会被tun截获接管，tun又将该连接发给v2rayN，v2rayN又发起直连，造成死循环。

[所有*](#)：不包括在`config.yaml`中`Server`项设置的ip和本地局域网的ip段。

### 2. 本地代理软件和远程代理服务器开启UDP支持，否则会出现打不开网页的情况。

原因：tun接管了本机 [所有*](#) 的`TCP/UDP`连接，包括DNS查询的UDP流量，如果本地代理软件和远程服务器没有开启UDP支持，就无法进行UDP流量转发完成DNS查询，域名无法解析为ip，造成打不开网页的情况。

[所有*](#)：不包括在`config.yaml`中`Server`项设置的ip和本地局域网的ip段。

Tips：v2rayN客户端默认开启了UDP支持，不需要特殊设置。vmess、vless协议的代理默认开启了UDP支持，不需要特殊设置。

## 软件截图

![a1.png](https://s2.loli.net/2021/12/31/4AOcwn3NGUe1Rkb.png)

## 运行环境

Windows 7、8、10、11

## 特别感谢

[xjasonlyu/tun2socks](https://github.com/xjasonlyu/tun2socks) tun2socks - powered by gVisor TCP/IP stack

[WireGuard/wintun](https://github.com/WireGuard/wintun) wintun - TUN Device Driver for Windows
