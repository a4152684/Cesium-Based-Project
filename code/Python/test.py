'''
@Description: las文件处理
@Author: longchen
@Date: 2020-07-26 11:15:19
LastEditTime: 2020-08-07 10:37:50
'''
from laspy import file


def getGeometryID(file_name):
    f = file.File(file_name, mode='r')
    head = f.header
    vlrs = head.vlrs
    if len(vlrs) == 0:
        print('没有定义投影坐标系')
        return None
    else:
        vlrs = vlrs[0]
        data = vlrs.parsed_body
        wNumber = data[3]
        for i in range(wNumber):
            wKeyId = data[4 + 4 * i]
            if wKeyId == 3072 or wKeyId == 4095:
                return data[7 + 4 * i]


file_name = '../data/武汉大学-车载点云/test.las'
print(getGeometryID(file_name))
