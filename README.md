# FathomNet Model Zoo
The FathomNet Model Zoo (FMZ) is a collection of <b>[FathomNet](www.fathomnet.org)</b>-trained machine learning algorithms that can be used by the community.

FathomNet is an open-source image database that can be used to train, test, and validate state-of-the-art artificial intelligence algorithms to help us understand our ocean and its inhabitants. Along with the FathomNet <b>[Data Use Policy](http://fathomnet.org/fathomnet/#/license)</b>, users agree to the following terms:

1. Acknowledgements - Anyone using FathomNet data for a publication or project acknowledges and references this [forthcoming] <b>[publication]()</b>. If you are sharing your work via a presentation or poster, please include a FathomNet </b>[logo](https://github.com/fathomnet/fathomnet-logo)</b> on your materials.
2. Enrichments - The user shares back with the community by creating how-to videos or workflows that are posted on FathomNet’s <b>[Medium](https://medium.com/fathomnet)</b> or <b>[YouTube](https://www.youtube.com/channel/UCTz_lVO8Q_FSjC5yE6sXAGg)</b> channels, posting trained models on the <b>[FathomNet Model Zoo](https://github.com/fathomnet/models)</b>, contributing training data, and/or providing subject-matter expertise to validate submitted data for the purpose of growing the ecosystem.
3. Benevolent Use - The data will only be used in ways that are consistent with the <b>[United Nations Sustainable Development Goals](https://sdgs.un.org/goals)</b>.

The FathomNet terms of use extends to the FathomNet Model Zoo unless otherwise indicated. 

### Object Detection <a name="object_detection"/>
Object detection models identify and locate objects within an image or video.

|Model Name |Model Class |Habitat |Training Details |Description |
|-|-|-|-|-|
|<b>[MBARI Monterey Bay](http://fathomnet.org/static/models/mbari-mb-benthic-33k.pt)</b>|<b>[yolov5](https://github.com/ultralytics/yolov5)</b>|Benthic|<b>[Training Data]()</b><br><br><b>[Confusion Matrix]()</b>|This model was trained on 691 classes using 33,667 localized images from MBARI’s Video Annotation and Reference System (VARS; note: only a subset of the VARS database is uploaded to FathomNet because of institutional concept embargos). For training, images were split 80/20 train/test. Classes were selected because they are commonly observed concepts (primarily benthic organisms along with equipment and marine litte or trash) within the Monterey Bay and Submarine Canyon system from 500 to 4000 m deep. Many of these organisms will be seen throughout the entire NE Pacific within the continental slope, shelf, and abyssal regions. We used the PyTorch framework and the yolov5 ‘YOLOv5x’ pretrained checkpoint to train for 28 epochs with a batch size of 18 and image size of 640 pixels.|
<hr>



