### Description 🤖🎥🐠

Deepsea-Detector is built on MBARI's [Monterey Bay Benthic Object Detector](https://zenodo.org/record/5539915), which can also be found in FathomNet's [Model Zoo](https://github.com/fathomnet/models). The model is trained on data from [NOAA Ocean Exploration](https://oceanexplorer.noaa.gov/) and [FathomNet](http://fathomnet.org/fathomnet/#/), with assistance from [WoRMS](https://www.marinespecies.org/) for organism classification. All the images and associated annotations we used can be found in our [Roboflow project](https://universe.roboflow.com/uwrov-2022-ml-challenge/deepsea-detect--mate-2022-ml-challenge).

Deepsea-Detector was developed for the [2022 MATE Machine Learning Satellite Challenge](https://materovcompetition.org/content/2022-mate-rov-competition-satellite-challenges) by Peyton Lee, Neha Nagvekar, and Cassandra Lam as part of the Underwater Remotely Operated Vehicles Team (UWROV) at the University of Washington.

*Please see the [original repository](https://github.com/ShrimpCryptid/deepsea-detector) for more information.*

### Repository Status:
- Working [`Dockerfile`](Dockerfile) ✅😀
- Working [`inference`](Scripts/inference.py) script and Notebooks ✅😀
- Working [`inference`](Scripts/tator_inference.py) script to use with [TATOR](tator.io) ✅😀
- Working [HuggingSpace demo](https://huggingface.co/spaces/Jordan-Pierce/UWROV_Deepsea_Detector) (see below) ✅😀

  
### HuggingSpace Demo

Click on the image below to be redirected to a `HuggingSpace` that is set 
up to demonstrate the capabilities of this particular model. Feel free to 
include your own test images, or use the examples provided (these were 
selected randomly from [FathomNet](fathomnet.com)🦑).

[![homepage](Figures/HuggingSpace.PNG)](https://huggingface.co/spaces/Jordan-Pierce/UWROV_Deepsea_Detector)


