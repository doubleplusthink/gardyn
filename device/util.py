# coding=utf-8
import os
import socket
from config import REMOTE_SERVER

def guarantee_dir(path):
    """
        split path by os.sep("/" or "\")
        loop from the beginning of paths 
        make sure each path exisits
        create one if not
    """
    paths = path.split(os.sep)
    try:
        for index in range(len(paths)):
            if not paths[index]:
                # use continue instead of break because the paths[0] may be empty sometimes
                continue
            curr = os.sep.join(paths[0:index+1])
            if not os.path.isdir(curr):
                os.mkdir(curr)
    except Exception:
        raise SystemError(message=path)
    finally:
        return path


def save_as_file(path, name, data):
    guarantee_dir(path)
    f_ssid = open(os.path.join(path, name), 'w')
    f_ssid.write(data)
    f_ssid.close()


def read_from_file(path, name):
    guarantee_dir(path)
    f = os.path.join(path, name)
    if os.path.isfile(f):
        with open(f, 'r') as fp:
            data = fp.read()
            if not data:
                return ''
            data = data.splitlines()[0]            
            return data
    return ''

def median(d):
    if type(d) != list:
        return ''
    s = sorted(d)
    l = len(d)
    return s[(int(l / 2)) : (int(l / 2) + 1)] if l % 2 > 0 else s[(int(l / 2) - 1) : (int(l / 2) + 1)]

def get_serial():
    fp = os.popen("cat /proc/cpuinfo | grep Serial | cut -d ' ' -f 2 | md5sum | cut -d ' ' -f 1")
    serial = fp.read().splitlines()[0]
    fp.close()
    return serial

def is_connected():
    try:
        host = socket.gethostbyname(REMOTE_SERVER)
        s = socket.create_connection((host, 80), 2)
        return True
    except:
        pass
    return False

# if __name__ == '__main__':
#     print(is_connected())