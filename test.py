
import os
import shutil

import paramiko


def host_all():
    output = os.system('echo "123456" | sudo -S ifconfig ens33:0 192.168.141.188/24 up')
    print(output)


def file_all(aa):
    output = os.system('sshpass -p "123456" scp %s root@172.16.1.171:/home/srv' % aa)
    print(output)


def test_all():

    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.connect("172.16.1.171", username="root", password="123456")
    _, stdout, _ = client.exec_command("[ -f /home/srv/mynginx.tar ] && echo OK")

    print(stdout.read())
    client.close()


if __name__ == '__main__':
    aa = '/tmp/pycharm_project_717/contests/jing/mynginx.tar'
    remote = '//172.16.1.171/home/srv/mynginx.tar'

    # file_all(aa)

    test_all()


