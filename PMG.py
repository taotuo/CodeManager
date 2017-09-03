#-*- coding：utf-8 -*-
from Utils import loadFile, writeFile, randomStrGenerator
from pyDes import *
import numpy as np
import base64
import os
import random

class PMG(object):
    def __init__(self, PW, Encoder=True, K = 2, Key= 'DESCRYPT', IV = '12345678', W=None):
        self.des_worker = des(Key, CBC, IV, pad=None, padmode=PAD_PKCS5)
        self.W = W
        self.PW = PW
        self.K = K
        self.Encoder = Encoder
        if not Encoder:
            self.Y = np.mat(np.array([PW.split('+')[0].split('-')]).astype(np.int64))
            self.K = self.Y.shape[1]
            self.ID = PW.split('+')[-1]
        self.ASCII_Dict = dict()
    def _ASCIIEncoder(self, STR):
        ascii_list = []
        for s in STR:
            ascii_list.append(ord(s))
        return ascii_list
    def _ASCIIDecoder(self, ASCII_LIST):
        return_str = ''
        for ascii_char in ASCII_LIST:
            return_str += chr(ascii_char)
        return return_str
    def _HexEncoder(self, INT):
        return hex(INT)
    def _HexDecoder(self, HEX):
        return int(HEX, 16)
    def _DESEncoder(self, STR):
        return self.des_worker.encrypt(STR)
    def _DESDecoder(self, DES_STR):
        return self.des_worker.decrypt(DES_STR, padmode=PAD_PKCS5).decode("utf-8")
    def _MatrixEncoder(self, X, W):
        if W is None:
            raise 'Matrix Encode Fails!'
        else:
            return np.dot(X, W)
    def _MatrixDecoder(self, Y, W):
        if W is None:
            raise 'Matrix Decode Fails!'
        else:
            return np.dot(Y, W)
    def _GenerateGDMM(self, Y, ID):
        str_y = ''
        for i in range(Y.shape[1]):
            str_y += '%d-' % (Y[0, i])
        return str_y[:-1] + '+' + ID
    def Operation(self, file_path=None):
        if self.Encoder:
            if file_path is not None and os.path.exists(file_path):
                self.ASCII_Dict = loadFile(file_path)
            ASCII_List = self._ASCIIEncoder(self.PW)
            HEX_STR = ''
            for ASCII_Num in ASCII_List:
                HEX_STR += self._HexEncoder(ASCII_Num) + '-'
            DES_STR = self._DESEncoder(HEX_STR)
            DES_STR = base64.b64encode(DES_STR).decode()
            while True:
                random_id = random.randint(1000, 9999)
                if str(random_id) not in self.ASCII_Dict.keys():
                    random_id = str(random_id)
                    break
            self.ASCII_Dict[random_id] = (DES_STR[:-self.K])
            writeFile(self.ASCII_Dict, file_path)
            ASCII_STR = DES_STR[-self.K:]
            X = np.array([self._ASCIIEncoder(ASCII_STR)])
            Y = self._MatrixEncoder(X, self.W[self.K])
            return self._GenerateGDMM(Y, random_id)
        else:
            '''Do Something...'''
            X = self._MatrixDecoder(self.Y, self.W[self.K].I)
            X = X.tolist()[0]
            X = [int(i) for i in X]
            ASCII_STR = self._ASCIIDecoder(X)
            ASCII_Dict = loadFile(file_path)
            DES_STR = ASCII_Dict[self.ID] + ASCII_STR
            DES_STR = base64.b64decode(DES_STR)
            HEX_STR = self._DESDecoder(DES_STR)
            HEX_STR_List = HEX_STR.split('-')[:-1]
            ASCII_List = []
            for hex_str in HEX_STR_List:
                ASCII_List.append(self._HexDecoder(hex_str))
            return self._ASCIIDecoder(ASCII_List)

def randWeightInitial(Num, FilePath):
    if os.path.exists(FilePath):
        os.remove(FilePath)
    W = dict()
    for i in range(Num):
        W[i+1] = np.mat(np.diag(np.random.randint(1,10,i+1)))
    writeFile(W, FilePath)
    return W

def randDictInitial(Key, IV, W, Num, FilePath):
    if os.path.exists(FilePath):
        os.remove(FilePath)
    for i in range(Num):
        pw = randomStrGenerator()
        K = random.randint(1, 5)
        encode_worker = PMG(pw, Key=Key, IV=IV, Encoder=True, K=K, W=W)
        encode_worker.Operation(FilePath)

def main():
    Key = input('Please input Key (Must be 8-bit):')
    IV = input('Please input IV (Must be 8-bit):')
    Encode = input('Please input Y/N to indicate whether to encode (Y/y) or decode (N/n):')
    while True:
        if Encode == 'Y' or Encode == 'y':
            Pwd = input('Please input a password:')
            randWeightInit = input('Please input Y/N to indicate whether to initialize weight (Y/y) or load from existing file (N/n):')
            if randWeightInit == 'Y' or randWeightInit == 'y':
                num = input('Please input number steps:')
                Fipath = input('Please input weights filename to save:')
                W = randWeightInitial(int(num), Fipath)
            elif randWeightInit == 'N' or randWeightInit == 'n':
                Fipath = input('Please input weights filename to load:')
                W = loadFile(Fipath)
            else:
                print('Weight initialization fails')
                break
            randDictInit = input('Please input Y/N to indicate whether to initialize dict (Y/y) or load from existing file (N/n):')
            if randDictInit == 'Y' or randWeightInit == 'y':
                num = input('Please input number steps:')
                Fipath = input('Please input dict filename to save:')
                randDictInitial(Key=Key, IV=IV, W=W, Num=int(num), FilePath=Fipath)
            elif randDictInit == 'N' or randWeightInit == 'n':
                Fipath = input('Please input dict filename to load:')
                if not os.path.exists(Fipath):
                    print('Dict initialization fails')
                    break
            else:
                print('Dict initialization fails')
                break
            encode_worker = PMG(Pwd, Key=Key, IV=IV, Encoder=True, K=1, W=W)
            gdmm = encode_worker.Operation(Fipath)
            Check = input('Please input Y/y to indicate whether to check decoded password:')
            if Check == 'Y' or Check == 'y':
                decoder_worker = PMG(gdmm, Key=Key, IV=IV, Encoder=False, W=W)
                pw = decoder_worker.Operation(Fipath)
                print('Decode Password is %s - Equal:' % (pw), pw == Pwd)
                print('Encode Password is %s' % (gdmm))
            else:
                print('Encode Password is %s' % (gdmm))
            break
        elif Encode == 'N' or Encode == 'n':
            gdmm = input('Please input a encoded password:')
            Fipath = input('Please input weights filename to load:')
            if not os.path.exists(Fipath):
                print('Weight initialization fails')
                break
            W = loadFile(Fipath)
            Fipath = input('Please input dict filename:')
            if not os.path.exists(Fipath):
                print('Dict initialization fails')
                break
            decoder_worker = PMG(gdmm, Key=Key, IV=IV, Encoder=False, W=W)
            pw = decoder_worker.Operation(Fipath)
            print('Original password is %s' % (pw))
            break
        else:
            print('Your input is incorrect, please re-input:')
            Encode = input('Please input a boolean value to indicate whether to encode (Y) or decode(N):')

if __name__ == '__main__':
    main()
