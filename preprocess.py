import json
import os

with open('label.json', 'r') as fp:
    data = json.load(fp)


print (len(data))
# 0: art, no cam, 1: cam, no art, 2: art, no cam
data_path = '/scratch/frames'

# training: 400, validation: 100, testing: 100

num_count = {'training': 480, 'validation': 120, 'testing': 0}

cats = [[] for i in range(3)]


split = {'training':[], 'validation':[], 'testing':[]}

for entry in data:
    entry['picked'] = False
    cats[entry['label']].append(entry)

for i in range(3):
    print (len(cats[i]))

for name in ['training', 'validation', 'testing']:
    num_cat = int(num_count[name] / 3)

    for i in range(3):
        num_rot = int(num_cat / 2)
        num_real_box = int(num_rot / 2)
        num_concrete_box = num_rot - num_real_box
        num_drawer = num_cat - num_rot

        print (num_rot, num_real_box, num_concrete_box, num_drawer)
        cnt = 0
        
        for entry in cats[i]:
            if entry['picked']:
                continue
            if entry['drawer']:
                if num_drawer > 0:
                    entry['picked'] = True
                    split[name].append(entry)
                    num_drawer -= 1
                    cnt += 1
            elif num_rot > 0:
                if entry['real_box']:
                    if num_real_box > 0:
                        split[name].append(entry)
                        entry['picked'] = True
                        num_real_box -= 1
                        num_rot -= 1
                        cnt += 1
                elif num_concrete_box > 0:
                    split[name].append(entry)
                    entry['picked'] = True
                    num_concrete_box -= 1
                    num_rot -= 1
                    cnt += 1
            if cnt == num_cat:
                break
        print (num_rot, num_real_box, num_concrete_box, num_drawer)

for name in ['training', 'validation', 'testing']:
    lbl_cnt = [0 for i in range(3)]
    drawer_cnt = [0 for i in range(3)]
    box_cnt = [0 for i in range(3)]

    print (len(split[name]))
    for entry in split[name]:
        lbl = entry['label']
        lbl_cnt[lbl] += 1
        if entry['drawer']:
            drawer_cnt[lbl] += 1
        elif entry['real_box']:
            box_cnt[lbl] += 1

    print (lbl_cnt)
    print (drawer_cnt)
    print (box_cnt)


# split['validation'] = split['testing'] = split['training']
split['labels'] = [0, 1, 2]
split['datapath'] = data_path

with open('annotation.json', 'w') as fp:
    json.dump(split, fp)






