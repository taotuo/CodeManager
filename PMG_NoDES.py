#-*- coding：utf-8 -*-
from Utils import loadFile, writeFile, randomStrGenerator
import numpy as np
import base64
import os
import random

class PMG_NoDES(object):
    def __init__(self, PW, Encoder=True, K = 2, W=None):
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

            HEX_STR = HEX_STR[:-1]
            BASE64_STR = base64.b64encode(HEX_STR.encode()).decode()

            while True:
                random_id = random.randint(1000, 9999)
                if str(random_id) not in self.ASCII_Dict.keys():
                    random_id = str(random_id)
                    break
            self.ASCII_Dict[random_id] = (BASE64_STR[:-self.K])
            writeFile(self.ASCII_Dict, file_path)
            ASCII_STR = BASE64_STR[-self.K:]
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
            BASE64_STR = ASCII_Dict[self.ID] + ASCII_STR
            HEX_STR = base64.b64decode(BASE64_STR).decode()
            HEX_STR_List = HEX_STR.split('-')
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

def randDictInitial(W, Num, FilePath):
    if os.path.exists(FilePath):
        os.remove(FilePath)
    for i in range(Num):
        pw = randomStrGenerator()
        K = random.randint(1, 5)
        encode_worker = PMG_NoDES(pw, Encoder=True, K=K, W=W)
        encode_worker.Operation(FilePath)

def main():
    Encode = input('Please input Y/N to indicate whether to encode (Y/y) or decode (N/n):')
    while True:
        if Encode == 'Y' or Encode == 'y':
            Pwd = input('Please input a password:')
            randWeightInit = input('Please input Y/N to indicate whether to initialize weight (Y/y) or load from existing file (N/n):')
            if randWeightInit == 'Y' or randWeightInit == 'y':
                num = input('Please input number steps:')
                W = randWeightInitial(int(num), 'UKey')
            elif randWeightInit == 'N' or randWeightInit == 'n':
                W = loadFile('UKey')
            else:
                print('Weight initialization fails')
                break

            randDictInit = input('Please input Y/N to indicate whether to initialize dict (Y/y) or load from existing file (N/n):')
            if randDictInit == 'Y' or randWeightInit == 'y':
                num = input('Please input number steps:')
                randDictInitial(W=W, Num=int(num), FilePath='UDict')
            elif randDictInit == 'N' or randWeightInit == 'n':
                if not os.path.exists('UDict'):
                    print('Dict initialization fails')
                    break
            else:
                print('Dict initialization fails')
                break

            K = input('Please input encoded passwords complexity(int:1-9):')
            encode_worker = PMG_NoDES(Pwd, Encoder=True, K=int(K), W=W)
            gdmm = encode_worker.Operation('UDict')
            Check = input('Please input Y/y to indicate whether to check decoded password:')
            if Check == 'Y' or Check == 'y':
                decoder_worker = PMG_NoDES(gdmm, Encoder=False, W=W)
                pw = decoder_worker.Operation('UDict')
                print('Decode Password is %s - Equal:' % (pw), pw == Pwd)
                print('Encode Password is %s' % (gdmm))
            else:
                print('Encode Password is %s' % (gdmm))
            break
        elif Encode == 'N' or Encode == 'n':
            gdmm = input('Please input a encoded password:')
            if not os.path.exists('UKey'):
                print('Weight initialization fails')
                break
            W = loadFile('UKey')
            if not os.path.exists('UDict'):
                print('Dict initialization fails')
                break
            decoder_worker = PMG_NoDES(gdmm, Encoder=False, K=1, W=W)
            pw = decoder_worker.Operation('UDict')
            print('Original password is %s' % (pw))
            break
        else:
            print('Your input is incorrect, please re-input:')
            Encode = input('Please input a boolean value to indicate whether to encode (Y) or decode(N):')

if __name__ == '__main__':
    main()
