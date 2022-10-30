# Roboflow doesn't have an option to export only annotated images.
# To work around this, we:
#   1) Scrape the names of all annotated images off the browser
#   2) Export the full dataset from roboflow, and fix the resulting annotations
#      (rename the images back to their origial names and combine annotations for
#       testing, training, and validation sets)
#   3) Reupload only the annotated images from step 1 with the fixed annotations from 
#      step 2 into a new, clean roboflow workspace to use to train the model

# This script handles step 2 of the process.


import json
import os
from worms_classifier import OrganismClass

# where data is stored relative to this script
DATA_FILEPATH = "../../data/"

# the folder where the exported roboflow annotations are stored
# relative to the data filepath
# all .coco.json files in this folder with be combined
ANNOTATIONS_FILEPATH = DATA_FILEPATH + "roboflow_annotations_to_combine/"
NEW_ANNOTATION_FILEPATH = ANNOTATIONS_FILEPATH + "combined_annotations.coco.json"

dirname = os.path.dirname(__file__)
annotations_folder = os.path.join(dirname, ANNOTATIONS_FILEPATH)

if not os.path.isdir(annotations_folder):
  raise FileNotFoundError(annotations_folder + " is not a filepath")

filename = os.path.join(dirname, NEW_ANNOTATION_FILEPATH)
if os.path.exists(filename):
  raise FileExistsError(NEW_ANNOTATION_FILEPATH + " already exists, rename or delete")

### ANNOTATION GENERATION

# INFO
info = {
        "year": "2022",
        "contributor": "",
    }


# CATEGORIES
categories_list = OrganismClass.list_values()
new_categories = [
    # for roboflow
    {
        "id": 0,
        "name": "marine-organisms",
        "supercategory": "none"
    }
]

new_category_name_to_id = {}

for i in range(1, (1+len(categories_list))):
    category_name = categories_list[i-1]
    new_cat = {
            "id": i,
            "name": category_name,
            "supercategory": "marine-organisms"
        }
    new_categories.append(new_cat)
    new_category_name_to_id[category_name] = i


new_images = []
new_annotations = []

for filename in os.listdir(annotations_folder):
  filepath = os.path.join(dirname, ANNOTATIONS_FILEPATH + filename)
  if not os.path.isfile(filepath) or not filename.endswith('.coco.json'):
    print("Skipping " + filename)
    continue

  annotation_file = open(filepath)
  coco_annotation = json.load(annotation_file)
  print("Processing " + filename + " ...")

  # the category ids in this annotation file might not necessarily match
  # the category ids in the new combined file, so we need a mapping from 
  # old to new ids
  get_new_category_id = {}
  old_categories = coco_annotation["categories"]
  for old_category in old_categories:
    new_id = new_category_name_to_id[OrganismClass.UNIDENTIFIED.value]
    if old_category["name"] in new_category_name_to_id:
      new_id = new_category_name_to_id[old_category["name"]]
    
    get_new_category_id[old_category["id"]] = new_id 

  # we also need a mapping from old->new id for images
  get_new_image_id = {}
  old_images = coco_annotation["images"]
  for old_image in old_images:
    # append each image to the end of new_images
    # the image id is its index in new_images
    id = len(new_images)

    # remove the extra suffix that roboflow adds to the filename
    # ex: filename_fileextension.rf.roboflowid.fileextension
    #     ==> filename.fileextension
    old_name = old_image["file_name"]
    removed_suffix = old_name.split(".")[0]
    extension_index = removed_suffix.rfind("_")
    fixed_name = removed_suffix[0: extension_index] + "." + removed_suffix[extension_index+1:]

    get_new_image_id[old_image["id"]] = id
    new_image = {
      "id": id,
      "file_name": fixed_name,
      "height": old_image["height"],
      "width": old_image["width"]
    }
    new_images.append(new_image)

  old_annotations = coco_annotation["annotations"]
  for old_annotation in old_annotations:
    id = len(new_annotations)
    new_annotation = {
      "id": id,
      "image_id": get_new_image_id[old_annotation["image_id"]],
      "category_id": get_new_category_id[old_annotation["category_id"]],
      "bbox": old_annotation["bbox"],
      "area": old_annotation["area"],
      "segmentation": old_annotation["segmentation"],
      "iscrowd": old_annotation["iscrowd"]
    }
    new_annotations.append(new_annotation)

  print("Done")

coco_annotation = {
    "info": info,
    "categories": new_categories,
    "images": new_images,
    "annotations": new_annotations
}

# extra parameters for nice formatting
# create file at the end so we don't open it while looping over other files
filename = os.path.join(dirname, NEW_ANNOTATION_FILEPATH)
combined_annotation_file = open(filename, 'w', encoding='utf-8')
json.dump(coco_annotation, combined_annotation_file, ensure_ascii=False, indent=4)
print("Annotation file generated, at " + NEW_ANNOTATION_FILEPATH)






