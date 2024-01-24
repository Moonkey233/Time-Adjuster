import os
import ctypes
import ctypes.util
import sys
import time
import datetime
import requests

total_count = 20
utcToLocal = +8  # Only Linux
true = True
false = False
null = ''

if sys.platform == 'win32' and not ctypes.windll.shell32.IsUserAnAdmin():
    ctypes.windll.shell32.ShellExecuteW(
        None, 'runas', sys.executable, __file__, None, 1)
    sys.exit(0)


def _win_set_time(time_tuple):
    import win32api as pywin32
    dayOfWeek = datetime.datetime(time_tuple[0], time_tuple[1], time_tuple[2],
                                  time_tuple[3], time_tuple[4], time_tuple[5], time_tuple[6]).isocalendar()[2]
    pywin32.SetSystemTime(time_tuple[0], time_tuple[1], dayOfWeek, time_tuple[2],
                          time_tuple[3], time_tuple[4], time_tuple[5], time_tuple[6])


def _linux_set_time(time_tuple):
    CLOCK_REALTIME = 0

    class timespec(ctypes.Structure):
        _fields_ = [('tv_sec', ctypes.c_long),
                    ('tv_nsec', ctypes.c_long)]
    librt = ctypes.CDLL(ctypes.util.find_library('rt'))
    ts = timespec()
    ts.tv_sec = int(time.mktime(
        datetime.datetime(*time_tuple[:6]).timetuple()))
    ts.tv_nsec = time_tuple[6] * 1000000
    librt.clock_settime(CLOCK_REALTIME, ctypes.byref(ts))


def main():
    while True:
        time_count = 0
        sum = 0
        ave = 0
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip',
            'Connection': 'keep-alive'
        }
        source = input('\n请输入时间源服务器: [0]退出 [1]淘宝 [2]京东 [3]B站\nINPUT: ')
        try:
            while (int(source) < 0 or int(source) > 3):
                source = input('输入有误, 请重新输入: [0]退出 [1]淘宝 [2]京东 [3]B站\nINPUT: ')
        except:
            continue
        if int(source) == 0:
            exit(0)
        elif int(source) == 1:
            time_url = 'http://api.m.taobao.com/rest/api3.do?api=mtop.common.getTimestamp'
            print('---淘宝时间源---\n')
        elif int(source) == 2:
            time_url = 'https://sgm-m.jd.com/h5/'
            print('---京东时间源---\n')
        else:
            time_url = 'https://app.bilibili.com/x/v2/splash/show'
            print('---B站时间源---\n')
        time.sleep(1)

        while True:
            try:
                while time_count < total_count:
                    if (time_count == 0):
                        print('开始测试延迟误差...', time_url, '\n')
                    time_timer = time.time()
                    res = requests.get(
                        url=time_url, headers=headers, timeout=0.5)
                    print('text:', res.text)
                    if int(source) == 1:
                        remote_time = float(res.json()['data']['t'])  # 淘宝
                    elif int(source) == 2:
                        remote_time = float(res.json()['timestamp'])  # 京东
                    else:
                        remote_time = float(
                            res.json()['data']['splash_request_id'][0:13])  # B站
                    d = remote_time - time_timer * 1000
                    print('ServerTime:', remote_time, '-',
                          'LocalTime', time_timer, '=', d, '\n')
                    time.sleep(0.2)
                    time_count += 1
                    sum += d
                if time_count != 0 and ave == 0:
                    ave = sum / time_count / 1000
                    print('Ave:', ave * 1000, 'ms')
                    break
            except:
                print('\n计算误差异常')
                ave = 0
                break

        time_tuple = [2022, 8, 27, 11, 0, 0, 0]
        timeStamp = time.time() + ave
        dateArray = str(datetime.datetime.utcfromtimestamp(timeStamp))
        print(dateArray, 'UTC')
        time_tuple[0] = int(dateArray[0:4])
        time_tuple[1] = int(dateArray[5:7])
        time_tuple[2] = int(dateArray[8:10])
        time_tuple[3] = int(dateArray[11:13])
        time_tuple[4] = int(dateArray[14:16])
        time_tuple[5] = int(dateArray[17:19])
        time_tuple[6] = int(dateArray[20:23])
        print(time_tuple)
        if abs(ave) >= 5:
            print('\n---时差过大, 请再次运行---\n')
        if sys.platform == 'linux2' or sys.platform == 'linux':
            if (utcToLocal >= 0):
                print(f'\nLinux UTC +{utcToLocal}')
            else:
                print('\nLinux UTC', utcToLocal)
            time_tuple[3] += utcToLocal
            _linux_set_time(time_tuple)
        elif sys.platform == 'win32' or sys.platform == 'win64':
            print('\nWindows')
            _win_set_time(time_tuple)
        print('时间修改成功:', timeStamp, time.strftime(
            '%Y-%m-%d %H:%M:%S', time.localtime(timeStamp)))
        input('Press ENTER to continue...')


if __name__ == '__main__':
    main()
