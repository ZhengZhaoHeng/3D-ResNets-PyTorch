python main.py --root_path . --video_path kinetics_videos/jpg --annotation_path annotation.json \
--result_path results/$1 --dataset synthetic --model resnet \
--model_depth 50 --n_classes 2 --batch_size 1 --n_threads 4 \
--resnet_shortcut B --channel_fuse -1 --resume_path results/$1/save_2.pth \
--no_train --no_val --test \
--n_val_samples 1 --image_type $1 --test_subset='test' 
