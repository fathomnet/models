# Deepsea-Detector: A deep-sea organism classifier.

<img src=https://user-images.githubusercontent.com/62577438/172253781-3bffec9b-f94a-4862-bbec-d64fdf1b7c20.png alt="UWROV logo" width="200"/>

**Student Contributors:**
| Name | Role |
| --------------- | -------------------- |
| Neha Nagvekar | Data Management, Annotation |
| Peyton Lee | Model Training, User Interface, Annotation |
| Cassandra Lam | Additional Annotation Help |

## Navigation
  * [Problem Description](#problem-description)
  * [Data](#data)
  * [Model](#model)
  * [UI](#ui)
  * [Results](#results)
  * [Limitations](#limitations)
  * [Resources and Acknowledgements](#resources-and-acknowledgements)
  * [Video Explanation](#video-explanation)

## Problem Description
We built our model to tackle [MATE’s 2022 Ocean Exploration Challenge](https://materovcompetition.org/content/2022-mate-rov-competition-satellite-challenges), which tasked us with identifying marine organisms in seafloor footage collected via remotely operated vehicles (ROVs).

The competition was divided into three levels of varying complexity:
- **Level 1:** Recording the first and last frame an organism appeared in
- **Level 2:** Detecting and localizing organisms in the frame
- **Level 3:** Classifying organisms by phyla (Annelida, Cnidaria, etc.) or supercategory (fish)

## Data
The classes we needed to identify for the competition are summarized in the following table:
| Class | Description |
| --- | --- |
| Annelida | Segmented worms |
| Arthropoda | Crustaceans (shrimp, crabs, copepods, etc.), pycnogonids (sea spiders) |
| Cnidaria | Sea jellies, corals, anemones, siphonophores |
| Echinodermata | Sea stars, brittle stars, basket stars, urchins, sea cucumbers, sea lilies, sand dollars |
| Fish | Cartilaginous, bony, and jawless fishes |
| Mollusca | Cephalopods (squid, octopi, cuttlefish), gastropods (sea snails and slugs), bivalves, aplacophorans (worm-like mollusks)|
| Porifera | Sponges, glass sponges |
| Other Invertebrates | Includes tunicates (sea squirts and larvaceans), ctenophores, many worm phyla|
| Unidentified Biology | |

We were provided with a dataset containing seafloor footage from NOAA to use to train our model. However, this dataset had multiple issues. The dataset was classified by genus/species, rather than phyla, and organisms were often labeled only once per appearance, resulting in almost all images containing many unlabeled organisms. 

To resolve the first issue, we used the [World Register of Marine Species (WoRMS) API](https://www.marinespecies.org/rest/) to look up the classifications of species and relabel their annotations. This was especially complicated for categories that are not phyla (such as fishes).

To tackle the issue of unlabeled organisms, we manually labeled as many images as we could with the assistance of Roboflow. The annotations for the dataset were not written in a standard format, so we wrote a script to reformat the annotations into the COCO json format so they could be imported into Roboflow. Using Roboflow, we manually labeled over 1400 images. Because Roboflow did not have a workflow to export only manually annotated images, we also wrote a script to scrape this data and reupload only the manually annotated images into a curated dataset. All the data we used can be found in our [Roboflow project](https://universe.roboflow.com/uwrov-2022-ml-challenge/Deepsea-detect--mate-2022-ml-challenge).

When we trained with this updated dataset, we found that our classification would label almost every organism as “cnidaria”. Cnidaria, which includes corals,  was the most prevalent classification in our dataset by far, because of how common they are on the seafloor. Many of our images contained 10+ cnidaria labels with only one or two other classes. To mitigate this issue, we also sourced data from [FathomNet](http://fathomnet.org/fathomnet/#/), which contained many more close-ups of organisms that we could use to create a more even spread of classifications. To prepare the FathomNet data for our use case, we wrote scripts to filter for the images that would be most helpful (images that were verified, did not have text labels of species information, and images of specific classifications). 

All the scripts we wrote to prepare our dataset can be found in the [data_manipulation folder](https://github.com/ShrimpCryptid/deepsea-detector/tree/main/src/data_manipulation). 

## Model
### Detection Model
Because of the small size of our dataset, we decided to modify a pretrained model rather than training a model from scratch ourselves. FathomNet provides [several models](https://github.com/fathomnet/models) that are trained on the Monterey Bay Aquarium’s internal datasets. Out of these models, we chose to use the [MBARI Monterey Bay Benthic YOLOv5x model](https://zenodo.org/record/5539915) as our base, due to the popularity of YOLOv5 and the availability of support resources.

During training, we froze the first 24 layers of the model, leaving just 
Our model was trained for 12 epochs using Google Colab, and the [Python Notebook is available online](https://colab.research.google.com/github/ShrimpCryptid/deepsea-detector/blob/main/notebooks/Model%20Training.ipynb). 

### Tracking
We used the open-source Norfair tracking algorithm to track detections across frames.
## UI
Deepsea-Detector can be run from the CLI, but also includes a UI wrapper built using Tkinter. The UI allows users to select an input video to process, define output files, choose a model to use, and adjust how often detection is run. As the inference is running, the UI will display a preview window for the video as it is being processed. The preview window displays tracking, localization, and optionally, classification information. We used built-in functions in Norfair (an external Python module) to display the preview window.

![image](https://user-images.githubusercontent.com/62577438/172256849-ac34d63f-0748-49b3-841f-d4b90708b3d9.png)

Once inference is done, the program outputs a video of the detection it performed and a spreadsheet containing tracking and classification information. A sample of one such spreadsheet is depicted below.

![image](https://user-images.githubusercontent.com/62577438/172254437-68da3760-0021-45cc-8aea-21a309f0cce6.png)


The following is a diagram detailing the architecture of our program.

![image](https://user-images.githubusercontent.com/62577438/172254192-1b459e25-a670-4b4e-b6b0-e780d1199f18.png)


## Results
Overall, our model performed well in localizing organisms, but struggled in classifying and consistently tracking organisms. See below for a full video showing the results of localization and tracking across videos with both low and high densities of organisms.

[![Deepsea-Detector Inference Video](https://i.imgur.com/EiBy7QJ.jpg)](https://youtu.be/qgBh8qigoR8)

![image](https://user-images.githubusercontent.com/62577438/172254379-b320e992-4488-496d-b34d-1b6adce6d78f.png)\
*An example localization.*

![image](https://user-images.githubusercontent.com/62577438/172254468-b085b880-e47a-4347-a7d2-daa347f27922.png)\
*Unfortunately, this is a shrimp (arthropod) and not a fish.*


![image](https://user-images.githubusercontent.com/62577438/172254560-3a2e894d-c73a-4860-8437-adb6898afbbe.png)
*Training loss for our ML model.*

![image](https://user-images.githubusercontent.com/62577438/172254588-10d49df4-ad3b-4749-9cc9-603631312e82.png)
*Images from the validation set. The left image is the actual ground-truth labels, while the right image is the predictions our model made for those same images.*

## Limitations
While organizing creatures by phyla greatly reduced the number of classifications our model needed to generate, the sheer diversity present in each category makes it difficult to recognize classes by single features. One way around this is to increase the number of training examples presented to our model, but as previously discussed our dataset was limited by what we could manually label.

![Illustration](https://user-images.githubusercontent.com/62577438/172256595-c16f9132-dc5c-4a39-a79f-d92a20d18db5.png)
*Example of the morphological diversity within the phyla Echinodermata. Images from Leonard et al. 2020.* 


With more time, we would also curate our dataset so the number of classifications in each class is more balanced. Even with the addition of FathomNet data we described in the Data section, our dataset was still heavily skewed towards cnidaria. 



## Resources and Acknowledgements
We would like to thank [FathomNet](fathomnet.org) and [NOAA Ocean Exploration](https://oceanexplorer.noaa.gov/) for providing our datasets!  We would also like to thank MATE and NOAA Ocean Exploration for hosting this competition. 

Finally, we would like to thank Professor Joseph Redmon for his advice and guidance throughout this project.

Leonard, C., Evans, J., Knittweis, L., Aguilar, R., Alvarez, H., Borg, J. A., Garcia, S., & Schembri, P. J. (2020). Diversity, distribution, and habitat associations of deep-water echinoderms in the Central Mediterranean. Marine Biodiversity, 50(5), 69. [https://doi.org/10.1007/s12526-020-01095-3](https://doi.org/10.1007/s12526-020-01095-3)


## Video Explanation
[![Deepsea-Detector Video Explanation](https://user-images.githubusercontent.com/62577438/172272316-9388e3fe-07e4-4cdf-9f9b-5e397d891c47.png)](https://youtu.be/gSg1rAmHmWs)
[(On YouTube)](https://youtu.be/gSg1rAmHmWs)










