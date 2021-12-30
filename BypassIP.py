import requests, re


def exchange_maskint(mask_int):
    mask_int = int(mask_int)
    bin_arr = ['0' for i in range(32)]
    for i in range(mask_int):
        bin_arr[i] = '1'
    tmpmask = [''.join(bin_arr[i * 8:i * 8 + 8]) for i in range(4)]
    tmpmask = [str(int(tmpstr, 2)) for tmpstr in tmpmask]
    return '.'.join(tmpmask)


def get_ip(text):
    tmp = []
    tmp1 = re.findall('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\d{1,2}', text)
    for x in tmp1:
        tmp.append([x[:x.find('/')], exchange_maskint(x[x.find('/') + 1:])])
        text = text.replace(x, '', 1)
    tmp2 = re.findall('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', text)
    for x in tmp2:
        tmp.append([x, '255.255.255.255'])
    return tmp


def getIP(mode, target):
    if mode == 'url':
        res = requests.get(target)
        return get_ip(res.text)
    else:
        with open(target, 'r', encoding='utf-8') as f:
            text = f.read()
        return get_ip(text)


if __name__ == '__main__':
    print(getIP('file', 'ip.txt'))
