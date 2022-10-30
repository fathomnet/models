import json
import os

from worms_classifier import ConceptDictionary, OrganismClass

USE_FILTER = True
FILTER_IMAGE_LIST = "fathomnet_non_noaa_arthropod_image_list.json"
FILTER_DESCRIPTION = "non_noaa_arthropod_"

FILTER_PREFIX = FILTER_DESCRIPTION if USE_FILTER else ""

FILTER_LIST_PREFIX = "fathomnet_image_lists/"


DATA_FILES_PREFIX = "../../data/"
ANNOTATION_FILES_PREFIX = "generated_annotations/"

ANNOTATION_FILENAME = "fathomnet_" + FILTER_PREFIX  + "coco_annotations.json"

FATHOMNET_LABELS_FILENAME = "fathomnet_global.json"

# file containing saved concept to classification mapping
CONCEPT_DICT_FILENAME = "concept_to_group.json"

# the file that contains all rows that could not be matched to a concept or were not localized
UNMATCHED_LOG_FILENAME = "fathomnet_" + FILTER_PREFIX + "unmatched_labels.csv"


def get_filename_from_url(url):
    return url.split('/').pop()


# FILE CHECKING AND OPENING
dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, DATA_FILES_PREFIX + FATHOMNET_LABELS_FILENAME)

if not os.path.exists(filename):
  raise FileNotFoundError(filename + " does not exist.")
labels_file = open(filename, newline='')
labels_reader = json.load(labels_file)

concept_dict_filename = os.path.join(dirname, DATA_FILES_PREFIX + CONCEPT_DICT_FILENAME)
if not os.path.exists(concept_dict_filename):
  raise FileNotFoundError(concept_dict_filename + " does not exist.")

filename = os.path.join(dirname, DATA_FILES_PREFIX + ANNOTATION_FILES_PREFIX + UNMATCHED_LOG_FILENAME)
if os.path.exists(filename):
  raise FileExistsError(filename + " already exists, rename or delete file before running.")
unmatched_log_file = open(filename, 'w')


filename = os.path.join(dirname, DATA_FILES_PREFIX + ANNOTATION_FILES_PREFIX + ANNOTATION_FILENAME)
if os.path.exists(filename):
  raise FileExistsError(filename + " already exists, rename or delete file before running.")
generated_annotation_file = open(filename, 'w', encoding='utf-8')

target_image_ids = set()
if (USE_FILTER):
    filename = os.path.join(dirname, DATA_FILES_PREFIX + FILTER_LIST_PREFIX + FILTER_IMAGE_LIST)
    if not os.path.exists(filename):
        raise FileNotFoundError(filename + " does not exist.")
    filter_image_list_file = open(filename, newline='')
    image_list_reader = json.load(filter_image_list_file)

    for i in image_list_reader:
        target_image_ids.add(i["id"])

    



### ANNOTATION GENERATION

# INFO
info = {
        "year": "2022",
        "url": "http://fathomnet.org/fathomnet/#/",
        "contributor": "FathomNet"
    }

# LICENSES
licenses = [
    {
        "url": "https://creativecommons.org/licenses/by-nd/4.0/",
        "id": 1,
        "name": "Attribution-No Derivatives 4.0 International License"

    }
]


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


# IMAGES AND ANNOTATIONS
images = []
annotations = []
concept_dict = ConceptDictionary.load_from_json(concept_dict_filename)

annotation_id = 1
for image in labels_reader:
    if (USE_FILTER):
        if (image["id"] not in target_image_ids):
            continue

    new_image = {
        "id": image["id"],
        "license": 1,
        "file_name": get_filename_from_url(image["url"]),
        "height": image["height"],
        "width": image["width"]
    }
    images.append(new_image)

    if ("boundingBoxes" in image):
        for boundingBox in image["boundingBoxes"]:
            category_name = concept_dict.get_class(boundingBox["concept"])
            if category_name is None:
                unmatched_log_file.write(str(image["id"]) + ", " + str(boundingBox["concept"]) + '\n')
                continue
            category_id = category_name_to_id[OrganismClass.UNIDENTIFIED.value]
            if category_name in category_name_to_id:
                category_id = category_name_to_id[category_name]

            new_annotation = {
                "id": annotation_id,
                "image_id": image["id"],
                "category_id": category_id,
                "bbox": [boundingBox["x"], boundingBox["y"], boundingBox["width"], boundingBox["height"]],
                "area": boundingBox["width"]*boundingBox["height"],
                "segmentation": [],
                "iscrowd": 0

            }
            annotation_id+=1
            annotations.append(new_annotation)
            print("annotations processed: " + str(annotation_id-1))


    
# WRITING
coco_annotation = {
    "info": info,
    "licenses": licenses,
    "categories": categories,
    "images": images,
    "annotations": annotations
}

# extra parameters for nice formatting
json.dump(coco_annotation, generated_annotation_file, ensure_ascii=False, indent=4)
print("Annotation file generated, at " + ANNOTATION_FILENAME)