python caffe_image_classify.py \ 
--weight lib/models/se-res50-hiv-v0.3-t2_iter_24000.caffemodel \
--deploy lib/models/deploy.prototxt \
--labels lib/labels.lst \
--gpu 0 \
--img_list val.txt\
--root val/