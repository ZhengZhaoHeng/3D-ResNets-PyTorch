# Preprocess Data by articualtion type

import json
import os
import random

# 0: art, no cam, 1: cam, no art, 2: art, no cam
data_path = '/home/zhaohenz/scratch/obj-art-dataset/data'
data = []

for group in os.listdir(data_path):
    with open(os.path.join(data_path, group, 'label.json'), 'r') as fp:
        tmp = json.load(fp)
        for entry in tmp:
            entry['group'] = group
    data += tmp

print (len(data))

num_count = {'training': 1000, 'validation': 120, 'testing': 0}

cats = [[] for i in range(2)]

split = {'training':[], 'validation':[], 'testing':[]}

# 0: Translation, 1: Rotation

for entry in data:
    entry['picked'] = False
    if entry['label'] == 0:
        continue
    if entry['drawer']:
        cats[0].append(entry)
        entry['label'] = 0
    else:
        cats[1].append(entry)
        entry['label'] = 1
    entry['n_frames'] = 120
    entry['rgb'] = [os.path.join(data_path, entry['group'], 'frames', entry['id'], 'color', '{}_{:06d}.png'.format(entry['id'], i)) for i in range(120)]
    entry['depth'] = [os.path.join(data_path, entry['group'], 'frames', entry['id'], 'depth_pred', '{}_{:06d}.t7'.format(entry['id'], i)) for i in range(120)]
    entry['normal'] = [os.path.join(data_path, entry['group'], 'frames', entry['id'], 'normal_pred', '{}_{:06d}.t7'.format(entry['id'], i)) for i in range(120)]

 
random.shuffle(cats[0])
random.shuffle(cats[1])
print (len(cats[0]), len(cats[1]))

split['training'] = cats[0] + cats[1]
print (len(split['training']))

val_cat = [[] for i in range(2)]

path = [('/z/zhaohenz/rbo_dataset/interactions/cabinet', 0), 
('/z/zhaohenz/rbo_dataset/interactions/ikeasmall', 0), 
('/z/zhaohenz/rbo_dataset/interactions/laptop', 1),
('/z/zhaohenz/rbo_dataset/interactions/microwave', 1)]

for p in path:
    videos = os.listdir(p[0])
    for video in videos:
        img_path = os.path.join(p[0], video, 'camera_rgb')
        depth_path = os.path.join(p[0], video,'depth_pred')
        normal_path = os.path.join(p[0], video,'normal_pred')
        entry = {}
        entry['id'] = video
        entry['label'] = p[1]
        entry['n_frames'] = len(os.listdir(img_path))
        entry['rgb'] = [os.path.join(img_path, x) for x in sorted(os.listdir(img_path))]
        entry['depth'] = [os.path.join(depth_path, x) for x in sorted(os.listdir(depth_path))]
        entry['normal'] = [os.path.join(normal_path, x) for x in sorted(os.listdir(normal_path))]
        val_cat[p[1]].append(entry)

random.shuffle(val_cat[1])        
random.shuffle(val_cat[0])

split['validation'] = val_cat[0][:25] + val_cat[1][:25]

test_cat = [[] for i in range(2)]

for p in path:
    videos = os.listdir(p[0])
    for video in videos:
        img_path = os.path.join(p[0], video, 'camera_rgb')
        depth_path = os.path.join(p[0], video,'depth_pred')
        normal_path = os.path.join(p[0], video,'normal_pred')
        rgb_imgs = sorted(os.listdir(img_path))
        depth_imgs = sorted(os.listdir(depth_path))
        normal_imgs = sorted(os.listdir(normal_path))
        n_frames = len(rgb_imgs)
        for sample_rate in range(1, 11):
            end_of_video = False
            cur = 0
            cnt = 0
            while not end_of_video:
                entry = {}
                entry['id'] = video + '_{}_{}'.format(sample_rate, cnt)
                entry['label'] = p[1]
                entry['n_frames'] = 16
                entry['rgb'] = []
                entry['depth'] = []
                entry['normal'] = []
                for idx in range(16):
                    entry['rgb'].append(os.path.join(img_path, rgb_imgs[cur]))
                    entry['depth'].append(os.path.join(depth_path, depth_imgs[cur]))
                    entry['normal'].append(os.path.join(normal_path, normal_imgs[cur]))
                    cur += sample_rate
                    if cur >= n_frames:
                        end_of_video = True
                        entry['n_frames'] = idx + 1
                        break
                test_cat[p[1]].append(entry)
                cnt += 1

#  split['validation'] = val_cat[0][:25] + val_cat[1][:25]
#  split['validation'] = split['training']

split['testing'] = test_cat[0] + test_cat[1]
split['testing'] = split['testing']
print (len(split['validation']))
print (len(split['testing']))
'''

# Preprocess for testing (data fron Dandan)
path = ['/home/zhaohenz/datasets/puzzle_videos']
for p in path:
    videos = os.listdir(p)
    for video in videos:
        img_path = os.path.join(p, video)
        entry = {}
        entry['id'] = video
        entry['label'] = 0 # Unannotated
        entry['n_frames'] = len(os.listdir(img_path))
        entry['rgb'] = [os.path.join(img_path, x) for x in sorted(os.listdir(img_path))]
        split['testing'].append(entry)
'''

split['labels'] = [0, 1]
split['datapath'] = data_path

with open('annotation.json', 'w') as fp:
    json.dump(split, fp)






