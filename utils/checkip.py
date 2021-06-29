

import os


def ping_all(ip):
    p_w = 'c'
    output = os.popen('ping -%s 1 %s' % (p_w, ip)).readlines()
    for w in output:
        if str(w).upper().find('TTL') >= 0:
            return True
    return False


def add_ip(ip):
    try:
        output = os.popen('ifconfig ens33:0 %s/24 up' % ip)
    except Exception as e:
        return False
    return True


if __name__ == '__main__':
    ping_all('192.168.141.188')
