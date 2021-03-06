import torch
from torch.autograd import Variable
import torch.nn.functional as F
import time
import os
import sys
import json
import pickle
import numpy as np
import cv2

from utils import AverageMeter


def calculate_video_results(output_buffer, video_id, test_results, class_names):
    video_outputs = torch.stack(output_buffer)
    average_scores = torch.mean(video_outputs, dim=0)
    sorted_scores, locs = torch.topk(average_scores, k=1)

    video_results = []
    for i in range(sorted_scores.size(0)):
        video_results.append({
            'label': class_names[locs[i].item()],
            'score': sorted_scores[i].item()
        })

    test_results['results'][video_id] = video_results


def test(data_loader, model, opt, class_names):
    print('test')

    model.eval()

    batch_time = AverageMeter()
    data_time = AverageMeter()

    end_time = time.time()
    output_buffer = []
    previous_video_id = ''
    test_results = {'results': {}}
    out_dump = []
    for i, (inputs, targets) in enumerate(data_loader):
        data_time.update(time.time() - end_time)
        
        input_mean = np.reshape(np.asarray(opt.mean), (1, 1, 1, 3))
        input_frames = inputs.data.numpy().squeeze()
        input_frames = (np.moveaxis(input_frames, 0, -1) + input_mean).astype(np.uint8)
        inputs = Variable(inputs, volatile=True)
        outputs = model(inputs)
        if not opt.no_softmax_in_test:
            outputs = F.softmax(outputs)
        out_dump.append({'data': input_frames, 'scores': outputs.data.cpu().numpy()})
        for j in range(outputs.size(0)):
            output_buffer = []
            output_buffer.append(outputs[j].data.cpu())
            calculate_video_results(output_buffer, targets[j],
                                        test_results, class_names)
        '''
        if (i % 100) == 0:
            with open(
                    os.path.join(opt.result_path, '{}.json'.format(
                        opt.test_subset)), 'w') as f:
                json.dump(test_results, f)
        '''

        batch_time.update(time.time() - end_time)
        end_time = time.time()

        print('[{}/{}]\t'
              'Time {batch_time.val:.3f} ({batch_time.avg:.3f})\t'
              'Data {data_time.val:.3f} ({data_time.avg:.3f})\t'.format(
                  i + 1,
                  len(data_loader),
                  batch_time=batch_time,
                  data_time=data_time))
    with open(
            os.path.join(opt.result_path, '{}.json'.format(
                opt.test_subset)), 'w') as f:
        json.dump(test_results, f)

    '''
    with open(
            os.path.join(opt.result_path, '{}.pkl'.format(opt.test_subset)),
            'wb') as f:
        pickle.dump(out_dump, f)
    '''
