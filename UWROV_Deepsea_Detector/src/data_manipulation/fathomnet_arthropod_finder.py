import json
import os
from worms_classifier import ConceptDictionary, OrganismClass

DATA_FILES_PREFIX = "../../data/"
OUTPUT_FOLDER = DATA_FILES_PREFIX + "fathomnet_image_lists/"
FATHOMNET_DATA_FILE = DATA_FILES_PREFIX + "fathomnet_global.json"

FATHOMNET_PREFIX = "fathomnet_"
NON_NOAA_PREFIX = "non_noaa_"
ARTHROPOD_PREFIX = "arthropod_"
IMAGE_LIST_NAME = FATHOMNET_PREFIX + NON_NOAA_PREFIX + ARTHROPOD_PREFIX + "image_list.json"

# file containing saved concept to classification mapping
CONCEPT_DICT_FILENAME = "concept_to_group.json"
UNMATCHED_LOG_FILEPATH = OUTPUT_FOLDER + "non_noaa_arthropod_unmatched_labels.csv"


dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, FATHOMNET_DATA_FILE)

if not os.path.exists(filename):
  raise FileNotFoundError(filename + " does not exist.")
fathomnet_file = open(filename)
fathomnet_data = json.load(fathomnet_file)


concept_dict_filename = os.path.join(dirname, DATA_FILES_PREFIX + CONCEPT_DICT_FILENAME)
if not os.path.exists(concept_dict_filename):
  raise FileNotFoundError(concept_dict_filename + " does not exist.")

filename = os.path.join(dirname, OUTPUT_FOLDER + IMAGE_LIST_NAME)
if os.path.exists(filename):
  raise FileExistsError(filename + " already exists, please rename or delete")
non_noaa_arthropod_images_file = open(filename, 'w', encoding='utf-8')

filename = os.path.join(dirname, UNMATCHED_LOG_FILEPATH)
if os.path.exists(filename):
  raise FileExistsError(filename + " already exists, please rename or delete")
unmatched_log_file = open(filename, 'w')


non_noaa_arthropod_images_list = []
concept_dict = ConceptDictionary.load_from_json(concept_dict_filename)

for count, i in enumerate(fathomnet_data):
  if ("noaa.gov" in i["url"]):
    continue
  if not "boundingBoxes" in i:
    continue

  has_arthropod = False
  for boundingBox in i["boundingBoxes"]:
    category_name = concept_dict.get_class(boundingBox["concept"])
    print(str(count) + ": " + str(category_name))
    if category_name is None:
      unmatched_log_file.write(boundingBox["concept"] + '\n')
    elif category_name == "arthropoda":
      has_arthropod = True
  
  if not has_arthropod:
    continue

  image_info = {
    "id": i["id"],
    "url": i["url"]
  }

  non_noaa_arthropod_images_list.append(image_info)
  
json.dump(non_noaa_arthropod_images_list, non_noaa_arthropod_images_file, ensure_ascii=False, indent=4)
concept_dict.save_to_json(os.path.join(dirname, "new_concept_dict.json"))

print("Image list generated")
