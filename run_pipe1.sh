#!/bin/bash
sudo /opt/anaconda3/envs/py3.6-pyt1.0.1/bin/python pipe1_detectron.py \
	--cfg configs/12_2017_baselines/e2e_mask_rcnn_R-101-FPN_2x.yaml \
	--output-dir ./uploads-pipe1 \
	--image-ext jpg \
	--wts ./models/e2e_mask_rcnn_R-101-FPN_2x.pkl \
	--output-ext png \
	--thresh 0.1