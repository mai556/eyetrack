import pandas as pd
import os
import re
import numpy as np
import random
import cv2 as cv
from time import time
import multiprocessing
from torch.utils.data import Dataset, DataLoader
import torch
import world
from utils import ToTensor
import matplotlib.pyplot as plt


W = 480
H = 640
C = 1

cores = multiprocessing.cpu_count() // 2
cores = 1 if cores == 0 else cores

class dataloader(Dataset):
    def __init__(self, datapath = '../data', mode="train", transform=None, folder=None):
        assert mode in ["train", "test", "val"]
        self.data_path = os.path.join(datapath, mode)
        self.mode = mode
        self.folder = folder
        self.labels, self.data, self.length = self.getDataIndex()
        # self.mean, self.std = self.getStat()
        self.transform = transform if transform is not None else ToTensor()

    def getDataIndex(self):
        from glob import glob
        if self.folder is None:
            table = glob(os.path.join(self.data_path, "*/*/Learn.csv"))
        else:
            table = glob(os.path.join(self.data_path, "%s/*/Learn.csv" % str(self.folder)))
        eyesXY = {}
        total = 0
        for i in table:
            data = pd.read_csv(i)
            data = data[["cornerxy[0]", "cornerxy[1]"]]
            i = os.path.dirname(i)
            if world.useSigmoid:
                eyesXY[i] = data.to_numpy()/world.label_scalar
                # print(">SCALAR labels by", world.label_scalar)
            else:
                eyesXY[i] = data.to_numpy()
            # print("max is", np.max(eyesXY[i], axis=0))
            # print("min is", np.min(eyesXY[i], axis=0))
            total += eyesXY[i].shape[0]
            print(">GOT %s DATA FROM" % eyesXY[i].shape[0] , i)
        order = []
        plot_dist = None
        for i in list(eyesXY):
            length = eyesXY[i].shape[0]
            order += [ os.path.join(i, str(j)) for j in range(1, length+1)]
            if plot_dist is None:
                plot_dist = eyesXY[i]
            else:
                plot_dist = np.vstack([plot_dist, eyesXY[i]])
        # print(">MEAN", np.mean(plot_dist*np.array([800,600]), axis=0))
        # print(">STD", np.std(plot_dist*np.array([800,600]), axis=0))
        # plt.scatter(plot_dist[:,0], plot_dist[:,1], s=5,c="black")
        # plt.xlabel("width")
        # plt.ylabel("height")
        # plt.grid()
        # plt.savefig("/output/" + self.mode+".png")
        # plt.close()
        # plt.scatter(plot_dist[:,0]*800, plot_dist[:,1]*600, s=5,c="black")
        # plt.xlabel("width")
        # plt.ylabel("height")
        # plt.grid()
        # plt.savefig("/output/" + self.mode+"_before.png")
        # plt.close()
        # random.shuffle(order)
        try:
            assert len(order) == total
        except AssertionError:
            raise AssertionError("%s %s, wrong in loading data" % (len(order), total))
        print(">TOTAL %s DATA:" % self.mode, len(order))
        return eyesXY, order, total

    def getStat(self, sep = 500):
        pool = multiprocessing.Pool(cores)
        data = []
        before = 0
        for i in range(sep, len(self.data)+1, sep):
            data.append(self.data[before:i])
            before = i
        data.append(self.data[before:])
        print("mapping", list(map(len, data)), "to", "%d cpus"%(cores))
        res = pool.map(self._getOneStat, data)
        print(res)
        mean1 = 0
        std1 = 0
        for i in res:
            mean1 = mean1 + i[0]
            std1 = std1 + i[1]
        return mean1/self.length, (std1/self.length)**0.5


    def _getOneStat(self, data):
        mean1 = 0
        std1 = 0
        now = time()
        for i in data:
            mean2 = 0
            std2 = 0
            for j in ["_%d.png" % k for k in [0, 1, 3,4]]:
                eye = cv.imread(i+j)
                eye = eye[...,0]
                mean2 = mean2 + np.mean(eye)
                std2 = std2 + np.std(eye)**2
            mean1 = mean1 + mean2/4
            std1 = std1 + std2/4
        print("cost %.2fs to compute statistics " % (time()-now))
        print(mean1, std1)
        return mean1, std1

    def getLabel(self, filename):
        index = int(os.path.basename(filename))
        # print(idne/x)
        label = self.labels[os.path.dirname(filename)]
        if label is None:
            raise TypeError(">GOT a filename is %s, which didn't exist" % (filename))
        return label[index-1]

    def getSample(self):
        res = {}
        filename = self.data[idx]
        # print(filename)
        for j, name in enumerate(["%s_%d.png" % (filename, k) for k in [0, 1, 3,4]]):
            res["img" + str(j)] = cv.imread(name)[..., 0:1]
        res["label"] = self.getLabel(filename)
        return res


    def __len__(self):
        return self.length

    def __getitem__(self, idx):
        res = {}
        filename = self.data[idx]
        # print(filename)
        if world.resize:
            for j, name in enumerate(["%s_%d_256.png" % (filename, k) for k in [0, 1, 3,4]]):
                try:
                    res["img" + str(j)] = cv.imread(name)[..., 0:1]
                except:
                    print("No such png file:", name)
                    raise TypeError("File didn't exist")
        else:
            for j, name in enumerate(["%s_%d.png" % (filename, k) for k in [0, 1, 3,4]]):
                try:
                    res["img" + str(j)] = cv.imread(name)[..., 0:1]
                except:
                    print("No such png file:", name)
                    raise TypeError("File didn't exist")
        res["label"] = self.getLabel(filename)
        if self.transform:
            res = self.transform(res)
        else:
            pass
        return res




if __name__ == "__main__":
    loader = dataloader()
    print(loader[100]["img0"].size(),loader[100]["label"])
