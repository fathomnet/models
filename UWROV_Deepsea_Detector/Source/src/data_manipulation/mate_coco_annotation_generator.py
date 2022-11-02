# reads mate_label_data.csv and converts it into coco annotation

import json
import os
import csv

from worms_classifier import ConceptDictionary, OrganismClass

# where data is stored relative to this script
DATA_FILES_PREFIX = "../../data/"

# the annotation file this script generates
ANNOTATION_FILENAME = "mate_coco_annotations.json"

# input labels to convert to coco annotations, in
# image_name, x, y, width, height, concept\n
# format, where x, y, width, and height are from 0 to 1, 
# and the first line of the csv are the column headers
MATE_LABELS_FILENAME = "mate_label_data.csv"

# file containing saved concept to classification mapping
CONCEPT_DICT_FILENAME = "concept_to_group.json"

# the file that contains all rows that could not be matched to a concept or were not localized
UNMATCHED_LOG_FILENAME = "mate_unmatched_labels.csv"

# dimensions of all Images
IMAGE_HEIGHT = 1080
IMAGE_WIDTH = 1920


# FILE CHECKING AND OPENING
dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, DATA_FILES_PREFIX + MATE_LABELS_FILENAME)

if not os.path.exists(filename):
  raise FileNotFoundError(MATE_LABELS_FILENAME + " does not exist.")
labels_file = open(filename, newline='')
labels_reader = csv.reader(labels_file)

concept_dict_filename = os.path.join(dirname, DATA_FILES_PREFIX + CONCEPT_DICT_FILENAME)
if not os.path.exists(filename):
  raise FileNotFoundError(filename + " does not exist.")

filename = os.path.join(dirname, DATA_FILES_PREFIX + UNMATCHED_LOG_FILENAME)
if os.path.exists(filename):
  raise FileExistsError(filename + " already exists, rename or delete file before running.")
unmatched_log_file = open(filename, 'w')


filename = os.path.join(dirname, DATA_FILES_PREFIX + ANNOTATION_FILENAME)
if os.path.exists(filename):
  raise FileExistsError(filename + " already exists, rename or delete file before running.")
generated_annotation_file = open(filename, 'w', encoding='utf-8')


### ANNOTATION GENERATION

# INFO
info = {
        "year": "2022",
        "contributor": "",
    }


# CATEGORIES
categories_list = OrganismClass.list_values()
categories = [
    # for roboflow
    {
        "id": 0,
        "name": "marine-organisms",
        "supercategory": "none"
    }
]

category_name_to_id = {}

for i in range(1, (1+len(categories_list))):
    category_name = categories_list[i-1]
    new_cat = {
            "id": i,
            "name": category_name,
            "supercategory": "marine-organisms"
        }
    categories.append(new_cat)
    category_name_to_id[category_name] = i


# IMAGES
images_set = set()

for i, row in enumerate(labels_reader):
    # skip header
    if i == 0:
        continue
    images_set.add(row[0])

images_list = list(images_set)

# for the annotations section later
image_name_to_id = {}

images = []

# skip csv header, start at 1
for i in range(len(images_list)):
    new_image = {
        "id": i,
        "file_name": images_list[i],
        "height": IMAGE_HEIGHT,
        "width": IMAGE_WIDTH
    }
    images.append(new_image)
    image_name_to_id[images_list[i]] = i


# ANNOTATIONS
annotations = []

concept_dict = ConceptDictionary.load_from_json(concept_dict_filename)

# go back to the start of the file to generate annotations
labels_file.seek(0)
for i, row in enumerate(labels_reader):
    if (i == 0):
        # again, skip csv header
        continue

    image_name = row[0]
    if image_name not in image_name_to_id:
        # this should never happen, abort
        print(images_list)
        raise ValueError(image_name + " not found in first pass through labels")

    image_id = image_name_to_id[image_name]

    category_name = concept_dict.get_class(row[5])
    if category_name is None:
        unmatched_log_file.write(str(row) + '\n')
        continue

    category_id = category_name_to_id[category_name]

    x = 0
    y = 0
    width = 0
    height = 0

    # not all labels are localized
    try:
        x = float(row[1])
        y = float(row[2])
        width = float(row[3])
        height = float(row[4])
    except:
        unmatched_log_file.write(str(row) + '\n')
        continue



    new_annotation = {
        "id": i,
        "image_id": image_id,
        "category_id": category_id,
        "bbox": [x*IMAGE_WIDTH, y*IMAGE_HEIGHT, width*IMAGE_WIDTH, height*IMAGE_HEIGHT ],
        "area": width*IMAGE_WIDTH * height*IMAGE_HEIGHT,
        "segmentation": [],
        "iscrowd": 0

    }
    annotations.append(new_annotation)
    print("Rows processed: " + str(i))
        
        
    
# WRITING
# licenses for this data are unknown, so not including them
coco_annotation = {
    "info": info,
    "categories": categories,
    "Images": images,
    "annotations": annotations
}

# extra parameters for nice formatting
json.dump(coco_annotation, generated_annotation_file, ensure_ascii=False, indent=4)
print("Annotation file generated, at " + ANNOTATION_FILENAME)