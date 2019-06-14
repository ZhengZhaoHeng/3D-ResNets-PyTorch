import json
import sys
import os
import numpy as np
import math


test_set = 'test'

with open(os.path.join('results', sys.argv[1], test_set + '.json')) as fp:
    results = json.load(fp)['results']

if test_set == 'test':
    with open('annotation.json') as fp:
        labels = json.load(fp)['testing']

tp = 0
eval_out = {}

# Evaluate and get clip wise accuracy

for entry in labels:
    video_id = entry['id']
    if results[video_id][0]['label'] == entry['label']:
        tp += 1
        eval_out[video_id] = {'hit': True, 'label': entry['label'], 'pred': results[video_id][0]['label'], 'score': results[video_id][0]['score']}
    else:
        eval_out[video_id] = {'hit': False, 'label': entry['label'], 'pred': results[video_id][0]['label'], 'score': results[video_id][0]['score']}

print ('Accuracy: {:.4f}'.format(tp / len(results)))

art_label_to_class = ['Translation', 'Rotation']

clip_acc = {
    'video_rate': {}, 
    'category_rate': {}, 
    'articulation_rate': {},
    'rate': {'total':[[] for i in range(11)]}
}

video_pred = {}

video_acc = {
    'category_rate': {}, 
    'articulation_rate': {},
    'rate': {'total':[[] for i in range(11)]}
}




for (key, entry) in eval_out.items():
    contents = key.strip().split('_')
    video_id = contents[0]
    category = video_id[:-2]
    art_type = art_label_to_class[entry['label']]
    sample_rate = int(contents[2])

    if not (video_id in clip_acc['video_rate']):
        clip_acc['video_rate'][video_id] = [[] for i in range(11)]
    if not (category in clip_acc['category_rate']):
        clip_acc['category_rate'][category] = [[] for i in range(11)]
    if not (art_type in clip_acc['articulation_rate']):
        clip_acc['articulation_rate'][art_type] = [[] for i in range(11)]

    clip_acc['video_rate'][video_id][sample_rate].append(entry['hit'])
    clip_acc['video_rate'][video_id][0].append(entry['hit'])
    clip_acc['category_rate'][category][sample_rate].append(entry['hit'])
    clip_acc['category_rate'][category][0].append(entry['hit'])
    clip_acc['articulation_rate'][art_type][sample_rate].append(entry['hit'])
    clip_acc['articulation_rate'][art_type][0].append(entry['hit'])
    clip_acc['rate']['total'][sample_rate].append(entry['hit'])
    clip_acc['rate']['total'][0].append(entry['hit'])

    if not (video_id in video_pred):
        video_pred[video_id] = {
            'label': entry['label'], 
            'prob': [[0, 0] for i in range(11)]
            }
    pred = entry['pred']
    video_pred[video_id]['prob'][sample_rate][pred] += math.log(entry['score'])
    video_pred[video_id]['prob'][sample_rate][1 - pred] += math.log(1 - entry['score'])
    video_pred[video_id]['prob'][0][pred] += math.log(entry['score'])
    video_pred[video_id]['prob'][0][1 - pred] += math.log(1 - entry['score'])


for (key, entry) in video_pred.items():
    video_id = key
    category = video_id[:-2]
    art_type = art_label_to_class[entry['label']]

    if not (category in video_acc['category_rate']):
        video_acc['category_rate'][category] = [[] for i in range(11)]
    if not (art_type in video_acc['articulation_rate']):
        video_acc['articulation_rate'][art_type] = [[] for i in range(11)]

    for sample_rate in range(11):
        pred = entry['prob'][0] < entry['prob'][1]
        hit = (pred == entry['label'])
        video_acc['category_rate'][category][sample_rate].append(hit)
        video_acc['articulation_rate'][art_type][sample_rate].append(hit)
        video_acc['rate']['total'][sample_rate].append(hit)

for (key, item) in clip_acc.items():
    with open(os.path.join('eval', sys.argv[1], 'clip_{}.txt'.format(key)), 'w') as fp:
        for (vid, entry) in item.items():
            fp.write(vid + ' ')
            for rate in range(11):  
                entry[rate] = np.asarray(entry[rate]).mean()
                fp.write('{:.4f} '.format(entry[rate]))
            fp.write('\n')

for (key, item) in video_acc.items():
    with open(os.path.join('eval', sys.argv[1], 'video_{}.txt'.format(key)), 'w') as fp:
        for (vid, entry) in item.items():
            fp.write(vid + ' ')
            for rate in range(11):  
                entry[rate] = np.asarray(entry[rate]).mean()
                fp.write('{:.4f} '.format(entry[rate]))
            fp.write('\n')









            



