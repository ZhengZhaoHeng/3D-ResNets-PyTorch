python main.py --root_path . --video_path kinetics_videos/jpg --annotation_path annotation.json \
--result_path results/$1 --dataset synthetic --model resnet \
--model_depth 50 --n_classes 400 --n_finetune_classes 2 --batch_size 32 --n_threads 4 --checkpoint 5 \
--resnet_shortcut B --pretrain_path resnet-50-kinetics.pth --ft_begin_index 4 --n_epochs 200 --channel_fuse -1 --gpu 0 \
--n_val_samples 5 --image_type $1
