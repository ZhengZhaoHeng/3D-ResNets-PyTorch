import torch
import torch.utils.data as data
import json
import random
from PIL import Image
import numpy as np

import os

def pil_loader(path):
    # open path as file to avoid ResourceWarning (https://github.com/python-pillow/Pillow/issues/835)
    with open(path, 'rb') as f:
        with Image.open(f) as img:
            return img.convert('RGB')

def load_annotation_data(data_file_path):
    with open(data_file_path, 'r') as data_file:
        return json.load(data_file)

class Synthetic(data.Dataset):
    
    def __init__(self, 
                 annotation_path,
                 subset,
                 n_frame=120,
                 transform=None):
        
        self.data = load_annotation_data(annotation_path)
        self.n_frame = n_frame
        self.datapath = self.data['datapath']
        self.data = self.data[subset]
        self.transform = transform

    def __getitem__(self, index):
        
        video_id = self.data[index]['id']
        label = self.data[index]['label']
        video_path = os.path.join(self.datapath, video_id)

        frame_id = random.randrange(self.n_frame)
        last_frame_id = max(0, frame_id - 24)
        next_frame_id = min(self.n_frame - 1, frame_id + 24)

        last_img = np.array(pil_loader(os.path.join(video_path, "{}_{:06d}.png".format(video_id, last_frame_id))))
        cur_img = np.array(pil_loader(os.path.join(video_path, "{}_{:06d}.png".format(video_id, frame_id))))
        next_img = np.array(pil_loader(os.path.join(video_path, "{}_{:06d}.png".format(video_id, next_frame_id))))

        last_grayscale = np.mean(last_img, axis=2)
        cur_grayscale = np.mean(cur_img, axis=2)
        next_grayscale = np.mean(next_img, axis=2)

        fused = np.stack([last_grayscale, cur_grayscale, next_grayscale], axis=2).astype(np.uint8)
        
        img = Image.fromarray(fused)

        if self.transform:
            img = self.transform(img)

        return img, label

    def __len__(self):
        return len(self.data)


if __name__ == '__main__':
    
    dataset = Synthetic('../annotation.json', 'training')

    for i in range(10):
        print (dataset.__getitem__(random.randrange(dataset.__len__())))


