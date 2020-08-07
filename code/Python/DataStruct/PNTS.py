'''
@Description: 读取pnts文件(实验)暂不考虑设计问题
@Author: longchen
@Date: 2020-07-29 09:30:28
@LastEditTime: 2020-08-01 08:05:52
'''
from Base_struct import Head, FeatureTable, BatchTable


class Pnts:
    def __init__(self, path):
        self.path = path
        self.head = Head(self.path)
        self.featureTable = FeatureTable(self.path, self.head)
        if self.head.Get_batchJsonLength():
            if 'BATCH_LENGTH' in self.featureTable.featurejson.keys():
                self.batchTable = BatchTable(
                    self.path, self.head,
                    self.featureTable.featurejson['BATCH_LENGTH'])
            else:
                self.batchTable = BatchTable(
                    self.path, self.head,
                    self.featureTable.featurejson['POINTS_LENGTH'])
        else:
            self.batchTable = None


if __name__ == "__main__":
    pnts1 = Pnts('../../data/new_UTM50/8/418/171.pnts')
    pnts2 = Pnts('../../data/UTM50_1/8/422/171.pnts')
    # print(pnts.featureTable.featureBinary[0:10])
    # print(pnts.batchTable.BatchBinary[0: 10])
    # print(pnts.featureTable.featurejson['QUANTIZED_VOLUME_OFFSET'])
    print(pnts1.featureTable.featurejson)
    print(pnts2.featureTable.featurejson)
    print(pnts1.featureTable.featureBinary)
    print(pnts2.featureTable.featureBinary)
