python main.py --root_path . --video_path kinetics_videos/jpg --annotation_path annotation.json \
--result_path results/channel_fusion_02_26 --dataset synthetic --model resnet \
--model_depth 18 --n_classes 400 --n_finetune_classes 3 --batch_size 12 --n_threads 2 --checkpoint 5 \
--resnet_shortcut A --pretrain_path resnet-18-kinetics.pth --ft_begin_index 4 --n_epochs 50 --channel_fuse 5
