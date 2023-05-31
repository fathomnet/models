
### <a id="image_augmentation"></a> Image Augmentation

YOLOv5 applies imagespace and colorspace augmentations by defaults during training.
Details can be found in the YOLOv5 documentation under [Augmentation](https://docs.ultralytics.com/FAQ/augmentation/).

To test different augmentations, use a hyperparameter file (default data/hyp.scratch.yaml).
Modifications were made to a copy of the default hyperparameter file. 

Many combinations can be done with the different augmentations. For our purposes, augmentations were divided in [three categories](../data/images/augmentations.png).


Training with different augmentations were tried:

* no augmentations
* no imagespace augmentations
* no colorspace augmentations
* no Mosaic augmentation

To train using a specific hyperparameter file:

```bash
python train.py --hyp <my_hyp.yaml> --img 640 --batch 16 --epochs 300 --data <data.yaml> --weights yolov5s.pt --cache
```


### <a id="image_resolution"></a> Image Resolution

Training was done at COCO's native resolution of `--img 640`. Due to the amount of small objects in the dataset, training could benefit by using a higher resolution such as `--img 1280`. Best inference results are obtained using the same value for `--img` as the training was run with. If you train with `--img 1280` you should also validate and run inference with `--img 1280`.


```bash
python train.py --img 1280 --batch 16 --epochs 300 --data <data.yaml> --weights yolov5s.pt --cache

python3 val.py --data {data.directory}/{domain}domain.yaml --weights runs/train/exp/weights/best.pt --img 1280 --task test

python detect.py --weights runs/train/exp/weights/best.pt --img 1280 --conf 0.65 --source {dataset.location}/test/images
```


### <a id="background_images"></a> Background Images

Background images are images with no objects that are added to a dataset to reduce False Positives (FP). No labels are required for background images.
To train with background images, these images need to be added to the images/train data.

A [Google Colab notebook](notebooks/athomnet_background_imgs.ipynb) is provided that illustrates a way to find and download background images.


### <a id="class_coarsening"></a> Class Coarsening

Training with a superclass requires the object class in the labels be modified.
For our experiment, we used simple sed scripts to modify the labels, so:

* labels for Chiroteuthis calyx, Dosidicus gigas and Gonatus onyx are set to 0
* labels for Sebastes, Sebastes diploproa, Sebastes melanostomus and Sebastolobus are set to 1.

In addition, the yaml file will have to refer to only two classes:

```bash
# Classes 
nc: 2  # number of clases
names: ['squid', 'fish']
```


### <a id="distractor_class"></a> Training With Distractor Classes

The dataset for training with distractor classes requires downloading the Nanomia bijuga.
This can be accomplished by the bash command:

```bash
fathomnet-generate -c "Nanomia bijuga" --img-download {dataset.location}/distractor/Nanomia/images --format coco -o {dataset.location}/distractor/Nanomia
```

Nanomia bijuga annotations will need to be converted from COCO format to YOLO format in a similar way as for other trainings.

The juvenile Chiroteuthis calyx images were manually selected from the all the Chiroteuthis calyx images downloaded. A list of thes images can be found [here](../data/misc/C_calyx_juvenile_images.txt).

Datasets for distractor training need to be prepared in a similar way as before:

* Split data into train, validadtion and test data

* Create the coresponding yaml files



