import cv2
import os
import numpy as np
from sklearn.model_selection import train_test_split
from torch.utils.data import Dataset
from torch.utils.data import DataLoader


def transform_img(image, thr):
    image[image > thr] = 255
    image[image <= thr] = 0
    return image


def data_prep(path, suffix='/'):
    list_post_treat = os.listdir(path)
    scans = []
    for filename_post in sorted(list_post_treat):
        images = []
        for group in [0, 1]:
            image_name = sorted(os.listdir(path + suffix + filename_post))[group]
            image_path = path + suffix + filename_post + suffix + image_name
            image = cv2.imread(image_path, 0)
            image = transform_img(image, 100)
            image = cv2.resize(image, (128, 128))  # .astype(float)/255.0-0.5
            # adding dimension because the model expects 3D input
            image = image.reshape(1, image.shape[0], image.shape[1])
            images.append(image)
        scans.append([filename_post, images])
    return np.asarray(scans)


class GroupData:
    def __init__(self, path):
        self.data = data_prep(path)
        self.train = None
        self.val = None

    def my_train_test_split(self, split_rate, constant_split=None):
        self.train, self.val = train_test_split(self.data, test_size=split_rate)

    def get_train_val_labels(self):
        return self.train, self.val


class TwoGroupDataset(Dataset):
    def __init__(self, data):
        self.data = data

    def __len__(self):
        return len(self.data)

    def __getitem__(self, item):
        subject = self.data[item][0]
        data = self.data[item][1]
        x = data[0]
        y = data[1]
        return subject, x, y


def get_train_test_loaders(path, split_rate, batch_size):
    my_data = GroupData(path)
    my_data.my_train_test_split(split_rate)
    train, val = my_data.get_train_val_labels()
    train_set = TwoGroupDataset(train)
    val_set = TwoGroupDataset(val)
    train_data_loader = DataLoader(train_set, batch_size=batch_size, shuffle=True)
    val_data_loader = DataLoader(val_set, batch_size=batch_size, shuffle=True)
    return train_data_loader, val_data_loader