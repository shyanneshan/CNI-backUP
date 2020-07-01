import numpy as np


class CRC:

    def __init__(self, info_list, crc_n=32):
        self.info_list = info_list

        # 初始化生成多项式p
        loc = [32, 26, 23, 22, 16, 12, 11, 10, 8, 7, 5, 2, 1, 0]
        p = [0 for i in range(crc_n + 1)]
        for i in loc:
            p[i] = 1

        info_list = self.info_list.copy()
        times = len(info_list)
        n = crc_n + 1

        # 左移补零
        for i in range(crc_n):
            info_list.append(0)
        # 除
        q = []
        for i in range(times):
            if info_list[i] == 1:
                q.append(1)
                for j in range(n):
                    info_list[j + i] = info_list[j + i] ^ p[j]
            else:
                q.append(0)

        # 余数
        check_code = info_list[-crc_n::]

        # 生成编码
        code_list = self.info_list.copy()
        for i in check_code:
            code_list.append(i)

        self.crc_n = crc_n
        self.p = p
        self.q = q
        self.check_code = check_code
        self.code_list = code_list


def encode_crc(data):
    crc = CRC(data, 32)
    return crc


def check(data):

    check_code = CRC(data, 32).check_code

    # print('检验余数：', ''.join('%s' % id for id in check_code))

    flag = 0
    for i in range(len(check_code)):
        if check_code[i] == 1:
            flag = 1
            break
    return flag

'''
    def print(self):
        info_str = ''.join('%s' % id for id in self.info_list)
        code_str = ''.join('%s' % id for id in self.code_list)
        p_str = ''.join('%s' % id for id in self.p)
        q_str = ''.join('%s' % id for id in self.q)
        check_code_str = ''.join('%s' % id for id in self.check_code)

        print('信息：', info_str)
        print('生成多项式：', p_str)
        print('商：', q_str)
        print('余数：', check_code_str)
        print('编码：', code_str)
'''


