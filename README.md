# FathomNet Model Zoo
The FathomNet Model Zoo (FMZ) is a collection of <b>[FathomNet](www.fathomnet.org)</b>-trained machine learning algorithms that can be used by the community.

FathomNet is an open-source image database that can be used to train, test, and validate state-of-the-art artificial intelligence algorithms to help us understand our ocean and its inhabitants. Along with the FathomNet <b>[Data Use Policy](http://fathomnet.org/fathomnet/#/license)</b>, users agree to the following terms:

1. Acknowledgements - Anyone using FathomNet data for a publication or project acknowledges and references this [forthcoming] <b>[publication]()</b>. If you are sharing your work via a presentation or poster, please include a FathomNet </b>[logo](https://github.com/fathomnet/fathomnet-logo)</b> on your materials.
2. Enrichments - The user shares back with the community by creating how-to videos or workflows that are posted on FathomNet’s <b>[Medium](https://medium.com/fathomnet)</b> or <b>[YouTube](https://www.youtube.com/channel/UCTz_lVO8Q_FSjC5yE6sXAGg)</b> channels, posting trained models on the <b>[FathomNet Model Zoo](https://github.com/fathomnet/models)</b>, contributing training data, and/or providing subject-matter expertise to validate submitted data for the purpose of growing the ecosystem.
3. Benevolent Use - The data will only be used in ways that are consistent with the <b>[United Nations Sustainable Development Goals](https://sdgs.un.org/goals)</b>.

The FathomNet terms of use extends to the FathomNet Model Zoo unless otherwise indicated. 

### Object Detection <a name="object_detection"/>
Object detection models identify and locate objects within an image or video.

|Model Name |Model Class |Habitat |Description |
|-|-|-|-|
|<b>[MBARI Monterey Bay Benthic](https://doi.org/10.5281/zenodo.5539915)</b>|<b>[yolov5](https://github.com/ultralytics/yolov5)</b>|Benthic|This model was trained on 691 classes using 33,667 localized images from MBARI’s Video Annotation and Reference System (VARS). Note: only a subset of the VARS database is uploaded to FathomNet because of institutional concept embargos. For training, images were split 80/20 train/test. Classes were selected because they are commonly observed concepts (primarily benthic organisms, along with equipment and marine litter or trash) within the Monterey Bay and Submarine Canyon system from 500 to 4000 m deep. Many of these organisms will be seen throughout the entire NE Pacific within the continental slope, shelf, and abyssal regions. We used the PyTorch framework and the yolov5 ‘YOLOv5x’ pretrained checkpoint to train for 28 epochs with a batch size of 18 and image size of 640 pixels. <b>[DOI: 10.5281/zenodo.5539915](https://doi.org/10.5281/zenodo.5539915)</b>|
|<b>[MBARI Monterey Bay Benthic Supercategory](https://zenodo.org/record/5571043#.YbEUQi1h1TY)</b>|<b>RetinaNet</b>|Benthic|This is a RetinaNet model fine-tuned from the [Detectron2](https://ai.facebook.com/tools/detectron2/) object detection platform's ResNet backbone to identify 20 benthic supercategories drawn from MBARI's remotely operated vehicle image data collected in Monterey Bay off the coast of Central California. The data is drawn from FathomNet and consists of 32779 images that contain a total of 80683 localizations. The model was trained on an 85/15 train/validation split at the image level. <b>[DOI: 10.5281/zenodo.5571043](https://doi.org/10.5281/zenodo.5571043)</b>|
|<b>[MBARI Midwater Object Detector](https://zenodo.org/record/5942597)</b>|<b>RetinaNet</b>|Midwater|A fine tuned RetinaNet model with a ResNet-50 backbone trained to identify 16 midwater classes. The 29,327 training images were collected in Monterey Bay by two imaging systems developed at the Monterey Bay Aquarium Research Institute.  The monochrome and 3-channel color images contain a total of 34,071 localizations that were split into 90/10 train/validation sets. The full set of images will be loaded into FathomNet and a list of persistent URLs will be added to a future version of this repository. <b>[DOI: 10.5281/zenodo.5942597](https://zenodo.org/record/5942597)  
<hr>



