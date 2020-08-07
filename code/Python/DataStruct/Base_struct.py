'''
@Description: 创建一些基础类型
@Author: longchen
@Date: 2020-07-29 09:38:03
@LastEditTime: 2020-07-31 20:22:17
'''
import os
import json
import struct


class Head():
    def __init__(self, path, start=0):
        file_type = os.path.splitext(path)[-1][1:]
        if file_type == 'pnts':
            f = open(path, 'rb')
            f.seek(start)
            header = f.read(28)
            # 读取28个字节
            header_list = struct.unpack('cIIIIII', header)
            self.magic = header_list[0]
            self.version = header_list[1]
            self.__byteLength = header_list[2]
            self.__featureTableJSONByteLength = header_list[3]
            self.__featureTableBinaryLength = header_list[4]
            self.__batchTableJSONByteLength = header_list[5]
            self.__batchTableBinaryLength = header_list[6]
            f.close()

    def Get_byteLength(self):
        return self.__byteLength

    def Get_fbJsonLength(self):
        return self.__featureTableJSONByteLength

    def Get_fbBinaryLength(self):
        return self.__featureTableBinaryLength

    def Get_batchJsonLength(self):
        return self.__batchTableJSONByteLength

    def Get_batchBinaryLength(self):
        return self.__batchTableBinaryLength

    def write_head(self, path):
        f = open(path, 'wb')
        f.write(
            struct.pack('cIIIIII', self.magic, self.version, self.__byteLength,
                        self.__featureTableJSONByteLength,
                        self.__featureTableBinaryLength,
                        self.__batchTableJSONByteLength,
                        self.__batchTableBinaryLength))
        f.close()


class FeatureTable():
    def __init__(self, path, head):
        file_type = os.path.splitext(path)[-1][1:]
        if file_type == 'pnts':
            JsonLength = head.Get_fbJsonLength()
            BinaryLength = head.Get_fbBinaryLength()
            # 获取长度信息
            f = open(path, 'rb')
            f.seek(28)
            # 跳过文件头
            featurejson = f.read(JsonLength)
            featureBinary = f.read(BinaryLength)
            self.featurejson = json.loads(
                struct.unpack('{}s'.format(JsonLength), featurejson)[0])
            self.GetBinary(featureBinary)
            f.close()

    def GetBinary(self, featureBinary):
        Table = {
            'POSITION': ['fff', 12],
            'RGB': ['BBB', 3],
            'POSITION_QUANTIZED': ['HHH', 6],
            'RGBA': ['BBBB', 4],
            'RGB565': ['H', 2],
            'NORMAL': ['fff', 12],
            'NORMAL_OCT16P': ['HH', 4],
            'BATCH_ID': ['B', 1]
        }
        keys = self.featurejson.keys()
        # 获取要素表中的声明
        Length = self.featurejson['POINTS_LENGTH']
        self.featureBinary = []
        for i in range(Length):
            data = {}
            self.featureBinary.append(data)
        # 定义这样一个列表，不使用[{}] * Length的方式，是为了不共享内存
        Attributes = [
            key for key in keys
            if type(self.featurejson[key]).__name__ == 'dict'
        ]
        # 默认是按照顺序进行过排列
        Attributes = sorted(
            Attributes,
            key=lambda attribute: self.featurejson[attribute]['byteOffset'])
        ALength = len(Attributes)
        for i in range(ALength):
            unpack_type = Table[Attributes[i]][0]
            diff = Table[Attributes[i]][1]
            if i != ALength - 1:
                start = self.featurejson[Attributes[i]]['byteOffset']
                end = self.featurejson[Attributes[i + 1]]['byteOffset']
                data = featureBinary[start:end]
                # diff = (end - start) // Length
            else:
                start = self.featurejson[Attributes[i]]['byteOffset']
                data = featureBinary[start:]
                # diff = (len(featureBinary) - start) // Length
            for j in range(Length):
                self.featureBinary[j][Attributes[i]] = list(
                    struct.unpack(unpack_type, data[j * diff:(j + 1) * diff]))
        # 读取完数据


class BatchTable():
    def __init__(self, path, head, batch_length=1):
        file_type = os.path.splitext(path)[-1][1:]
        if file_type == 'pnts':
            JsonLength = head.Get_batchJsonLength()
            BinaryLength = head.Get_batchBinaryLength()
            f = open(path, 'rb')
            f.seek(28 + head.Get_fbJsonLength() + head.Get_fbBinaryLength())
            # 将指针移到相应位置
            featurejson = f.read(JsonLength)
            featureBinary = f.read(BinaryLength)
            self.length = batch_length
            self.featurejson = json.loads(
                struct.unpack('{}s'.format(JsonLength), featurejson)[0])
            self.GetBinary(featureBinary)
            f.close()

    def GetBinary(self, featureBinary):
        Table = {
            'FLOAT': ['f', 4],
            'DOUBLE': ['d', 8],
            'UNSIGNED_INT': ['I', 4],
            'UNSIGNED_SHORT': ['H', 2],
            'UNSIGNED_BYTE': ['B', 1],
            'BYTE': ['b', 1]
        }
        self.BatchBinary = []
        keys = self.featurejson.keys()
        if 'name' in keys:
            for i in range(self.length):
                data = {}
                data['name'] = self.featurejson['name'][i]
                self.BatchBinary.append(data)
        else:
            for i in range(self.length):
                data = {}
                self.BatchBinary.append(data)
        # 命名
        Attributes = [
            key for key in keys
            if key != 'name' and 'byteOffset' in self.featurejson[key].keys()
        ]
        Attributes = sorted(
            Attributes,
            key=lambda attribute: self.featurejson[attribute]['byteOffset'])
        ALength = len(Attributes)
        for i in range(ALength):
            attribute = Attributes[i]
            dtype = self.featurejson[attribute]['type'][-1]
            cType = Table[self.featurejson[attribute]['componentType']][0]
            diff = Table[self.featurejson[attribute]['componentType']][1]
            if dtype < '9' and dtype > '0':
                struct_type = ''.join([cType] * int(dtype))
                diff = diff * int(dtype)
            else:
                struct_type = cType
            # 定义好unpack的类型
            if i != ALength - 1:
                start = self.featurejson[Attributes[i]]['byteOffset']
                end = self.featurejson[Attributes[i + 1]]['byteOffset']
                data = featureBinary[start:end]
                # diff = (end - start) // self.length
            else:
                start = self.featurejson[Attributes[i]]['byteOffset']
                data = featureBinary[start:]
                # diff = (len(featureBinary) - start) // self.length
            for j in range(self.length):
                self.BatchBinary[j][Attributes[i]] = list(
                    struct.unpack(struct_type, data[j * diff:(j + 1) * diff]))


if __name__ == "__main__":
    file_name = '../../data/Titles/pnts/pointCloudRGB.pnts'
    header = Head(file_name)
    featuretable = FeatureTable(file_name, header)
    batchtable = BatchTable(file_name, header)
    print(featuretable.featureBinary[0:10])
    print(batchtable.featurejson, batchtable.BatchBinary[0:8])
    # print(featuretable.featureBinary[0:10])
