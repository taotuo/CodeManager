import _pickle as cPickle
import random
import string

def loadFile(File_path):
    with open(File_path, 'rb') as f:
        return cPickle.load(f)

def writeFile(File, File_path):
    with open(File_path, 'wb') as f:
        return cPickle.dump(File, f)

def randomStrGenerator(N=1):
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(N))
