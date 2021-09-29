# FathomNet Model Zoo
The FathomNet Model Zoo is a collection of pre-trained, state-of-the-art models shared by the FathomNet community.


### Object Detection <a name="object_detection"/>
Object detection models identify and locate objects within an image or video.

|Model |Model Class |Habitat |Metadata |Description |
|-|-|-|-|-|
|<b>[MBARI Monterey Bay](http://fathomnet.org/static/models/mbari-mb-benthic-33k.pt)</b>|<b>[yolov5](https://github.com/ultralytics/yolov5)</b>|Benthic|<b>[Training Data]()</b><br><b>[Confusion Matrix]{}</b>|This model was trained on 691 classes using 33,667 localized images from MBARI’s Video Annotation and Reference System (VARS; note: only a subset of the VARS database is uploaded to FathomNet because of institutional concept embargos). For training, images were split 80/20 train/test. Classes were selected because they are commonly observed concepts (primarily benthic organisms along with equipment and marine litte or trash) within the Monterey Bay and Submarine Canyon system from 500 to 4000 m deep. Many of these organisms will be seen throughout the entire NE Pacific within the continental slope, shelf, and abyssal regions. We used the PyTorch framework and the yolov5 ‘YOLOv5x’ pretrained checkpoint to train for 28 epochs with a batch size of 18 and image size of 640 pixels.|
<hr>



