import json
import os

data_path = '/home/zhaohenz/scratch/obj-art-dataset/data'
data = []

for group in os.listdir(data_path):
    with open(os.path.join(data_path, group, 'label.json'), 'r') as fp:
        tmp = json.load(fp)
        with open('img_lists/img_list_{}.txt'.format(group), 'w') as fp:
            for entry in tmp:
                for prefix in ['depth', 'normal']:
                    folder_path = os.path.join(data_path, group, 'frames', entry['id'], prefix+'_pred')
                    if not os.path.exists(folder_path):
                        os.makedirs(folder_path)
                for i in range(120):
                    fp.write(os.path.join(data_path, group, 'frames', entry['id'], 'color', '{}_{:06d}.png'.format(entry['id'], i)))
                    fp.write('\n')



path = [('/z/zhaohenz/rbo_dataset/interactions/cabinet', 0), 
('/z/zhaohenz/rbo_dataset/interactions/ikeasmall', 0),
('/z/zhaohenz/rbo_dataset/interactions/laptop', 1),
('/z/zhaohenz/rbo_dataset/interactions/microwave', 1)]

with open('img_lists/rbo.txt', 'w') as fp:
    for p in path:
        videos = os.listdir(p[0])
        for video in videos:
            img_path = os.path.join(p[0], video, 'camera_rgb')
            for prefix in ['depth', 'normal']:
                output_path = os.path.join(p[0], video, prefix+'_pred')
                if not os.path.exists(output_path):
                    os.makedirs(output_path)
            for x in sorted(os.listdir(img_path)):
                fp.write(os.path.join(img_path, x))
                fp.write('\n')


