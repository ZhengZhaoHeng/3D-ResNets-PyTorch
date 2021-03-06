import torch
import torch.utils.data as data
from PIL import Image
import os
import math
import functools
import json
import copy
import numpy as np
import random
import torchfile

from utils import load_value_file

def pil_loader(path):
    # open path as file to avoid ResourceWarning (https://github.com/python-pillow/Pillow/issues/835)
    with open(path, 'rb') as f:
        with Image.open(f) as img:
            return img.convert('RGB')

def lua_loader(path):
    stuff = np.rollaxis(torchfile.load(path), 0, 3).astype(np.float32)
    if stuff.shape[2] == 1:
        stuff = stuff - stuff.min()
        stuff = stuff / stuff.max()
        stuff *= 255
        stuff = np.tile(stuff, (1, 1, 3))
    else:
        stuff = (stuff + 1) * 255 / 2

    return Image.fromarray(stuff.astype(np.uint8))


def accimage_loader(path):
    try:
        import accimage
        return accimage.Image(path)
    except IOError:
        # Potentially a decoding problem, fall back to PIL.Image
        return pil_loader(path)


def get_default_image_loader(image_type):
    if image_type == 'rgb':
        return pil_loader
    else:
        return lua_loader

def get_default_video_loader(image_type):
    image_loader = get_default_image_loader(image_type)
    return functools.partial(video_loader, image_loader=image_loader)

def video_loader(frame_indices, img_list, channel_fuse_step, image_loader):
    video = []
    for i in frame_indices:
        image_path = img_list[i-1]
        if os.path.exists(image_path):
            cur_frame = image_loader(image_path)

            '''
            if channel_fuse_step > 0:
                assert False
                last_image_path = os.path.join(video_dir_path, '{}_{:06d}.png'.format(video_dir_path[-6:], i - 1 - channel_fuse_step))
                next_image_path = os.path.join(video_dir_path, '{}_{:06d}.png'.format(video_dir_path[-6:], i - 1 + channel_fuse_step))

                if not os.path.exists(last_image_path):
                    last_frame = cur_frame
                else:
                    last_frame = image_loader(last_image_path)
                
                if not os.path.exists(next_image_path):
                    next_frame = cur_frame
                else:
                    next_frame = cur_frame

                cur_frame = np.array(cur_frame)
                last_frame = np.array(last_frame)
                next_frame = np.array(next_frame)

                cur_frame[:, :, 0] = last_frame[:, :, 0]
                cur_frame[:, :, 2] = next_frame[:, :, 2]

                cur_frame = Image.fromarray(cur_frame)
                video.append(cur_frame)
            else:
            '''
            video.append(cur_frame)
        else:
            return video

    return video


def load_annotation_data(data_file_path):
    with open(data_file_path, 'r') as data_file:
        return json.load(data_file)


def get_class_labels(data):
    class_labels_map = {}
    index = 0
    for class_label in data['labels']:
        class_labels_map[class_label] = index
        index += 1
    return class_labels_map

def get_video_names_and_annotations(data, subset):
    return [entry['id'] for entry in data[subset]], [entry for entry in data[subset]]


def make_dataset(root_path, annotation_path, subset, n_samples_for_each_video,
                 sample_duration, sample_step, image_type):
    data = load_annotation_data(annotation_path)
    video_names, annotations = get_video_names_and_annotations(data, subset)
    class_to_idx = get_class_labels(data)
    idx_to_class = {}
    for name, label in class_to_idx.items():
        idx_to_class[label] = name

    dataset = []
    for i in range(len(video_names)):
        if i % 1000 == 0:
            print('dataset loading [{}/{}]'.format(i, len(video_names)))

        '''
        video_path = os.path.join(data['datapath'], video_names[i])
        if not os.path.exists(video_path):
            continue

        n_frames_file_path = os.path.join(video_path, 'n_frames')
        '''
        n_frames = data[subset][i]['n_frames']
        if n_frames <= 0:
            continue

        begin_t = 1
        end_t = n_frames
        sample = {
            'segment': [begin_t, end_t],
            'n_frames': n_frames,
            'video_id': video_names[i],
            'img_list': data[subset][i][image_type]
        }
        if len(annotations) != 0:
            sample['label'] = class_to_idx[annotations[i]['label']]
        else:
            sample['label'] = -1

        if n_samples_for_each_video == 1:
            sample['frame_indices'] = list(range(1, n_frames + 1))
            dataset.append(sample)
        else:
            if n_samples_for_each_video > 1:
                step = max(1,
                           math.ceil((n_frames - 1 - sample_duration * sample_step) /
                                     (n_samples_for_each_video - 1)))
            else:
                step = sample_duration
            for j in range(1, n_frames, step):
                sample_j = copy.deepcopy(sample)
                sample_j['frame_indices'] = list(
                    range(j, min(n_frames + 1, j + sample_duration * sample_step), sample_step))
                dataset.append(sample_j)

    return dataset, idx_to_class


class Synthetic(data.Dataset):
    """
    Args:
        root (string): Root directory path.
        spatial_transform (callable, optional): A function/transform that  takes in an PIL image
            and returns a transformed version. E.g, ``transforms.RandomCrop``
        temporal_transform (callable, optional): A function/transform that  takes in a list of frame indices
            and returns a transformed version
        target_transform (callable, optional): A function/transform that takes in the
            target and transforms it.
        loader (callable, optional): A function to load an video given its path and frame indices.
     Attributes:
        classes (list): List of the class names.
        class_to_idx (dict): Dict with items (class_name, class_index).
        imgs (list): List of (image path, class_index) tuples
    """

    def __init__(self,
                 root_path,
                 annotation_path,
                 subset,
                 n_samples_for_each_video=1,
                 spatial_transform=None,
                 temporal_transform=None,
                 target_transform=None,
                 sample_duration=16,
                 channel_fuse_step=-1,
                 get_loader=get_default_video_loader,
                 image_type='rgb',
                 sample_step=10):
        self.data, self.class_names = make_dataset(
            root_path, annotation_path, subset, n_samples_for_each_video,
            sample_duration, sample_step, image_type)

        self.spatial_transform = spatial_transform
        self.temporal_transform = temporal_transform
        self.target_transform = target_transform
        self.loader = get_loader(image_type)
        self.channel_fuse_step=channel_fuse_step
        self.sample_step = sample_step
        self.subset = subset

    def __getitem__(self, index):
        """
        Args:
            index (int): Index
        Returns:
            tuple: (image, target) where target is class_index of the target class.
        """

        frame_indices = self.data[index]['frame_indices']
        if self.temporal_transform is not None:
            step = random.randint(1, 10)
            frame_indices = self.temporal_transform(frame_indices, step=step)
        clip = self.loader(frame_indices, self.data[index]['img_list'], self.channel_fuse_step)
        ret = []
        if self.spatial_transform is not None:
            self.spatial_transform.randomize_parameters()
            clip = [self.spatial_transform(img) for img in clip]
        clip = torch.stack(clip, 0).permute(1, 0, 2, 3)

        target = self.data[index]
        if self.target_transform is not None:
            target = self.target_transform(target)

        return clip, target

    def __len__(self):
        return len(self.data)
