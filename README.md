# FathomNet Model Zoo
The FathomNet Model Zoo is a collection of pre-trained, state-of-the-art models shared by the FathomNet community of users.


### Object Detection <a name="object_detection"/>
Object detection models detect the presence of multiple objects in an image and both identify the object class and localize the image where the objects are detected.

|Model |Model Class |Habitat |Description |
|-|-|-|-|
|<b>[MBARI Monterey Bay](http://fathomnet.org/static/models/mbari-mb-benthic-33k.pt)</b>|<b>[yolov5](https://github.com/ultralytics/yolov5)</b>|Benthic|This model was trained on 691 classes using 33,667 localized images from MBARI’s Video Annotation and Reference System. For training, images were split 80/20 train/val. The classes that were selected are commonly observed benthic organisms within the Monterey Bay and Submarine Canyon system from 500 - 4000 meters water depth. Many of these organisms will be seen throughout the entire NE Pacific within the continental slope, shelf, and abyssal regions. Additional classes include equipment and marine litter (trash).  We used the PyTorch framework and the yolov5 ‘YOLOv5x’ pretrained checkpoint to train for 28 epochs with a batch size of 18 and image size of 640. For detections and tracking in video we’ve used yolov5 and [DeepSort](https://github.com/mikel-brostrom/Yolov5_DeepSort_Pytorch) with good success.|
<hr>



