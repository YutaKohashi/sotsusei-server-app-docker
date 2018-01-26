#ファイル操作ユーティリティ
import os

def mkdir(path, dirname):
    if not os.path.isdir(path + "/" + dirname):
        os.makedirs(path + "/" + dirname)

def isExistDir(path, dirname):
    return True

def deldir(path):
    pass