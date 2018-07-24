python caffe_image_classify.py  \
--weight lib/models/se-res50-hik-v0.32-zrh_iter_48000_acc_0.841.caffemodel  \
--deploy lib/models/deploy.prototxt \
--labels lib/labels.lst \
--gpu 0 \
--batch_size 8\
--img_list data/images.lst \
--root . \
#--labels_corres lib/labels_correspond.lst