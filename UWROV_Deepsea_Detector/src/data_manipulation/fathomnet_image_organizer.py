import json
import os

# extracts images from the fathomnet dataset that are verfied, and splits them based on 
# whether they are from NOAA or not
# We separate NOAA images because they include a header with text identifying a species, which
# would need to be cropped out before using it as training data for our model

DATA_FILES_PREFIX = "../../data/"
OUTPUT_FOLDER_PREFIX = "fathomnet_image_lists/"
FATHOMNET_DATA_FILE = "fathomnet_global.json"

FATHOMNET_PREFIX = "fathomnet_"
FULLY_VERIFIED_PREFIX = "fully_verified_"
PARTIALLY_VERIFIED_PREFIX = "partially_verfied_"
NOAA_PREFIX = "noaa_"
NON_NOAA_PREFIX = "non_noaa_"
IMAGE_LIST_SUFFIX = "image_list.json"


dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, DATA_FILES_PREFIX + FATHOMNET_DATA_FILE)

if not os.path.exists(filename):
  raise FileNotFoundError(filename + " does not exist.")
fathomnet_file = open(filename)
fathomnet_data = json.load(fathomnet_file)

filename = os.path.join(dirname, DATA_FILES_PREFIX + OUTPUT_FOLDER_PREFIX + FATHOMNET_PREFIX + FULLY_VERIFIED_PREFIX + NON_NOAA_PREFIX + IMAGE_LIST_SUFFIX)
if os.path.exists(filename):
  raise FileExistsError(filename + " already exists, please rename or delete")
fully_verified_non_noaa_images_file = open(filename, 'w', encoding='utf-8')

filename = os.path.join(dirname, DATA_FILES_PREFIX + OUTPUT_FOLDER_PREFIX + FATHOMNET_PREFIX + PARTIALLY_VERIFIED_PREFIX + NON_NOAA_PREFIX + IMAGE_LIST_SUFFIX)
if os.path.exists(filename):
  raise FileExistsError(filename + " already exists, please rename or delete")
partially_verified_non_noaa_images_file = open(filename, 'w', encoding='utf-8')

filename = os.path.join(dirname, DATA_FILES_PREFIX + OUTPUT_FOLDER_PREFIX + FATHOMNET_PREFIX + FULLY_VERIFIED_PREFIX + NOAA_PREFIX + IMAGE_LIST_SUFFIX)
if os.path.exists(filename):
  raise FileExistsError(filename + " already exists, please rename or delete")
fully_verified_noaa_images_file = open(filename, 'w', encoding='utf-8')

filename = os.path.join(dirname, DATA_FILES_PREFIX + OUTPUT_FOLDER_PREFIX + FATHOMNET_PREFIX + PARTIALLY_VERIFIED_PREFIX + NOAA_PREFIX + IMAGE_LIST_SUFFIX)
if os.path.exists(filename):
  raise FileExistsError(filename + " already exists, please rename or delete")
partially_verified_noaa_images_file = open(filename, 'w', encoding='utf-8')

fully_verified_non_noaa_images_list = []
partially_verified_non_noaa_images_list = []
fully_verified_noaa_images_list = []
partially_verified_noaa_images_list = []


for i in fathomnet_data:
  if "boundingBoxes" in i:
    bounding_info_arr = i["boundingBoxes"]
    at_least_one_verified = False
    all_verified = True
    for b in bounding_info_arr:
      if b["verified"] == True:
        at_least_one_verified = True
      else:
        all_verified = False

  image_info = {
    "id": i["id"],
    "url": i["url"]
  }
  if (at_least_one_verified and not all_verified):
    if ("noaa.gov" in i["url"]): 
      partially_verified_noaa_images_list.append(image_info)
    else:
      partially_verified_non_noaa_images_list.append(image_info)
  elif (all_verified):
    if ("noaa.gov" in i["url"]): 
      fully_verified_noaa_images_list.append(image_info)
    else:
      fully_verified_non_noaa_images_list.append(image_info)
  
json.dump(fully_verified_non_noaa_images_list, fully_verified_non_noaa_images_file, ensure_ascii=False, indent=4)
json.dump(partially_verified_non_noaa_images_list, partially_verified_non_noaa_images_file, ensure_ascii=False, indent=4)
json.dump(fully_verified_noaa_images_list, fully_verified_noaa_images_file, ensure_ascii=False, indent=4)
json.dump(partially_verified_noaa_images_list, partially_verified_noaa_images_file, ensure_ascii=False, indent=4)

print("Image lists generated")
