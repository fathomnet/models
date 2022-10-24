
|Model Name |Model Class |Habitat |Description |
|-|-|-|-|
|<b>[MBARI Monterey Bay Benthic Supercategory](https://zenodo.org/record/5571043#.YbEUQi1h1TY)</b>|<b>RetinaNet</b>|Benthic|This is a RetinaNet model fine-tuned from the [Detectron2](https://ai.facebook.com/tools/detectron2/) object detection platform's ResNet backbone to identify 20 benthic supercategories drawn from MBARI's remotely operated vehicle image data collected in Monterey Bay off the coast of Central California. The data is drawn from FathomNet and consists of 32779 images that contain a total of 80683 localizations. The model was trained on an 85/15 train/validation split at the image level. <b>[DOI: 10.5281/zenodo.5571043](https://doi.org/10.5281/zenodo.5571043)</b>| 
<hr>

![image](confusion_matrix_norm.png)  
  

#### Class Categories Detected:
~~~
- Anemone
- Fish
- Eel
- Gastropod
- Sea star
- Feather star
- Sea cucumber
- Urchin
- Glass sponge
- Sea fan
- Soft coral
- Sea pen
- Stony coral
- Ray
- Crab
- Shrimp
- Squat lobster
- Flatfish
- Sea spider
- Worm
~~~

#### Information passed to TATOR:
~~~
x - left-most
y - right-most
width - width of bbox (x2 - x)
height - height of bbox (y2 - y)
class_category - string of top prediction
confidence - float of confidence scores [0-1]
~~~



##### This repository contains:
~~~
- model_final.pth - Fine-tuned model weights.
- train_images.json - Training image FathomNet UUIDs, bounding boxes, and 
  metadata.
- val_images.json - Validation image FathomNet UUIDs, bounding boxes, and 
  meta data.
- benthic_label_map.json - Dictionary that links the lowest taxonomic rank to 
  super-category.
- Detectron2-Inference-MBARI.ipynb - Jupyter Notebook that runs model 
  inference with these weights.
- Detectron2_Inference_MBARI_multiscale.ipynb - Jupyter Notebook that test 
  running model inference at two resizing scales to better resolve small 
  targets.
- fathomnet_config_v2_1280.yaml - Settings file for Detectron2 interface.
- inference.py - a script version of Detectron2_Inference_MBARI_multiscale.
  ipynb.
- tator.py - script for using inference.py with a Docker container with TATOR.
- Dockerfile - a file for building the docker container for use with TATOR.
~~~