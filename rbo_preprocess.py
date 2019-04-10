# Preprocess Data by articualtion type

import json
import os
import random

with open('label.json', 'r') as fp:
    data = json.load(fp)


print (len(data))
# 0: art, no cam, 1: cam, no art, 2: art, no cam
data_path = '/home/zhaohenz/scratch/valid_03_26/frames'

# training: 400, validation: 100, testing: 100

num_count = {'training': 480, 'validation': 120, 'testing': 0}

cats = [[] for i in range(2)]


split = {'training':[], 'validation':[], 'testing':[]}

for entry in data:
    entry['picked'] = False
    if entry['label'] == 0:
        continue
    if entry['drawer']:
        cats[0].append(entry)
        entry['label'] = 0
        entry['n_frames'] = 120
        entry['img_list'] = [os.path.join(data_path, entry['id'], 'color', '{}_{:06d}.png'.format(entry['id'], i)) for i in range(120)]
    else:
        cats[1].append(entry)
        entry['label'] = 1
        entry['n_frames'] = 120
        entry['img_list'] = [os.path.join(data_path, entry['id'], 'color', '{}_{:06d}.png'.format(entry['id'], i)) for i in range(120)]
 
random.shuffle(cats[0])
random.shuffle(cats[1])

split['training'] = cats[0] + cats[1]

val_cat = [[] for i in range(2)]
path = [('/z/zhaohenz/datasets/rbo_dataset/interactions/cabinet', 0), 
('/z/zhaohenz/datasets/rbo_dataset/interactions/laptop', 1),
('/z/zhaohenz/datasets/rbo_dataset/interactions/microwave', 1)]

for p in path:
    videos = os.listdir(p[0])
    for video in videos:
        img_path = os.path.join(p[0], video, 'camera_rgb')
        entry = {}
        entry['id'] = video
        entry['label'] = p[1]
        entry['n_frames'] = len(os.listdir(img_path))
        entry['img_list'] = [os.path.join(img_path, x) for x in sorted(os.listdir(img_path))]
        val_cat[p[1]].append(entry)

random.shuffle(val_cat[1])        
random.shuffle(val_cat[0])

split['validation'] = val_cat[0][:25] + val_cat[1][:25]
#split['validation'] = split['training']

split['testing'] = split['validation']

split['labels'] = [0, 1]
split['datapath'] = data_path

with open('annotation.json', 'w') as fp:
    json.dump(split, fp)






